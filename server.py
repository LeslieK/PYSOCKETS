import socket
# SERVER 

MAX_BUF_SIZE = 1024
PORT = 8765

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

    def serve(self, port, handler):
        self.sock.bind(('', port))
        self.sock.listen(5) # queue backlog = 5
        while(True):
            client_sock, client_addr = self.sock.accept()
            print ("connection attempt", client_addr)
            handler(client_addr, client_sock)

def my_handler(client_addr, client_sock):
    while True:
        msg = client_sock.recv(MAX_BUF_SIZE)
        print ("received ",  len(msg))
        if not msg:
            break
        # send msg with number of msgs to expect after this one
        client_sock.sendall("3\0")
        # send msg 1
        client_sock.sendall(msg)
        client_sock.sendall("Another message!\0")
        client_sock.sendall("That's all folks!\0")
    client_sock.close()
    print ("Connection closed. Bye")
    
s = mysocket()
s.serve(PORT, my_handler)
