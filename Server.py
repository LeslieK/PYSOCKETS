import socket
import select
from collections import defaultdict, deque

# SERVER 

PORT = 8765
SERVER_ADDR = ('localhost', PORT)
MAX_BUFFER_SIZE = 1024
BACKLOG = 5
DELIMITER = "\0"

class Server:
    """
    A server that uses select to handle multiple clients at a time.
    """

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of local addresses (why is this not the default?)
        self.sock.bind(SERVER_ADDR)
        self.sock.listen(BACKLOG)          # max number of connections waiting to be served
        self.MSGS = defaultdict(deque)     # complete messages per client     
        self.buffers = {}                  # partial messages per client
        self.MSGSLEN = {}                  # message lengths per client [len, sent, recvd]
        self.MSGSRECV = {}                 # messages received from each client

    def serv(self, inputs, msgs=None):  # inputs = [self.sock]
        inputs = inputs
        outputs = []
        running = True
        while running:
            readready, writeready, _ = select.select(inputs, outputs, [])
            for s in readready:
                if s == self.sock:
                    # handle the server socket
                    try:
                        print "Waiting for client to connect"
                        client, addr = self.sock.accept()
                        print "Server accepted {}".format(client.getsockname())
                        # set connection to non-blocking
                        client.setblocking(False)
                        # give new connection a queue to store its messages
                        self.MSGS[client.fileno()].append("")
                        # give new connection a buffer variable to store characters received
                        self.buffers[client.fileno()] = ""
                        # give new connection a key in dict to store # msgs expected
                        self.MSGSLEN[client.fileno()] = -1
                        # give new connection a key in dict to store # msgs received
                        self.MSGSRECV[client.fileno()] = 0
                        # add connection to list of inputs to monitor
                        inputs.append(client)
                    except socket.error as e:
                        if e.errno == 10054:
                            print e
                        continue
                else:
                    # read from an already established client socket
                    isDone = self.read(s)
                    if isDone is None:
                        # s disconnected
                        print "{} disconnected.".format(s.getsockname())
                        inputs.remove(s)
                        # remove its resources
                        del self.MSGS[s.fileno()]
                        del self.buffers[s.fileno()]
                        del self.MSGSLEN[s.fileno()]
                        del self.MSGSRECV[s.fileno()]
                        if s in outputs:
                            # remove s from outputs (no need to respond to it anymore)
                            outputs.remove(s)
                        s.close()
                    elif isDone:
                        print "Server is done reading from client {}".format(s.fileno())
                        inputs.remove(s)
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        # add s to outputs so server can send a response
                        if s not in outputs:
                            outputs.append(s)
            for s in writeready:
                    # write to client socket
                    #print "writing to {}".format(s.getsockname()[1])
                    isDone = self.write(s)
                    if isDone:
                        print "Server is done writing to client {}".format(s.fileno())
                        if s in outputs:
                            outputs.remove(s)
                        #print "closed {}".format(client.getsockname())
                        s.close()

    def write(self, client_sock):
        """write characters"""
        dq = self.MSGS[client_sock.fileno()]
        if dq:
            nextMSG = dq.popleft()
            if nextMSG != '':
                sent = client_sock.send(nextMSG)        # nextMSG is top element of dq (chars up to and including DELIMITER)
                print "Server sent {} bytes to {}".format(sent, client_sock.fileno())
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                if sent < len(nextMSG):
                    self.MSGS[client_sock.fileno()].appendleft(nextMSG[sent:])           # add part of msg not sent to front of deque
                # check if done writing
                # done reading and len(MSGS deque) == 0
                if self.MSGSRECV[client_sock.fileno()] == self.MSGSLEN[client_sock.fileno()] + 1:
                    return len(self.MSGS[client_sock.fileno()]) == 0
                else:
                    # server has not finished receiving all messages
                    return False
        if self.MSGSRECV[client_sock.fileno()] == self.MSGSLEN[client_sock.fileno()] + 1:
            return len(self.MSGS[client_sock.fileno()]) == 0
        else:
            return False
    
    def read(self, client_sock):
        """read characters; build messages"""
        buff = self.buffers[client_sock.fileno()]
        msgs_recv = self.MSGSRECV[client_sock.fileno()]
        if DELIMITER in buff:
            next_msg, sep, msgs_rest = buff.partition(DELIMITER)
            self.MSGS[client_sock.fileno()].append(next_msg + DELIMITER)        # store complete msg on deque
            self.MSGSRECV[client_sock.fileno()] = msgs_recv + 1
            self.buffers[client_sock.fileno()] = msgs_rest                  # store partial msg in buffer
            return self.MSGSRECV[client_sock.fileno()] == self.MSGSLEN[client_sock.fileno()] + 1                    
        else:
            chunk = client_sock.recv(MAX_BUFFER_SIZE)
            # check that client_sock is still connected
            if chunk:
                next_msg, sep, msgs_rest = chunk.partition(DELIMITER)
                if sep == DELIMITER:
                    # store number of messages from this client, if not yet stored
                    if self.MSGSLEN[client_sock.fileno()] < 0:
                        self.MSGSLEN[client_sock.fileno()] = int(buff + next_msg)               # set total number of messages to follow
                        self.MSGS[client_sock.fileno()].append(buff + next_msg + DELIMITER)     # store complete msg
                        self.MSGSRECV[client_sock.fileno()] = msgs_recv + 1                     # first message received
                    else:
                        self.MSGS[client_sock.fileno()].append(buff + next_msg + DELIMITER)     # store complete msg
                        self.buffers[client_sock.fileno()] = msgs_rest                          # store partial msg
                        self.MSGSRECV[client_sock.fileno()] = msgs_recv + 1                     # incr messages received  
                else:
                    # delimiter not found
                    # concatenate partial messages
                    self.buffers[client_sock.fileno()] = buff + next_msg
                return self.MSGSRECV[client_sock.fileno()] == self.MSGSLEN[client_sock.fileno()] + 1

##################################################################################            

if __name__ == "__main__":
    print 'Echo Server starting'
    s = Server(PORT)
    s.serv([s.sock]) 
