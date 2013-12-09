import Client
import Server
import threading
import time

PORT = 8765

#with open("Genesis.txt") as f:
#	MSGS = f.read().split('\n')
#	N_MSG = len(MSGS)

def start_server():
	''' create server socket; call the handler'''
	s = Server.MySocket()
	#server_s.echo_serve(PORT)
	s.serv(PORT, s.echo_handler) 

print 'Echo Server starting'
start_server()




