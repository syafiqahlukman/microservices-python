FROM python:3.10-slim-bullseye 
#lightweight version of python 3.10, contains all of the necessary dependencies to run python applications

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential default-libmysqlclient-dev \
  && pip install --no-cache-dir --upgrade pip
#installs necessary OS dependencies and upgrades pip in one RUN instruction 
#keeps them all in the same layer, making the Docker image smaller

WORKDIR /app 
#creates a folder /app inside the Docker container and sets it as the current directory.
COPY ./requirements.txt /app 
#copying this separately to make sure the requirements.txt (lists all the Python packages that our app needs to run)are in a separate layer 
#Installing these packages can take a lot of time. Docker can cache layer so can reuse instead of building
#So if application code change, Docker skip reinstall the packages
RUN pip install --no-cache-dir --requirement /app/requirements.txt
#Installs the dependencies listed in requirements.txt
COPY . /app
#Copies the rest of application code from local (cd where docker build) to the /app directory in the container.

EXPOSE 5000

CMD ["python3", "server.py"]
#same as when we're actually running this python3 server.py from the command line.
#The goal is to deploy all services within a Kubernetes cluster.
#Docker images are created and pushed to a repository.
#Kubernetes pulls these Docker images from the repository to create deployments within the cluster.

#each instruction in a Dockerfile results in a single new image layer being created. 
#That means that the next instruction's image layer will be built on top of the previous instruction's image layer. 
#If a file changes, Docker will rebuild the layer that includes this file.
#Docker will also rebuild any layers that come after this changed layer.

#make sure to create the requirements.txt using the command pip freeze > requirements.txt
#the requirements.txt and server.py file need to be in the same directory as the Dockerfile

#then, to build this dockerfile, run the command "docker build ." in the same directory as the Dockerfile:
