## Key Concepts

**Microservices Architecture:**
 - A design approach where an application is composed of small, independent services that communicate over a network.
 - Microservices: Small, independent services running in a Kubernetes cluster.

    **synchronous inter-service communication**
    - When one service (Gateway) sends a request to another service (Auth), the Gateway service waits until Auth service responds with either a success (JWT) or an error before doing anything else.
    - This waiting makes the Gateway service "blocked" until it gets a response.
    - Because the Gateway service has to wait for the Auth service, they are closely connected or tightly coupled

    **asynchronous inter-service communication**
    - when the Gateway service sends a request, it doesn't wait for a response. It can continue doing other things.
    - This is called a "non-blocking" request.
    - When Gateway service sends a message to RabbitMQ to notify the Converter servie that there's a video to process, the Gateway doesnt just wait for the Converter service to finish, it just moves on to handle other requests.
    - Because the Gateway doesn't wait for the Converter service, they are not closely connected or loosely coupled.

    In our system design:
        - uploading and converting video services use asynchronous communication to allow the system to handle multiple video uploads and conversions simultaneously without blocking the Gateway service.
        - authentication service uses synchronous communication to ensure that the Gateway service waits for the Auth service to authenticate the user before allowing them to perform any actions

    **strong consistency**
    - used in authentication service when gateway service waits for authentication service to verify user before allowing any further action
    - this ensures that the user's authentication is consistent and up to date
    - not being used in uploading service because user would have to wait until the conversion is complete before can do anything else
    - this make our system slow because user have to wait for each video to be processed before can upload another one

    **eventual consistency**
    - data might not be immediately up-to-date but it will eventually become consistent
    - when a user uploads a video, Gateway service store the video in MOngoDB and send message to RabbitMQ to notify converter service. Gateway dont wait for the video to be converted before responding to user. So user can upload another video immediately
    - the conversion happens in the background, and the MP3 file becomes available after some time

**server.py**
Code for the authentication microservice. 
This microservice has two main endpoints, login and validate
/login endpoint handles user login by verifying credentials.
/validate endpoint validates the JWT included in subsequent requests.

## Use case scenario

As an end user, when you log in to an application, you provide your username and password. 
When you login to the application, your browser sends a POST request to /login with your credentials.

The API gateway receives the request and routes it to the authentication microservice.
The authentication microservice connects to the MySQL database, checks the credentials against the database.

If credentials are valid, the microservice generates a JWT, then returns the JWT to the API gateway, and then to the client's browser

After logging in, the application gives you a token (JWT) behind the scenes. You don’t see this token, but it’s stored in your browser.

Your browser includes the JWT in subsequent requests to the server. So that when you navigate the application (e.g., uploading a file, viewing your profile), the server uses this token to verify your identity and permissions.

The server checks the token to see what you are allowed to do. For example, if you have admin privileges, you might see additional options or features.


**Python:**
 - The primary programming language used to develop the microservices.

**Kubernetes:**
- Automates the deployment, scaling, and management of containerized applications.
- It eliminates manual processes involved in deploying and scaling applications.
- It ensures the desired number of pods are running. If a pod crashes, Kubernetes automatically replaces it.
- Scaling up or down is simplified, it handles the deployment and load balancing.

**Kubernetes Objects:**
- Kubernetes uses objects to represent the state of a cluster. These objects are defined in YAML files
- For each microservice, typically we will have the following kubernetes objects: 
    - Deployment:
        - Manages the deployment of the microservice.
        - Ensures the specified number of copies (replicas) of the microservice are running.
        - Handles updates and scaling (making more or fewer copies)

    - ConfigMap:
        - Stores configuration data as key-value pairs (like a dictionary).
        - Injects configuration data into the microservice without changing the app code.

    - Secret:
        - Stores sensitive data such as passwords and tokens.
        - Injects sensitive data into the microservice securely.

    - Service:
        - Exposes a set of pods as a network service.
        - Provides load balancing and service discovery (helps find and distribute traffic to the microservice).


**RabbitMQ:**
 - Facilitates communication between microservices.
 - Helps coordinate the tasks of storing the video, converting it to MP3, notifying the user, and finally delivering the MP3 to the user. This ensures that everything happens in the right order and nothing gets missed.

    **Producer and Exchange**:
    
    -   **Producer**: The service that sends messages to RabbitMQ.
    -   **Exchange**: A middleman that receives messages from the producer and routes them to the appropriate queue.

    **Queues**:
    
    -   RabbitMQ can have multiple queues within a single instance.
    -   For example, you might have a "video" queue and an "MP3" queue.

    **Default Exchange**:
    
    -   The default exchange is a direct exchange with no name (empty string).
    -   Every queue created is automatically bound to the default exchange with a routing key that matches the queue name.

### Message Routing

1.  **Routing Key**:
    
    -   The routing key is set to the name of the queue you want the message to go to.
    -   For example, setting the routing key to "video" will route the message to the "video" queue.
2.  **Message Publishing**:
    
    -   The producer publishes a message to the exchange.
    -   The exchange routes the message to the correct queue based on the routing key.

### Example Scenario

1.  **Video Upload**:
    -   When a user uploads a video, the gateway service stores the video and publishes a message to the exchange.
    -   The exchange routes the message to the "video" queue.
    -   The consumer (e.g., a video-to-MP3 converter service) processes the message by pulling the video from MongoDB, converting it to MP3, and storing the MP3 in MongoDB.

### Handling Multiple Consumers

1.  **Competing Consumers Pattern**:
    -   This pattern allows multiple consumers to process messages from the same queue concurrently.
    -   RabbitMQ uses a round-robin algorithm to distribute messages evenly among consumers.

### Message Persistence

1.  **Durable Queues and Messages**:
    -   **Durable Queue**: The queue remains even after a RabbitMQ restart.
    -   **Persistent Messages**: Messages remain in the queue even after a RabbitMQ restart.
    -   To ensure messages are persisted, set the  `delivery_mode`  to  `pika.spec.PERSISTENT_DELIVERY_MODE`.

### Error Handling

1.  **Deleting Files on Failure**:
    -   If a message cannot be added to the queue, the file is deleted from MongoDB.
    -   This prevents stale files from accumulating in the database.
    -   The function returns an "internal server error" if the message cannot be added to the queue.


    **How RabbitMQ Fits into the System***
    1. A user uploads a video to be converted to MP3. The request first goes to the Gateway
    2. The Gateway stores the video in MongoDB 
    3. Then, the Gateway sends a message to RabbitMQ notifying that there's a new video to be processed to let other parts of the system know that there's a new task to do.
    4. The Video to MP3 Converter service gets the message from RabbitMQ. The service takes the video ID from the message, pulls the video from MongoDB, converts it to MP3, and stores the MP3 back in MongoDB.
    5. After converting the video, the Converter service sends a new message to RabbitMQ notifying that the MP3 conversion is done to let the Notification service know that the conversion is complete.
    6. Then, the Notification service gets the message from RabbitMQ and sends an email to the user saying, "Your MP3 is ready for download!"
    7. The user gets a unique ID from the notification email and uses it, along with their JWT (a kind of digital key), to request the MP3 from the Gateway. The Gateway pulls the MP3 from MongoDB and sends it to the user.
 
**MongoDB:**
- Database. Stores data in a flexible, JSON-like format.

**MySQL:**
- Stores structured data with relationships between tables.

## Overall Architecture

**API Gateway**
- The entry point to the application, receiving requests from the client and communicating with internal services to fulfill those requests (routing requests to appropriate microservices)
- Handles routing, authentication, and validation before passing requests to other microservices
- It receives requests from clients outside the Kubernetes cluster.

**Authentication Microservice**
- Handles user login and token validation using Flask, MySQL, and JWT
- The server.py file is part of the authentication microservice.
- This microservice handles user login and token validation.
- It connects to a MySQL database to manage user data.
- It uses JWT for secure authentication.

**Kubernetes Cluster**

The microservices, including the authentication service, run inside the Kubernetes cluster.
By default, Kubernetes clusters are designed to be secure and isolated from external access to protect internal services.
The API gateway routes requests to the appropriate microservices within the cluster and manage external access is typically managed through specific end points for example /login /validate /upload 


**manifest directory**
- Contains all the Kubernetes configuration files needed for the deployment of auth service
- These configuration files in the this directory are used to pull the Docker image from the repository and deploy it to the Kubernetes cluster.
- These files include:
    - auth-deploy.yaml: Defines the deployment for the auth service, specifying the number of replicas, the Docker image to use, and environment variables.
    - configmap.yaml: Defines a ConfigMap for non-sensitive environment variables, such as database host, user, and port.
    - secret.yaml: Defines a Secret for sensitive data like passwords and JWT secrets.
    - service.yaml: Defines a Service to expose the auth deployment within the Kubernetes cluster, specifying the ports and type of service

**Deployment Process**
- The auth service is implemented in server.py that contains the logic for handling authentication.
- A Dockerfile is created to build the server.py script into a Docker image, the image is then pushed to a Docker repository.
- When the Kubernetes configuration files are applied using kubectl apply -f ./ (make sure minikube is started), they interface with the Kubernetes API and manage the resources defined in the configuration files.
- The Docker image containing the auth service code is pullk9sed from the repository and deployed to the cluster.
- The Kubernetes API creates the necessary resources (e.g., pods, services) based on the configuration files.
- The Kubernetes API manages the resources in the cluster, such as deployments, services, ConfigMaps, and Secrets.




