#access.py is a module that contain our login function to handle the login request to the auth service
#a module is a single file that can be imported and used in another file

import os, requests #this requests is different with the one we imported from Flask in the server.py. this request is going to be the module that we use to make HTTP calls to our auth service 


def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
