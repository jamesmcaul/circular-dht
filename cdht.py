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

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.bind((self.host, 5000 + self.id))

		while True:
			message, address = server_socket.recvfrom(1024)
			message_text = message.decode()

			print("A ping request message was received from Peer %s" % message_text[4:])

			response = "PING" + str(self.id)
			response.encode()
			server_socket.sendto(response, address)


	def pingSuccessors(self):
		for pings in range(10):
			time.sleep(5)
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			########## Ping first successor ##########

			# client_socket.bind((self.host, 6000 + self.id))
			client_socket.settimeout(1.0)
			message_string = 'PING' + str(self.id)
			message = message_string.encode()

			addr = (self.host, 5000 + self.next_id)

			client_socket.sendto(message, addr)

			try:
				data, server = client_socket.recvfrom(1024)
				response = data.decode()
				print("A ping response message was received from Peer %s" % response[4:])

			except socket.timeout:
				print('PING TO PEER %d TIMED OUT' % self.next_id)

			########## Ping second successor ##########		
			
			# client_socket.bind((self.host, 7000 + self.id))
			client_socket.settimeout(1.0)
			message_string = 'PING' + str(self.id)
			message = message_string.encode()

			addr = (self.host, 5000 + self.next_next_id)

			client_socket.sendto(message, addr)
			try:
				data, server = client_socket.recvfrom(1024)
				response = data.decode()
				print("A ping response message was received from Peer %s" % response[4:])

			except socket.timeout:
				print('PING TO PEER %d TIMED OUT' % self.next_next_id)
 



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

	pingSuccessorsThread = threading.Thread(target=peer.pingSuccessors)

	pingServerThread.start() 
	pingSuccessorsThread.start()

	print("Main function ending")
	sys.exit()


if __name__ == "__main__":
	main()