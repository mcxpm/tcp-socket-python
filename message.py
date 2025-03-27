import struct

MAX_NAME_LENGTH = 32  
MAX_MESSAGE_LENGTH = 1024
class Message:
    global MAX_MESSAGE_LENGTH
    global MAX_NAME_LENGTH
    
    def __init__(self, name="", message=""):
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(f"Name must not exceed {MAX_NAME_LENGTH} characters.")
        
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message must not exceed {MAX_MESSAGE_LENGTH} characters.")
        
        self.name = name
        self.message = message
    
    def marshal_message(self):
        name_bytes = self.name.encode('utf-8')
        msg_bytes = self.message.encode('utf-8')
        name_length = len(name_bytes)
        msg_length = len(msg_bytes)
        
        data = struct.pack('B', name_length)  
        data += name_bytes
        data += struct.pack('H', msg_length)  
        data += msg_bytes
        return data

    @classmethod
    def unmarshal_message(cls, buffer):
        # print(buffer) #debug
        name_length = struct.unpack('B', buffer[0:1])[0] #unpack alw returns a tuple value here 
        name = buffer[1:1+name_length].decode('utf-8')
        msg_length = struct.unpack('H', buffer[1+name_length:3+name_length])[0]
        message = buffer[3+name_length:3+name_length+msg_length].decode('utf-8')
        
        return cls(name, message)

if __name__ == "__main__": 
    def test_case(name, message):
        try:
            m = Message(name, message)
            marshalled = m.marshal_message()
            m2 = Message.unmarshal_message(marshalled)
            print(f"[PASS] Name: {repr(name)}, Message: {repr(message)}")
            assert m.name == m2.name
            assert m.message == m2.message
        except Exception as e:
            print(f"[FAIL] Name: {repr(name)}, Message: {repr(message)}")
            print(f"       Error: {e}")


    test_case("Markus", "Hello")
    # test_case("", "Hello world")
    # test_case("Markus", "")
    # test_case("マーカス", "こんにちは世界")
    # test_case("a" * 32, "Test")
    # test_case("Alice", "b" * 1024)
    # test_case("a" * 33, "Overflow name")     # should raise or be handled
    # test_case("Bob", "x" * 1025)             # should raise or be handled
