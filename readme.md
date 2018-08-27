# CAM2 database API python client

## What is this repository for?
This repository stores the source code for the CAM2 camera API's python client.

This is part of Purdue's CAM2 (Continuous Analysis of Many Cameras) project. The project's web site is https://www.cam2project.net/

Please read the terms of use https://www.cam2project.net/terms/

In particular, "You agree not to use the Platform to determine the identity of any specific individuals contained in any video or video stream."

The lead investigator is Dr. Yung-Hsiang Lu, yunglu@purdue.edu. Please send your questions, comments, or suggestions to him.

## Motivation
We have a centralized repository of cameras which can be accessed using the CameraDatabase API. We also have numerous image processing teams in CAM2 (continuous Analysis of Many Cameras). But we have a problem. 
A basic client is to be made which can interact with our server to automate the process of retrieving data from the database. If every team creates a new client it will lead to maintenance issues and the API development team 
will be under a restriction of not be able to change API in a swift manner (as all the users of the api will have to be notified of every change).

To  Overcome this problem the Developers of the API have created this client which allows successful transactions with the API. This allows the API developers to be flexible and are held 
responsible for maintaining this client.

## Documentation
Full documentation and examples can be found at https://purduecam2project.github.io/CameraDatabaseClient.

## Location
The CAM2 client is available for pip install in https://pypi.org/

## Registration
In order to access the API, you must make an account through the CAM2 project website, and register a new application. The website can be found here: https://www.cam2project.net/.

## Usage
Step 1) Please use the following command to install the package: 'pip install CAM2CameraDatabaseAPIClient'.

Step 2) On the Class import the CAM2CameraDatabaseAPIClient's  client and camera classes. 

Step 3) Create an object of client and pass the  clientID  and clientSecret as parameters.

Step 4) Use the routes of the API, for description of all the methods please view the documentation (https://purduecam2project.github.io/CameraDatabaseClient)
