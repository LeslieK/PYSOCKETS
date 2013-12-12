import Client
import select


PORT = 8765
SERVER_ADDR = ('localhost', PORT)

with open("Genesis.txt") as f:
	# retain "\n" 
	# newline is msg delimiter
	MSGS = []
	while True:
		msg = f.readline()
		if msg != "":
			MSGS.append(msg)
		else:
			break

client = Client.Client(SERVER_ADDR, MSGS) # creates a non-blocking client socket
rsocket = [client.sock]
wsocket = [client.sock]

running = True
while running:
	readready, writeready, _ = select.select(rsocket, wsocket, [])
	for s in writeready:
		isDone = client.send()
		if isDone:
			print "Done sending"
			wsocket.remove(s)
	for s in readready:
		isDone = client.receive()
		if isDone:
			rsocket.remove(s)
			print "Done receiving"
			running = False
			s.close()







