import Client
import Server
import threading
import time

PORT = 8765

with open("Genesis.txt") as f:
	MSGS = f.read().split('\n')
	N_MSG = len(MSGS)
f.close()

def start_server():
	server_s = Server.MySocket()
	server_s.msgs_serve(PORT, MSGS)

thread.start_new_thread(start_server, ())
# give server time to start up
time.sleep(.5)

client_s = Client.MySocket()
client_s.connect('localhost', PORT)
print (client_s.myreceive_all()) # print what it receives from server

#assert(len(MSGS) == client_s.myreceive_all)
print len(MSGS)




