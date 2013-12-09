import socket
# SERVER 

MAX_BUFFER_SIZE = 1024
BACKLOG = 5

class MySocket:
    '''
    a server socket
    '''

    def __init__(self, sock=None):
        self.msgs_rest = ''
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of local addresses (why is this not the default?)
        else:
            self.sock = sock

    def serv(self, port, handler, msgs=None):
        self.sock.bind(('', port))
        self.sock.listen(BACKLOG) # max number of connections waiting to be served
        print "Server about to accept"
        while(True):
            try:
                client_sock, client_addr = self.sock.accept()
                print "connection attempt", client_addr
                handler(client_addr, client_sock, msgs)
            except socket.error as e:
                if e.errno == 10054:
                    print e
                continue

    def msgs_handler(self, client_addr, client_sock, msgs):
        '''sends msgs to Client'''
            # msg = client_sock.recv(MAX_BUFFER_SIZE)
            # print ("received ",  len(msg))
            # if not msg:
            #     break
        # send msg with number of msgs to expect after this one
        client_sock.sendall(str(len(msgs))+"\0")
        for msg in msgs:
            client_sock.sendall(msg+"\0")
        client_sock.close()
        print "Connection closed. Bye"

    def echo_handler(self, client_addr, client_sock, msgs):
        '''echos all messages received from Client back to Client'''
        self.msgs_handler(client_addr, client_sock, self.myreceive_all(client_sock))
            
    def myreceive_one(self, client_sock):
        '''read one msg, chunk by chunk; return one msg'''
        #msgs_rest = self.msgs_rest
        #self.msgs_rest = '' # reset instance variable

        # read rest of last message from buffer (if buffer not empty)
        msg, sep, msgs_rest = self.msgs_rest.partition("\0")
        if sep != '':
            self.msgs_rest = msgs_rest
            return msg

        while True:
            chunk = client_sock.recv(MAX_BUFFER_SIZE)
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

            
    def myreceive_all(self, client_sock):
        ''' returns a list of messages'''
        msgs=[]
        first_msg = self.myreceive_one(client_sock)
        print ("first msg:", first_msg) # number of msgs to follow
        num_msgs = int(first_msg)
        for i in range(num_msgs):
            msgs.append(self.myreceive_one(client_sock))
        return msgs
        
