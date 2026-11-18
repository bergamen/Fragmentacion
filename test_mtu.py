from router import *

message = b"Hola como estas"

segment = {"address":("197.0.0.1",8000),"ttl":10,"id":10,"offset":0,"tamanno":len(message),"flag":0,"message":message}

print(fragment_IP_packet(segment,15+16))
print(fragment_IP_packet(segment,4+16))