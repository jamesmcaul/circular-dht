# James McAuliffe, z5248493
# Python version 3.*

import sys
import socket
import threading
import time
import random

class Peer():

	def __init__(self, id_in, next_id, next_next_id, mss, drop_prob):
		self.host = "127.0.0.1" 
		self.id = id_in
		self.next_id = next_id
		self.next_next_id = next_next_id
		self.mss = mss
		self.drop_prob = drop_prob
		self.predecessor = -1
		self.prepredecessor = -1
		self.start_time = time.time()


	def pingServerInit(self):

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.bind((self.host, 50000 + self.id))

		while True:
			message, address = server_socket.recvfrom(1024)
			message_text = message.decode()

			# Ping Response
			if message_text[:4] == "PING":

				print("A ping request message was received from Peer %s." % message_text[5:])

				if message_text[4] == '1':
					self.predecessor = int(message_text[5:])

				elif message_text[4] == '2':
					self.prepredecessor = int(message_text[5:])

				else: 
					print("PROTOCOL ERROR") 


				response_string = "PING" + str(self.id)
				response = response_string.encode()
				server_socket.sendto(response, address)

			else:
				print("ERROR: COULD NOT IDENTIFY PACKET RECEVIED OVER UDP PORT %d" % 50000 + self.id)



	def pingSuccessors(self):
		first_drop_count = 0
		second_drop_count = 0 

		while True:

			if first_drop_count > 4:
				print("Peer %d no longer alive." % self.next_id)

				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				departure_message_text = "K1"
				departure_message = departure_message_text.encode()
				sock.connect((self.host, 50000 + self.next_next_id))
				sock.send(departure_message)
				response = sock.recv(1024)
				sock.close()

				response_text = response.decode()

				self.next_id = self.next_next_id
				self.next_next_id = int(response_text) 

				print("My first successor is now peer %d." % self.next_id)
				print("My second successor is now peer %d." % self.next_next_id)

				first_drop_count = 0


			if second_drop_count > 5: 
				print("Peer %d no longer alive." % self.next_next_id)

				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				departure_message_text = "K2"
				departure_message = departure_message_text.encode()
				sock.connect((self.host, 50000 + self.next_id))
				sock.send(departure_message)
				response = sock.recv(1024)
				sock.close()

				response_text = response.decode()

				self.next_next_id = int(response_text)

				print("My first successor is now peer %d." % self.next_id)
				print("My second successor is now peer %d." % self.next_next_id)

				second_drop_count = 0


			time.sleep(5)
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			########## Ping first successor ##########

			# client_socket.bind((self.host, 6000 + self.id))
			client_socket.settimeout(1.0)
			message_string = 'PING1' + str(self.id)
			message = message_string.encode()

			addr = (self.host, 50000 + self.next_id)

			client_socket.sendto(message, addr)

			try:
				data, server = client_socket.recvfrom(1024)
				response = data.decode()
				print("A ping response message was received from Peer %s." % response[4:])
				first_drop_count = 0

			except socket.timeout:
				print('PING TO PEER %d TIMED OUT' % self.next_id)
				first_drop_count += 1

			########## Ping second successor ##########		
			
			# client_socket.bind((self.host, 7000 + self.id))
			client_socket.settimeout(1.0)
			message_string = 'PING2' + str(self.id)
			message = message_string.encode()

			addr = (self.host, 50000 + self.next_next_id)

			client_socket.sendto(message, addr)
			try:
				data, server = client_socket.recvfrom(1024)
				response = data.decode()
				print("A ping response message was received from Peer %s." % response[4:])
				second_drop_count = 0

			except socket.timeout:
				print('PING TO PEER %d TIMED OUT' % self.next_next_id)
				second_drop_count += 1


	def tcpServerInit(self):
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind((self.host, 50000 + self.id))
		server_socket.listen(5)

		while True: 
			conn, address = server_socket.accept()

			message = conn.recv(1024)
			message_text = message.decode()

			if message_text[0] == "K":
				response_text = str(self.next_id)
				message = response_text.encode()

			elif message_text[:3] == "REQ":
				file = int(message_text[3:7])
				file_hash = file % 256

				if file_hash == self.id or (file_hash < self.id and file_hash > self.predecessor) or (file_hash < self.id and self.id < self.predecessor) or (file_hash > self.id and file_hash > self.predecessor and self.id < self.predecessor):
					print("File %s is here." % message_text[3:7])
					response_text = "RES" + message_text[3:7] + "|" + str(self.id)
					response = response_text.encode()

					respond_to_peer = int(message_text[8:])

					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((self.host, 50000 + respond_to_peer))
					sock.send(response)
					sock.close()
					print("A response message, destined for peer %d, has been sent." % respond_to_peer)

					self.fileTransfer(respond_to_peer, message_text[3:7])

					print("The file is sent.")




				else:
					print("File %s is not stored here." % message_text[3:7])
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((self.host, 50000 + self.next_id))
					sock.send(message)
					sock.close()
					print("File request message has been forwarded to my successor.")


			elif message_text[:3] == "RES":
				print("Received a response message from peer %s, which has the file %s." % (message_text[8:], message_text[3:7]))

				self.fileReceive()

				print("The file is received.")


			else: 
				split1 = message_text.find("|")
				split2 = message_text.find("|", split1 + 1)
				split3 = message_text.find("|", split2 + 1)

				print("Peer %s will depart from the network." % message_text[split1+1:split2])

				if message_text[:split1] == "1":
					print("My first successor is now peer %s." % message_text[split2+1:split3])
					self.next_id = int(message_text[split2+1:split3])

					print("My second successor is now peer %s." % message_text[split3+1:])
					self.next_next_id = int(message_text[split3+1:])

				elif message_text[:split1] == "2": 
					print("My first successor is now peer %d." % self.next_id)

					print("My second successor is now peer %s." % message_text[split2+1:split3])
					self.next_next_id = int(message_text[split2+1:split3])

				else:
					print("ERROR: INCORRECT PROTOCOL")
					conn.close()
					continue 


			conn.send(message)
			conn.close()


	def fileTransfer(self, rec_id, file):
		print("We now start sending the file ......")

		transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		transfer_socket.settimeout(1.0)
		addr = (self.host, 60000 + rec_id)

		file_name = str(file) + ".pdf"

		f = open(file_name, "rb")
		file_data = f.read(self.mss)

		resp_log = open("responding_log.txt", "a+b")
		seq_num = 0 
		ack_num = 0
		is_resend = False

		while(file_data):

			message = "SEQ" + str(seq_num) + "ACK" + str(ack_num) + "X" + str(sys.getsizeof(file_data)) + "F"
			packet = message.encode('latin-1')
			packet = packet + file_data

			transfer_socket.sendto(packet, addr)

			try: 
				data, server = transfer_socket.recvfrom(1024)

				if not is_resend: 
					log_message = "snd " + str(time.time() - self.start_time) + " " + str(seq_num) + " " + str(sys.getsizeof(file_data)) + " " + str(ack_num) + "\r\n"
					log  = log_message.encode("latin-1")
					resp_log.write(log)

				if is_resend:
					log_message = "RTX " + str(time.time() - self.start_time) + " " + str(seq_num) + " " + str(sys.getsizeof(file_data)) + " " + str(ack_num) + "\r\n"
					log  = log_message.encode("latin-1")
					resp_log.write(log)

				seq_num += 1
				ack_num += 1
				is_resend = False 


			except socket.timeout:
				is_resend = True
				continue

			file_data = f.read(self.mss)

		end_message = "DONE"
		packet = end_message.encode()
		transfer_socket.sendto(packet, addr)

		f.close()
		resp_log.close()

	def fileReceive(self):
		print("We now start receiving the file .......")

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.bind((self.host, 60000 + self.id))

		f = open("received_file.pdf", "wb")

		req_log = open("requesting_log.txt", "a+b")

		while True:
			message, address = server_socket.recvfrom(1024)
			message_text = message.decode('latin-1')

			if message_text[0:4] == "DONE":
				break

			random_number = random.random()

			index_seq = message_text.find("Q")
			index_ack = message_text.find("A")
			index_x = message_text.find("X")
			index_f = message_text.find("F")

			if random_number < self.drop_prob:
				log_message = "drop " + str(time.time() - self.start_time) + " " + message_text[index_seq+1:index_ack] + " " + message_text[index_x+1:index_f] + " " + message_text[index_ack+3:index_x] + "\r\n"
				log  = log_message.encode("latin-1")
				req_log.write(log)
				continue

			file_data = (message_text[index_f+1:]).encode('latin-1')
			f.write(file_data)

			log_message = "rcv " + str(time.time() - self.start_time) + " " + message_text[index_seq+1:index_ack] + " " + message_text[index_x+1:index_f] + " " + message_text[index_ack+3:index_x] + "\r\n"
			log  = log_message.encode("latin-1")
			req_log.write(log)

			ack_text = "ACK"
			ack = ack_text.encode()
			server_socket.sendto(ack, address)

		f.close()
		req_log.close()








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

	tcpServerThread = threading.Thread(target=peer.tcpServerInit)
	tcpServerThread.daemon = True

	pingSuccessorsThread = threading.Thread(target=peer.pingSuccessors)
	pingSuccessorsThread.daemon = True

	pingServerThread.start() 
	tcpServerThread.start()
	pingSuccessorsThread.start()


	while True: 
		text = input()
		
		if text == "quit":

			if peer.predecessor == -1 or peer.prepredecessor == -1:
				print("ERROR: PEER CANNOT SAFETLY EXIT, TRY AGAIN LATER") 
				continue 

			###### Depart from first predecessor #####
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			departure_message_text = "1|" + str(peer.id) + "|" + str(peer.next_id) + "|" + str(peer.next_next_id)
			departure_message = departure_message_text.encode()
			sock.connect((peer.host, 50000 + peer.predecessor))
			sock.send(departure_message)
			response = sock.recv(1024)
			sock.close()

			###### Depart from second predecessor #####
			sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			departure_message_text = "2|" + str(peer.id) + "|" + str(peer.next_id) + "|" + str(peer.next_next_id)
			departure_message = departure_message_text.encode()
			sock2.connect((peer.host, 50000 + peer.prepredecessor))
			sock2.send(departure_message)
			response = sock2.recv(1024)
			sock2.close()

			break


		elif text[:7] == "request":

			file = text[8:]

			sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			departure_message_text = "REQ" + file + "|" + str(peer.id)
			departure_message = departure_message_text.encode()
			sock3.connect((peer.host, 50000 + peer.next_id))
			sock3.send(departure_message)
			sock3.close()

			print("File request message for %s has been sent to my successor." % file)


		else:
			print("ERROR: NOT A VALID INPUT")





	print("Main function ending")
	sys.exit()


if __name__ == "__main__":
	main()