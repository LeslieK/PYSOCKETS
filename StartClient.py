import Client
#import Server

PORT = 8765

with open("Genesis.txt") as f:
	MSGS = f.read().split('\n')

def start_client(msgs):
	'''create Client socket; send all data'''
	s = Client.MySocket()
	s.connect('localhost', PORT)
	# send first message with number of messages
	s.mysend(str(len(msgs))) # requires file read all at once
	for msg in msgs:
		s.mysend(msg)
	print (len(s.myreceive_all())) # print what it receives from server

print 'Client about to send {} msgs'.format(len(MSGS))
start_client(MSGS)