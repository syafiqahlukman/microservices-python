
#communicates with the auth_svc to validate the token
#focuses on the token validation logic and does not handle the login process
#API gateway used this auth to validate the token that the website receives from the client, to make sure each request is authorized before rerouting the request to the appropriate service

import os, requests


def token(request): #token function takes the request object as an argument. the request object contains all the information about the HTTP request that the website receives
    if not "Authorization" in request.headers: #check if the request has an Authorization header
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"] #extracts the token from the Authorization header

    if not token:
        return None, ("missing credentials", 401)

    response = requests.post( #sends POST request tp the Auth Service's /validate endpoint (src/auth) to check if user's token is valid. #This is how the requests module is used to make HTTP calls to the Auth Service.
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate", #get host from the environment using env variable AUTH_SVC_ADDRESS and acces the validate endpoint
        headers={"Authorization": token},#pass the authorization token to our valid request of auth service. The token is included in the Authorization header of the request.
    )# /validate is the endpoint that the validate function in the Auth Service listens to. Since the Auth Service will be in a different container, the website uses the URL to know exactly where to send the token to check if it is valid.

    if response.status_code == 200:
        return response.text, None #response.text is the body of http response received from the auth_svc
    else:
        return None, (response.text, response.status_code)
