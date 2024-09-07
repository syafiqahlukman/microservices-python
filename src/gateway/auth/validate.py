
#communicates with the auth_svc to validate the token
#focuses on the token validation logic and does not handle the login process
#API gateway used this auth to validate the token that the website receives from the client, to make sure each request is authorized before rerouting the request to the appropriate service

import os, requests


def token(request): #token function takes the request object as an argument. the request object contains all the information about the HTTP request that the website receives
    if not "Authorization" in request.headers: #check ig the request has an Authorization header
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"] #extracts the token from the Authorization header

    if not token:
        return None, ("missing credentials", 401)

    response = requests.post( #send a post request to the auth service to validate the token
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
