## Key Concepts

**Microservices Architecture:**
 - A design approach where an application is composed of small, independent services that communicate over a network.
 - Microservices: Small, independent services running in a Kubernetes cluster.

**server.py**
Code for the authentication microservice. 
This microservice has two main endpoints, login and validate
/login endpoint handles user login by verifying credentials.
/validate endpoint validates the JWT included in subsequent requests.


**Python:**
 - The primary programming language used to develop the microservices.

**Kubernetes:**
 - Manages the deployment and scaling of your microservices.

**RabbitMQ:**
 - Facilitates communication between microservices.
 
**MongoDB:**
- Database. Stores data in a flexible, JSON-like format.

**MySQL:**
- Stores structured data with relationships between tables.

## Overall Architecture

**API Gateway**
- The entry point to the application, receiving requests from the client and communicating with internal        services to fulfill those requests (routing requests to appropriate microservices)
- Defines the functionality of the application, e.g endpoints for login and validating user, uploading files.
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


## Use case scenario

As an end user, when you log in to an application, you provide your username and password. 
When you login to the application, your browser sends a POST request to /login with your credentials.

The API gateway receives the request and routes it to the authentication microservice.
The authentication microservice connects to the MySQL database, checks the credentials against the database.

If credentials are valid, the microservice generates a JWT, then returns the JWT to the API gateway, and then to the client's browser

After logging in, the application gives you a token (JWT) behind the scenes. You don’t see this token, but it’s stored in your browser.

Your browser includes the JWT in subsequent requests to the server. So that when you navigate the application (e.g., uploading a file, viewing your profile), the server uses this token to verify your identity and permissions.

The server checks the token to see what you are allowed to do. For example, if you have admin privileges, you might see additional options or features.
