'''
For authentication service. Main job is to handle user login and validate user tokens. 
uses Flask (a web framework for Python) and MySQL (a database) to manage user data and JSON Web Tokens (JWT) for authentication.
'''


import jwt, datetime, os #libraries for handlong JWT, date & time operations, and accessing environment variable
from flask import Flask, request #flask web framework & request handling
from flask_mysqldb import MySQL

server = Flask(__name__) #initializes flask application
mysql = MySQL(server) #setup MySQL database connection for the flask app

# config
#where we tell Flask application how to connect to the MySQL database using environment variables
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

#handles user login and returns a JWT token if the credentials are valid
@server.route("/login", methods=["POST"]) #when user comes to the /login page (URL), execute login function
def login(): #function, set of instruction that will be followed when someone comes to the /login page
    auth = request.authorization #retrieves the authorzation credentials from the request and assigns them to the variable auth.
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    cur = mysql.connection.cursor() #cursor - allows to interact with the database, like a pointer that can move through rows of result set
    res = cur.execute( #execute sql
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    ) #query to find the email and password from the user table where the email column matches the provided username
      #(auth.username,) username provided by user during login. will replace %s in SQL query
      #the res variable will contain number of rows that match query criteria (number of users found in the db)

    if res > 0: #means if one or more rows were found that match the query criteria
        user_row = cur.fetchone() 
        #when execute SQL query that retrieves data from db, result can contain multiple rows
        #if call fetchone() multiple times, each call will return the next row in the result set until there are no more rows to retrieve
        #so this line means it retrieves the first (and the only) row from the result set. Since emails are unique so at most one row.
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        # calls the createJWT function with arguments: auth.username, secret key used to sign the token and flag indicate the user is authorized.
    else:
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"]) #verfiy the validity of JWT
def validate():
    encoded_jwt = request.headers["Authorization"] # Retrieves the Authorization header that contain JWT from the API request

    if not encoded_jwt: #if the authorization header missing
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1] #Splits the Authorization header value by spaces and extracts the actual JWT

    try: # Attempts to decode the JWT
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz): #function that creates a JWT using the provided username, secret key, and authorization flag
    return jwt.encode( #jwt.encode encodes data below into JWT
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1), #expiration time of token, 1 day from now
            "iat": datetime.datetime.utcnow(), #issued at(iat); time token was issued
            "admin": authz, #flag indicating whether user is admin. if yes, they has access to all API endpoints
        },   #will create the endpoint for this auth service to validate jwt
        secret,
        algorithm="HS256",
    )

#Python idiom used to ensure that certain code is only executed when the script is run directly

if __name__ == "__main__": #if we run this python program, the name will resolve to main
    server.run(host="0.0.0.0", port=5000) #whenever we run our program, we want our server to start
    #allow this program to liste on any IP on our host


'''

1.User enters their credentials and clicks "Sign In."
2.Browser sends a POST request to the server.
3.Server verifies the credentials and generates a JWT.
4.Server sends the JWT back to the browser.
5.Browser stores the JWT in local storage or a cookie.
6.The user tries to access a protected resource (e.g., perform any operation, viewing a profile, accessing a video).
7.Browser includes the JWT in the Authorization header of the request.
8.The server extracts the JWT from the header and verifies it.
9.If the JWT is valid and the user is authorized, the server processes the request and returns the appropriate response.
10.If server checks the JWT and finds that it has expired, server responds with an error, indicating that user need to log in again.

'''

