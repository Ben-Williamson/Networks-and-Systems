
+------------------------------+
| Instant Messenger User guide |
+------------------------------+


Starting the program
====================

Server
------
The server can be started with:

python server.py [port]

The port must be a valid port number and should not be reserved for any other application.

Client
------
The client can be started with:

python client.py [username] [hostname] [port]

- The username can be any string provided it does not contain a space.
- The hostname should be a the hostname of the machine on which the server is running.
- The port should be the port the server is running on.

Functionality
=============

General Useage
--------------
In general the messenger works according to the following principles:
- User input to the program is treated as a message and is transmitted when a newline character is entered.
- Inputs beginging with \ are treated as commands and provide special functionality.

On start up the client will be in "broadcast" mode, this means that messages entered will be shared to every client connected to the server.

The details of available commands are listed below.

\clients
--------
The \clients command outputs a table containing all the clients currently connected to the server. 
Clients are numbered to allow each client to specified in unicast messages.

\unicast [client number]
------------------------
Sets the client to unicast mode; the client will transmit messages that can only be seen by the client specified by the ```[client number]``` argument.  This number should be determined by finding the required user in the table provided by ### ```\clients```.

\broadcast
----------
Returns the client to broadcast mode; messages sent will be recieved by every connected client.

\files
------
Outputs a table containing all the files in the server's /downloads folder.

\download [file number]
-----------------------
Downloads the specified file from the server over the network, storing it in a directory of the current username.