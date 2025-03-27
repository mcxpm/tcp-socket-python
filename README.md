This is a simple socket-based chat application implemented in Python using TCP sockets. It allows multiple clients to connect to a server and chat with each other.

- The server listens for incoming connections and manages client messages
- Each client runs two separate threads:
  - One thread for sending messages
  - One thread for receiving messages

In the works:
- Upgrade the TCP socket communication to a WebSocket protocol -> requires encryption as part of the WebSocket handshake
- Encode and decode websocket frames instead of using fixed-length messages

## To run 
Note that it currently only works on Linux machines (using select.poll instead of select.select -> change that line for windows and it should work)
```bash
git clone <repository-url>
cd <repository-folder>
python server.py 5000
python client.py localhost 5000 Alice
python client.py localhost 5000 Bob
