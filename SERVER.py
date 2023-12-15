import socket 
import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ("127.0.0.1", 4444)
server_socket.bind(server_address)
server_socket.listen(5)

print("Server is running on {}:{}".format(*server_address))

def get_client_name(client_socket):
    Message = "Server: Please Enter Your Name"
    client_socket.send(Message.encode())
    return client_socket.recv(1024).decode()

def get_updated_user_list():
    return [client_names[client.getpeername()] for client in clients if client != server_socket]

clients = [server_socket]
client_names = {}

while True:
    read_socket, _, _ = select.select(clients, [], [])

    for sock in read_socket:
        if sock == server_socket:            
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)

            print("New Connection From {}:{}".format(*client_address))
            print("Number of connections: ", len(clients) - 1)

            client_name = get_client_name(client_socket)
            client_names[client_socket.getpeername()] = client_name

            Message = (f"Welcome to the server, {client_name}, Start sending messages")
            client_socket.send(Message.encode())

            updated_users = get_updated_user_list()
            update_user_message = f"/Users {', '.join(updated_users)}"
            for client in clients:
                if client != server_socket and client != sock:
                    try:
                        client.send(update_user_message.encode())
                    except Exception as e:
                        print("Error Updating Users")
                        break 


        else:
            try:
                data = sock.recv(1024).decode()
                if data:
                    for client in clients:
                        if client != server_socket and client != sock:
                            try:
                                sender_name = client_names[sock.getpeername()]
                                New_message = (f"{sender_name}: {data}")
                                client.send(New_message.encode())
                            except:
                                clients.remove(client)
                                print(f"{client_names[sock.getpeername()]} removed due to an exception")
                                del client_names[sock.getpeername()]
            except:
                clients.remove(sock)
                print(f"{client_names[sock.getpeername()]} removed due to an exception")
                del client_names[sock.getpeername()]

                continue

server_socket.close()


        

