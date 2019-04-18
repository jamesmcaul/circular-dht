# James McAuliffe, z5248493
# Python version 3.*

import sys
import socket
import threading
import time

class Peer():

	def __init__(self, id_in, next_id, next_next_id, mss, drop_prob):
		self.host = "127.0.0.1" 
		self.id = id_in
		self.next_id = next_id
		self.next_next_id = next_next_id
		self.mss = mss
		self.drop_prob = drop_prob


	def pingServerInit(self):
		# print("Ping Server Initializing to port %d" % (5000 + self.id))
		# print(self.id)
		# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# server_socket.bind(("127.0.0.1", 5001))

		# while True:
		# 	print("Server waiting for ping... ")
		# 	message, client_address = server_socket.recvfrom(1024)

		# 	print(message)
		# 	print(client_address)

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.bind(('', 5000 + self.id))

		while True:
		    message, address = server_socket.recvfrom(1024)
		    print(message)
		    print(address)
		    message = message.upper()
		    server_socket.sendto(message, address)


	def pingFirstSuccessor(self):
		# # Ping Message
		# while True:  
		# 	time.sleep(5)
		# 	print("Pinging First Successor")

		# 	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# 	# client_socket.bind(('', 6000 + self.id))
		# 	# client_socket.settimeout(5) 

		# 	message = b'First'
  #     		client_socket.sendto = (message, ("127.0.0.1", 5001))

  #     		# try:
  #     		# 	response, server_address = client_socket.recvfrom(1024)
  #     		# 	print("Ping first response received")

  #     		# except socket.timeout:
  #     		# 	print("PING FIRST SUCCESSOR TIMED OUT") 

  		for pings in range(10):
		    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		    client_socket.bind(('',6000 + self.id))
		    client_socket.settimeout(1.0)
		    message = b'First'
		    addr = ("127.0.0.1", 5000 + self.id)

		    client_socket.sendto(message, addr)
		    try:
		        data, server = client_socket.recvfrom(1024)
		        print(data)
		    except socket.timeout:
		        print('REQUEST TIMED OUT')




	def pingSecondSuccessor(self):
		# # Ping Message
		# while True: 
		# 	time.sleep(5)
		# 	print("Pinging Second Successor")

		# 	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# 	# client_socket.bind(('', 7000 + self.id))
		# 	# client_socket.settimeout(5)

		# 	message = b'Second'
		# 	client_socket.sendto = (message, ("127.0.0.1", 5001))

		# 	# try:
		# 	# 	response, server_address = client_socket.recvfrom(1024)
		# 	# 	print("ping second response received")

		# 	# except socket.timeout:
		# 	# 	print("PING SECOND SUCCESSOR TIMED OUT")	

		for pings in range(10):
		    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		    client_socket.bind(('',7000 + self.id))
		    client_socket.settimeout(1.0)
		    message = b'Second'
		    addr = ("127.0.0.1", 5000 + self.id)

		    client_socket.sendto(message, addr)
		    try:
		        data, server = client_socket.recvfrom(1024)
		        print(data)
		    except socket.timeout:
		        print('REQUEST TIMED OUT')	





 



def main():

	###################  Read in arguments  #####################

	assert len(sys.argv) == 6, "Error: Include all required arguments"

	init_peer = int(sys.argv[1])
	next_peer = int(sys.argv[2])
	next_next_peer = int(sys.argv[3])

	assert (init_peer >= 0 and init_peer <= 255), "Error: First argument not in range"
	assert (next_peer >= 0 and next_peer <= 255), "Error: Second argument not in range"
	assert (next_next_peer >= 0 and next_next_peer <= 255), "Error: Third argument not in range"

	mss = int(sys.argv[4])

	drop_prob = float(sys.argv[5])
	assert (drop_prob >= 0 and drop_prob <= 1), "Error: Fifth arguement not in range"

	print("Successfully read in arguements")


	###################  Initialize peer  #####################

	peer = Peer(init_peer, next_peer, next_next_peer, mss, drop_prob)

	pingServerThread = threading.Thread(target=peer.pingServerInit)
	pingServerThread.daemon = True

	pingFirstSuccessorThread = threading.Thread(target=peer.pingFirstSuccessor)
	pingFirstSuccessorThread.daemon = True 

	pingSecondSuccessorThread = threading.Thread(target=peer.pingSecondSuccessor)
	pingSecondSuccessorThread.deamon = True

	pingServerThread.start() 
	pingFirstSuccessorThread.start()
	pingSecondSuccessorThread.start() 

	print("Main function ending")
	sys.exit()


if __name__ == "__main__":
	main()