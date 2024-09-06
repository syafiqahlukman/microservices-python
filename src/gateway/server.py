import os, gridfs, pika, json #os to interact with the os, gridfs to store large files in mongodb, pika is python lib to interact with rabbitmq, json to work with json data (used for API responses and requests)
from flask import Flask, request, send_file #flask is the web framework and defines route for the app, request is flask module to handle HTTP request, send_file to send files to the client (the converted mp3 file)
from flask_pymongo import PyMongo #flask_pymongo is a flask extension to interact with mongodb from within the Flask app
from auth import validate #auth is the module to validate the token
from auth_svc import access #auth_svc for handling authentication services
from storage import util #storage is the module to handle file storage
from bson.objectid import ObjectId #bson is a module to work with ObjectId which is unique identifier for documents in MongoDB

server = Flask(__name__) #Initializes a Flask application

mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos") #connects to the mongodb server for storing videos

mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s") #connects to the mongodb server for storing mp3s

fs_videos = gridfs.GridFS(mongo_video.db) #Initializes GridFS for storing large video files.
fs_mp3s = gridfs.GridFS(mongo_mp3.db) #Initializes GridFS for storing large mp3 files.

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq")) #connects to the rabbitmq server
channel = connection.channel() #creates a channel to interact with the rabbitmq server (send and receive messages)


@server.route("/login", methods=["POST"]) #routes for user login
def login():
    token, err = access.login(request) #calls the login function from auth_svc module

    if not err:
        return token
    else:
        return err


@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err

        return "success!", 200
    else:
        return "not authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
