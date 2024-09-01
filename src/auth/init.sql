/*
setup database environment
this file does not require configuration as it is a script executed directly on the database.
*/

-- create new db user account in MySQL 
-- allows the db user to access the auth db
-- used by application to connect to the db
CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'Auth123';

-- creates a new db named auth
CREATE DATABASE auth;

-- grants the db user (auth_user) all privileges on the auth db. auth.* refers to all tables in the db
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

-- use auth db for subsequent commands
USE auth;

-- creates a table named user, with columns id, email, and password
CREATE TABLE user (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
  -- ^ name of column, data type, cannot be null, value of id increase by 1 for new row, primary key of the table
  email VARCHAR(255) NOT NULL UNIQUE,
  -- ^ name of column, max length, cannot be null, must be uniqe
  password VARCHAR(255) NOT NULL
  -- ^ name of column, max length, cannot be null
);

-- add a new entry (user) to the user table
INSERT INTO user (email, password) VALUES ('ssyafiqahlukman@gmail.com', 'Admin123');

  




