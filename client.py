import socket
# CLIENT
MAX_BUFFER_SIZE = 16
PORT = 8765

class MySocket:
    '''
    a client socket
    '''

    def __init__(self, sock=None):
        '''creates a client socket'''
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.msg2_start = '' # beginning of msg2; transmitted with end of msg1

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
        # add delimiter
        self.sock.send("\0")

    
    def myreceive_one(self):
        '''read one msg, chunk by chunk'''
        msg = self.msg2_start
        self.msg2_start = '' # reset instance variable
        while True:
            chunk = self.sock.recv(MAX_BUFFER_SIZE)
            print ("client received ", chunk, len(chunk))
            # check for msg delimiter
            index = chunk.find("\0")
            if index  >= 0:
                # delimiter found
                msg1_end, msg2_start = chunk.split('\0')
                self.msg2_start = msg2_start
                msg = msg + msg1_end
                return msg
            else:
                # delimiter not found
                msg = msg + chunk

            
    def myreceive_all(self):
        msgs=[]
        first_msg = self.myreceive_one()
        print ("first msg:", first_msg) # number of msgs to follow; sent by server
        num_msgs = int(first_msg)
        for i in range(num_msgs):
            msgs.append(self.myreceive_one())
            print ("msg", msgs[i])
        self.sock.close()
        text = ''.join(msgs)
        print len(text)
        return text

s = MySocket()
s.connect('', PORT)
s.mysend('Here I am. Sending a longer message.')
print (s.myreceive_all())

