import socket
import sys 
import threading
from message import Message, MAX_MESSAGE_LENGTH

stop_signal = False 

def recv_msg(socket):
    global stop_signal
    while not stop_signal:
        try:
            data = socket.recv(MAX_MESSAGE_LENGTH)
        except Exception as e:
            print("Receive error:", e)
            break
        if not data:
            print("Server closed connection")
            break
        try:
            msg = Message.unmarshal_message(data)
            print(f"[FROM {msg.name}]: {msg.message}")
        except Exception as e:
            print("Error unmarshalling message:", e)
    print("Receiver thread stopping...")

def main(): 
    global stop_signal    

    if len(sys.argv) < 4:
        print("usage: python client.py [hostname] [port] [name]")
        sys.exit(1)
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    try: 
        client = socket.create_connection((hostname, port))
    except Exception as e:
        print("Error connecting:", e)
        sys.exit(1)
    print("Connected to", hostname)

    #start the recv_thread 
    t = threading.Thread(target=recv_msg, args=(client,))
    t.start()

    try:
        while True:
            msg_text = input("Enter: ")
            if msg_text == "":
                continue
            print("You entered:", msg_text)
            if msg_text.startswith("exit") or msg_text.startswith("quit"):
                stop_signal = True
            msg = Message(name, msg_text)
            try:
                client.sendall(msg.marshal_message())
            except Exception as e:
                print("Error sending:", e)
                break
            if stop_signal:
                break
    except KeyboardInterrupt:
        stop_signal = True

    t.join()
    client.close()

if __name__ == '__main__':
    main()