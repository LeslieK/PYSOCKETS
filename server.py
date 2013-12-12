import socket
import select
from collections import defaultdict, deque

# SERVER 

PORT = 8765
SERVER_ADDR = ('localhost', PORT)
MAX_BUFFER_SIZE = 1024
BACKLOG = 5
DELIMITER = "\n"

class Server:
    '''
    A server that uses select to handle multiple clients at a time.
    Entering any line of input at the terminal will exit the server.
    '''

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of local addresses (why is this not the default?)
        self.sock.bind(SERVER_ADDR)
        self.sock.listen(BACKLOG) # max number of connections waiting to be served
        self.MSGS = defaultdict(deque)     # complete messages per client     
        self.buffers = {}                  # partial messages per client
        self.MSGSLEN = {}                  # message lengths per client [len, sent, recvd]

    def serv(self, inputs, msgs=None):  # inputs = [self.sock]
        inputs = set(inputs)
        outputs = set()
        running = True
        while running:
            readready, writeready, _ = select.select(inputs, outputs, [])
            print readready
            for s in readready:
                if s == self.sock:
                    # handle the server socket
                    try:
                        client, addr = self.sock.accept()
                        print "Server accepted {}".format(client.getsockname())
                        client.setblocking(False)
                        self.MSGS[client.fileno()].append("")
                        self.buffers[client.fileno()] = ""
                        self.MSGSLEN[client.fileno()] = -1
                        inputs.add(client)
                    except socket.error as e:
                        if e.errno == 10054:
                            print e
                        continue
                else:
                    # read from client socket
                    self.read(s)
                    # data can be sent to client
                    outputs.add(s)
            for s in writeready:
                    # write to client socket
                    print "Writing to {}".format(s)
                    self.write(s)

    def write(self, client_sock):
        """write characters"""
        # attempt to write a complete message
        nextMSG = self.MSGS[client_sock.fileno()].popleft()
        if nextMSG != '':
            print "Server: about to send {}".format(nextMSG)
            sent = client_sock.send(nextMSG)
            print "Server sent {} bytes to {}".format(sent, client_sock.getsockname())
            if sent == 0:
                raise RuntimeError("socket connection broken")
            self.MSGS[client_sock.fileno()].appendleft(nextMSG[sent:]) # add part of msg not sent to front of deque
        return 
    
    def read(self, client_sock):
        """read characters; build messages"""
        buff = self.buffers[client_sock.fileno()]
        if DELIMITER in buff:
            next_msg, sep, msgs_rest = buff.partition(DELIMITER)
            self.MSGS[client_sock.fileno()].append(next_msg)        # store complete msg on deque
            self.buffers[client_sock.fileno()] = msgs_rest          # store partial msg
        else:
            chunk = client_sock.recv(MAX_BUFFER_SIZE)
            next_msg, sep, msgs_rest = chunk.partition(DELIMITER)
            if sep  == DELIMITER:
                # delimiter found
                # store number of messaages from this client, if not yet stored
                if self.MSGSLEN[client_sock.fileno()] < 0:
                    self.MSGSLEN[client_sock.fileno()] = int((buff + next_msg)[:-1])  # set number of messages
                # store complete msg
                # store partial msg
                self.MSGS[client_sock.fileno()].append(buff + next_msg)
                self.buffers[client_sock.fileno()] = msgs_rest
            else:
                # delimiter not found
                # concatenate partial messages
                self.buffers[client_sock.fileno()] = buff + next_msg
        return 

##################################################################################            

if __name__ == "__main__":
    print 'Echo Server starting'
    s = Server(PORT)
    s.serv([s.sock]) 