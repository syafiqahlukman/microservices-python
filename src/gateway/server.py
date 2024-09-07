import os, gridfs, pika, json #os to interact with the os, gridfs to store large files in mongodb, pika is python lib to interact with rabbitmq, json to work with json data (used for API responses and requests)
from flask import Flask, request, send_file #flask is the web framework and defines route for the app, request is flask module to handle HTTP request, send_file to send files to the client (the converted mp3 file)
from flask_pymongo import PyMongo #flask_pymongo is a flask extension to interact with mongodb from within the Flask app
from auth import validate #auth is the module to validate the token
from auth_svc import access #auth_svc for handling authentication services
from storage import util #storage is the module to handle file storage
from bson.objectid import ObjectId #bson is a module to work with ObjectId which is unique identifier for documents in MongoDB

server = Flask(__name__) #Initializes a Flask application

mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos") #PyMongo library will wrap our Flask server, allowing it to connects to the mongodb server for storing videos.The mongo_video variable can be used to interact with the videos database (querying, inserting, updating, and deleting documents within that database)

mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s") #connects to the mongodb server for storing mp3s

fs_videos = gridfs.GridFS(mongo_video.db) #this sets up GridFS to store large video files in the MOngoDB db. 
fs_mp3s = gridfs.GridFS(mongo_mp3.db) #this sets up GridFS to store large mp3 files in the MOngoDB db. 
#MongoDB has a limit on how big a single file can be (16MB). IF a file is bigger than that, GridFS breaks it into smaller chunks and store chunks separately, when u need the file, GridFS puts it all the pieces back together for you

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq")) #sets up connection to the rabbitmq server
channel = connection.channel() #creates a channel on the connection to interact with the rabbitmq server (send and receive messages)


@server.route("/login", methods=["POST"]) #creating endpoint for login and only accepts POST requests
def login(): #login function takes the username and password from the request and calls the login function from the auth_svc module
    token, err = access.login(request) #calls the login function from access module (in another folder service), to check if the user is authorized to access the gateway
 
    if not err:
        return token
    else:
        return err
#if login details are correct, the access.login function returns a token which is returned to the client. If the login details are incorrect, the access.login function returns an error message which is returned to the client.

@server.route("/upload", methods=["POST"]) #creating endpoint for upload and only accepts POST requests
def upload():
    access, err = validate.token(request) #validates the token from the request. return 2 values, access and err

    if err:
        return err #if err is not None, return the error message so that only requests with valid tokens can access the upload endpoint

    access = json.loads(access) #the website reads the key to see what kind of acess the user has. the 'access' is the JWT (a string) and json.load converts to json, a format that can be read by the website
    if access["admin"]: #the website check if the user is an admin, they can upload videos
        if len(request.files) > 1 or len(request.files) < 1: #the function checks if exactly 1 file is uploaded by evaluating the length of the request.files dictionary
            return "exactly 1 file required", 400 #if the length of the dictionary is not exactly 1, the function returns an error message

        for _, f in request.files.items(): # starts a loop to go through each item in request.files dictionary (when user upload a video to the website, website receives the files and stores in request.files dictionary)
            #the request.files.items() returns a list of tuples where the first element is the key and the second element is the value. The key is the name of the file input field in the form and the value is the file object. We don't need the key, so we use an underscore (_) to ignore it. We just need the f which is the actual file object
            err = util.upload(f, fs_videos, channel, access) #The upload function is called with the file and other necessary parameters, with attempts to upload the file to the specified storage system and publish a message to the message queue.

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"]) #creating endpoint for download and only accepts GET requests
def download():
    access, err = validate.token(request) #validates the token from the request. return 2 values, access and err

    if err:
        return err #if err is not None (not valid), return the error message so that only requests with valid tokens can access the download endpoint

    access = json.loads(access) #the website reads the key to see what kind of acess the user has. the 'access' is the JWT (a string) and json.load converts to json, a format that can be read by the website

    if access["admin"]: #the website check if the user is an admin, they can download videos
        fid_string = request.args.get("fid") #when user click the download link URL with the fid in it, the request.args.get("fid") reads the fid parameter from the URL query string. The fid parameter is the unique identifier of the file that the user wants to download

        if not fid_string:
            return "fid is required", 400

        try: #if provide fid, the website tries to get the file from the database using the fid and sends the file to the user to download
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401 #if the user is not an admin, the website returns a 401 status code to indicate that the user is not authorized to download files


if __name__ == "__main__": #checks if the script is being run directly or imported as a module (being used by other program). 
    server.run(host="0.0.0.0", port=8080) #If the script is being run directly, the web server will start and run on the specified host 0.0.0.0 which means will be accessible from any network interface (wifi, ethernet, loopback, which means any devices on same wifi network or wired network) on the machine and listen for HTTP request

#This means that if your computer's IP address on your Wi-Fi network is 192.168.1.10, you can access the web server by going to http://192.168.1.10:8080 from any device on the same Wi-Fi network.