import Client
#import Server

PORT = 8765

with open("Genesis.txt") as f:
	MSGS = f.read().split('\n')

def start_client(msgs):
	client_s = Client.MySocket()
	client_s.connect('localhost', PORT)
	# send first message with number of messages
	client_s.mysend(str(len(msgs)))
	for msg in msgs:
		client_s.mysend(msg)
	print (len(client_s.myreceive_all())) # print what it receives from server

print 'Client about to send {} msgs'.format(len(MSGS))
start_client(MSGS)







