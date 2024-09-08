#access.py is a module that contain our login function to handle the login request to the auth service
#a module is a single file that can be imported and used in another file

#this auth_svc is a microservice that is responsible for handling user authentication such as logging in users and issue JWT tokens
#it is a standalone microservice that handles the core authentication logic
#other services, including the API gateway can communicate with auth_svc to authenticate users and obtain tokens

import os, requests #this requests is different with the one we imported from Flask in the server.py. this request is going to be the module that we use to make HTTP calls to our auth service 


def login(request): #login function takes the request object as an argument. the request object contains all the information about the HTTP request that the website receives
    auth = request.authorization #extracts the username and password from the request object to check if the authorization information is present. means the website checks if user have entered their username and password
    if not auth: #if not, return error
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password) #to prepare credentials in a format that can be used in the HTTP request to another service

    response = requests.post( #makes a POST request to send username and password to the Auth Service's /login endpoint (auth/server.py) to check if the user is authorized and obtain a token. #This is how the requests module is used to make HTTP calls to the Auth Service.
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth #get host from the environment using env variable AUTH_SVC_ADDRESS and acces the login endpoint
    ) #AUTH_SVC_ADDRESS is the environment variable that contains the address of the Auth Service.
    #os.environ.get('AUTH_SVC_ADDRESS') reads environment variable and get the address
    #/login is the endpoint that the login function in the Auth Service listens to. Since the Auth Service will be in a different container, the website uses the URL to know exactly where to send the username and password to check if the user is allowed to log in.

    if response.status_code == 200: #if the response status code is 200, the login was successful and the token is returned to the client
        return response.text, None
    else:
        return None, (response.text, response.status_code)
