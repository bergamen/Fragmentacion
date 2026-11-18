from router import *

message = b'Este es el mensaje a fragmentar'
IP_packet_v1 = {"address":("197.0.0.1",8000),"ttl":10,"id":1,"flag":0,"offset":0,"tamanno":len(message),"message":message}
MTU = 16 + 4

fragment_list = fragment_IP_packet(IP_packet_v1, MTU)
fragment_list = list(map(parse_packet,fragment_list))
IP_packet_v2 = reassemble_IP_packet(fragment_list)

print(fragment_list)

print(IP_packet_v1)
print(IP_packet_v2)

print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))