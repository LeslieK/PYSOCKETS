import socket
# CLIENT
MAX_BUFFER_SIZE = 16

class mysocket:
    '''demonstration class only
    - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None):
        self.msg2_start = ''
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            print ("client sent ",  sent)
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        self.sock.send("\0")

    
    def myreceive_one(self):
        msg = self.msg2_start
        while True:
            chunk = self.sock.recv(MAX_BUFFER_SIZE)
            print ("client received ", chunk, len(chunk))
            index = chunk.find("\0")
            if index  >= 0:
                msg1_end, msg2_start = chunk.split('\0')
                self.msg2_start = msg2_start
                msg = msg + msg1_end
                return msg
            else:
                msg = msg + chunk

            
    def myreceive_all(self):
        msgs=[]
        first_msg = self.myreceive_one()
        print ("first msg:", first_msg)
        num_msgs = int(first_msg)
        for i in range(num_msgs):
            msgs.append(self.myreceive_one())
            print ("msgs", msgs)
        self.sock.close()
        return msgs

s = mysocket()
s.connect('', 8765)
s.mysend('Here I am. Sending a longer message.')
print (s.myreceive_all())

