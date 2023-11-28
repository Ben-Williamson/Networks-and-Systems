
1. A common message class between client and server, containing:
   1. Message type
   2. Sender
   3. Payload
2. A common connection class between client and server, this should allow a socket to be read and written to
   1. Read messages
   2. Transmit messages
   3. be non-blocking
3. A clientConnection class to track connections to the server
4. A server class to handle a list of connected clients and route messages accordingly.