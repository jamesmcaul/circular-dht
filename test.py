import random
import socket
import time
import threading

def serverInit():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_socket.bind(('', 5001))

	while True:
	    message, address = server_socket.recvfrom(1024)
	    print(message)
	    print(address)
	    message = message.upper()
	    server_socket.sendto(message, address)

def clientInit():
	for pings in range(10):
	    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    client_socket.bind(('',6001))
	    client_socket.settimeout(1.0)
	    message = b'First'
	    addr = ("127.0.0.1", 5001)

	    client_socket.sendto(message, addr)
	    try:
	        data, server = client_socket.recvfrom(1024)
	        print(data)
	    except socket.timeout:
	        print('REQUEST TIMED OUT')

def clientInit2():
	for pings in range(10):
	    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	    client_socket.bind(('',7001))
	    client_socket.settimeout(1.0)
	    message = b'Second'
	    addr = ("127.0.0.1", 5001)

	    client_socket.sendto(message, addr)
	    try:
	        data, server = client_socket.recvfrom(1024)
	        print(data)
	    except socket.timeout:
	        print('REQUEST TIMED OUT')


def main():

	thread1 = threading.Thread(target=serverInit)

	thread2 = threading.Thread(target=clientInit)

	thread3 = threading.Thread(target=clientInit2)

	thread1.start()
	thread2.start()
	thread3.start()




if __name__ == "__main__":
	main()