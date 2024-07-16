import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 12345))

while True:
	message = client_socket.recv(1024).decode()
        if not message:
		break

	print(message, end='')
	data = input()
        client_socket.send(data.encode())
        response = client_socket.recv(1024).decode()
        print(response, end='')

        if "Goodbye!" in response:
		break
    
client_socket.close()

