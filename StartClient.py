import Client
import select


PORT = 8765
SERVER_ADDR = ('localhost', PORT)
DELIMITER = "\0"

with open("Genesis.txt") as f:
	# retain "\n" 
	# newline is msg delimiter
	MSGS = []
	while True:
		msg = f.readline()
		if msg == "":
			break
		msg = msg + DELIMITER
		MSGS.append(msg)

client = Client.Client(SERVER_ADDR, MSGS) # creates a non-blocking client socket
#rsocket = [client.sock]
wsocket = [client.sock]
rsocket = []

running = True
while running:
	print "at top of client select loop", rsocket, wsocket
	readready, writeready, _ = select.select(rsocket, wsocket, [])
	print readready, writeready
	print len(writeready), len(readready)
	for s in readready:
		isDone = client.receive()
		if isDone:
			print "{} done receiving recvL".format(s.fileno())
			rsocket.remove(s)
			running = False
			s.close()
		else:
			print "{} still receiving".format(s.fileno())
			if s not in rsocket:
				# monitor for reading
				rsocket.append(s)	
	for s in writeready:
		isDone = client.send()
		if isDone:
			print "{} done sending".format(s.fileno())
			# no need to monitor this write channel anymore
			wsocket = []
			# need to monitor read channel for a response
			if s not in rsocket:
				rsocket.append(s)
		else:
			print "{} still sending".format(s.fileno())
			if s not in rsocket:
				# monitor read channel for a response
				rsocket.append(s)
print "after client select loop", running
print readready is None
print readready == []







