from router import *
import socket



big_message = '1234567890\n'*15


final_ip = "127.0.0.1"
final_puerto = input("Ingrese el puerto destino: ")

env_ip = "127.0.0.1"
env_puerto = input("Ingrese el puerto envio: ")

#message = input("Ingrese el mensaje: ")
message = big_message

id = int(input("Ingrese el id: "))

segment = {"address":(final_ip,int(final_puerto)),"message":message.encode(),"ttl":10,"id":300,"offset":0,"flag":0,"tamanno":len(message.encode())}

router_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
address = (env_ip,int(env_puerto))
print(segment)
router_socket.sendto(create_packet(segment),address)
print("Mensaje enviado")
