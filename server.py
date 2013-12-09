import socket
import threading
# SERVER 

MAX_BUFFER_SIZE = 1024
BACKLOG = 5

class MySocket:
    '''
    a server socket
    '''

    def __init__(self, sock=None):
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
                client, addr = self.sock.accept()
                print "connection attempt", client
                c = Connection(client, addr, handler, msgs)
                c.start()
                print "Started connection"
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
            
    def myreceive_one(self, client_sock, msgs_rest_passed):
        '''read one msg, chunk by chunk; return one msg'''

        # read rest of last message from buffer (if buffer not empty)
        msg, sep, msgs_rest = msgs_rest_passed.partition("\0")
        if sep != '':
            msgs_rest_new = msgs_rest
            return (msg, msgs_rest_new)

        while True:
            chunk = client_sock.recv(MAX_BUFFER_SIZE)
            #print ("client received ", chunk, len(chunk))
            # check for msg delimiter
            next_msg, sep, msgs_rest = chunk.partition("\0")
            if sep  != '':
                # delimiter found
                msg = msg + next_msg
                msgs_rest_new = msgs_rest
                return (msg, msgs_rest_new)
            else:
                # delimiter not found
                msg = msg + next_msg

            
    def myreceive_all(self, client_sock):
        ''' returns a list of messages'''
        msgs=[]
        first_msg, msgs_rest = self.myreceive_one(client_sock, '')
        print ("first msg:", first_msg) # number of msgs to follow
        num_msgs = int(first_msg)
        for i in range(num_msgs):
            m, msgs_rest = self.myreceive_one(client_sock, msgs_rest)
            msgs.append(m)
        return msgs
        
class  Connection(threading.Thread):
    """
    a threaded connection between server and client
    """
    def __init__(self, client_sock, client_addr, handler, msgs=None):
        threading.Thread.__init__(self)
        self.client = client_sock
        self.addr = client_addr
        self.handler = handler
        self.msgs = msgs

    def run(self):
        self.handler(self.addr, self.client, self.msgs)
