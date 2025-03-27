import socket
import select
import sys
from message import Message, MAX_MESSAGE_LENGTH

def main(): 
    if len(sys.argv) < 2: 
        print("to start run: python server.py [port num]")
        sys.exit(1)
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)
    print("Listening for connections on port", port)
    server_socket.setblocking(False)

    poller = select.poll()
    poller.register(server_socket, select.POLLIN)

    fd_socket_map = {server_socket.fileno(): server_socket}
    fd_name_map = {server_socket.fileno(): "Server"}

    try: 
        while True: 
            print("Polling...")
            # wait till the event starts 
            events = poller.poll()
            print(f"Polled events of {len(events)}")
            for fd, flag in events: 
                cur_socket = fd_socket_map[fd]
                # check the event type 
                # if the event type is a new_connection 
                if cur_socket is server_socket: 
                    client_socket, addr = server_socket.accept()
                    client_socket.setblocking(False)
                    poller.register(client_socket, select.POLLIN)
                    fd_socket_map[client_socket.fileno()] = client_socket
                else: 
                    # if the event type is new message  
                    # get the msg
                    try: 
                        data = cur_socket.recv(MAX_MESSAGE_LENGTH)
                    except Exception as e: 
                        print("Error receiving data:", e)
                        data = b''
                    #check the data 
                    if not data: 
                        print("Close client connection")
                        poller.unregister(fd)
                        cur_socket.close()
                        del fd_socket_map[fd]
                    else: 
                        # get the actual message from the data 
                        try: 
                            msg = Message.unmarshal_message(data)
                        except Exception as e:
                            print("Error unmarshalling message:", e)
                            continue
                        if fd not in fd_name_map: 
                            fd_name_map[fd] = msg.name
                            print("Registered new client name:", msg.name)
                        else: 
                            if fd_name_map[fd] != msg.name: 
                                print(f"Client attempted to change name from '{fd_name_map[fd]}' to '{msg.name}'. Overriding.")
                                msg.name = fd_name_map[fd]
                        print(f"Received from [{msg.name}]: [{msg.message}]")
                        #check if the client wanna leave 
                        if msg.message == "exit": 
                        # create a message indicating the client is leaving
                            leave_msg = Message(msg.name, f"{msg.name} leaves")
                            leave_bytes = leave_msg.marshal_message()
                            
                            # broadcast the leave message to all other clients
                            for _, other_socket in list(fd_socket_map.items()):
                                if other_socket is not server_socket and other_socket is not cur_socket:
                                    try:
                                        other_socket.sendall(leave_bytes)
                                    except Exception as e:
                                        print("Send error:", e)
                                                        
                            try: 
                                cur_socket.sendall(leave_bytes)
                            except Exception as e: 
                                print("Send error:", e)
                            print("Client closed connection")
                            poller.unregister(fd)
                            cur_socket.close()
                            del fd_socket_map[fd]
                            if fd in fd_name_map:
                                del fd_name_map[fd]
                        #broadcast the msg here 
                        else: 
                            for _, other_socket in list(fd_socket_map.items()):
                                if other_socket is not server_socket and other_socket is not client_socket:
                                    try:
                                        other_socket.sendall(data)
                                    except Exception as e:
                                        print("Send error:", e)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        for s in fd_socket_map.values():
            s.close()

if __name__ == '__main__':
    main()