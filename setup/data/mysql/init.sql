-- Create the first additional user and grant privileges
CREATE USER 'user1'@'%' IDENTIFIED BY 'password1';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'user1'@'%';

-- Create the second additional user and grant privileges
CREATE USER 'user2'@'%' IDENTIFIED BY 'password2';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'user2'@'%';

-- Create the second database
CREATE DATABASE mysecondatabase;

-- Create a user for the second database and grant privileges
CREATE USER 'user3'@'%' IDENTIFIED BY 'password3';
GRANT ALL PRIVILEGES ON mysecondatabase.* TO 'user3'@'%';
