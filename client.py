import socket
# CLIENT
MAX_BUFFER_SIZE = 16

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
        self.msgs_rest = '' # msgs after first delimiter

    def connect(self, host, port):
        print ("Client about to connect")
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
        #msgs_rest = self.msgs_rest
        #self.msgs_rest = '' # reset instance variable

        msg, sep, msgs_rest = self.msgs_rest.partition("\0")
        if sep != '':
            self.msgs_rest = msgs_rest
            return msg

        while True:
            chunk = self.sock.recv(MAX_BUFFER_SIZE)
            #print ("client received ", chunk, len(chunk))
            # check for msg delimiter
            next_msg, sep, msgs_rest = chunk.partition("\0")
            if sep  != '':
                # delimiter found
                msg = msg + next_msg
                self.msgs_rest = msgs_rest
                return msg
            else:
                # delimiter not found
                msg = msg + next_msg

            
    def myreceive_all(self):
        msgs=[]
        first_msg = self.myreceive_one()
        print ("first msg:", first_msg) # number of msgs to follow; sent by server
        num_msgs = int(first_msg)
        for i in range(num_msgs):
            msgs.append(self.myreceive_one())
            #print ("msg", msgs[i])
        self.sock.close()
        return msgs



