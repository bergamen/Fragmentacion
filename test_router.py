from router import *

IP_packet_v1 = int(255).to_bytes(4) + int(8000).to_bytes(2) + int(10).to_bytes(1) + int(1).to_bytes(2) + int(101).to_bytes(2) + int(800).to_bytes(4) + int(1).to_bytes(1) + b"hola"
parsed_IP_packet = parse_packet(IP_packet_v1)
IP_packet_v2_str = create_packet(parsed_IP_packet)
IP_packet_v2 = IP_packet_v2_str

print(IP_packet_v1)
print(IP_packet_v2)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))