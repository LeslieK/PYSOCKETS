import Client
import Server
import threading
import time

PORT = 8765

#with open("Genesis.txt") as f:
#	MSGS = f.read().split('\n')
#	N_MSG = len(MSGS)

def start_server():
	server_s = Server.MySocket()
	server_s.echo_serve(PORT)

#print 'Server sent {} msgs'.format(N_MSG)
print 'Echo Server starting'
start_server()




