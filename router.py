import sys
import socket

rr_ips = {}


def IP_string_to_bytes(ip: str):
    ip_n = ip.split(".")
    ip_r = int(ip_n[0]).to_bytes(1) + int(ip_n[1]).to_bytes(1) + int(ip_n[2]).to_bytes(1) + int(ip_n[3]).to_bytes(1)

    return ip_r


def parse_packet(IP_packet: bytes):
    a = IP_packet[0]
    b = IP_packet[1]
    c = IP_packet[2]
    d = IP_packet[3]
    ip = f"{a}.{b}.{c}.{d}"
    puerto = int.from_bytes(IP_packet[4:6])
    ttl = IP_packet[6]

    id = int.from_bytes(IP_packet[7:9])
    offset = int.from_bytes(IP_packet[9:11])
    tamanno = int.from_bytes(IP_packet[11:15])
    flag = IP_packet[15]

    message = IP_packet[16:]
    return {"address":(ip,puerto),"message":message,"ttl":ttl,"id":id,"offset":offset,"tamanno":tamanno,"flag":flag}

def create_packet(parse_IP_packet):
    ip = IP_string_to_bytes(parse_IP_packet["address"][0])
    puerto = parse_IP_packet["address"][1].to_bytes(2)
    ttl = parse_IP_packet["ttl"].to_bytes(1)

    id = parse_IP_packet["id"].to_bytes(2)
    offset = parse_IP_packet["offset"].to_bytes(2)
    tamanno = parse_IP_packet["tamanno"].to_bytes(4)
    flag = parse_IP_packet["flag"].to_bytes(1)

    message = parse_IP_packet["message"]
    return ip+puerto+ttl+id+offset+tamanno+flag+message

def check_routes(routes_file_name: str, destination_address: tuple[str,int]) -> tuple[str,int]:
    global rr_ips
    re_address = None
    count = 0
    mtu = None
    prio = 0
    with open(routes_file_name,"r") as file:
        for line in file:
            args = line.strip().split(" ")

            if not count in rr_ips:
                rr_ips[count] = 0

            n = int(args[0].split("/")[1])

            mask = (((0xFFFFFFFF) << (32-n)) & 0xFFFFFFFF).to_bytes(4)

            des_check = bytes(a & b for a,b in zip(IP_string_to_bytes(destination_address[0]),mask)) 
            rot_check = bytes(a & b for a,b in zip(IP_string_to_bytes(args[0].split("/")[0]),mask))  

            if des_check == rot_check and prio <= n:
                puerto_ini = int(args[1])
                puerto_fin = int(args[2])
                if puerto_ini <= destination_address[1] and destination_address[1] <= puerto_fin:
                    if re_address == None:
                        re_address =(args[3],int(args[4]))
                        ip_ruta = count
                        prio = n
                        mtu = int(args[5])
                    else:
                        if n > prio:
                            re_address =(args[3],int(args[4]))
                            ip_ruta = count
                            prio = n
                            mtu = int(args[5])
                        elif n == prio:
                            re_address = (args[3], int(args[4]))
                            ip_ruta = count
                            prio = n
                            mtu = int(args[5])
            count += 1
    print(rr_ips)
    if re_address != None:
        rr_ips[ip_ruta] += 1
    return re_address,mtu



def fragment_IP_packet(IP_packet,MTU):
    tam_headers = 16
    tam_message = len(IP_packet["message"])

    if tam_headers + tam_message > MTU:
        new_message = IP_packet["message"][:MTU-tam_headers]
        next_message = IP_packet["message"][MTU-tam_headers:]

        new_segment = IP_packet.copy()
        next_segment = IP_packet.copy()

        new_segment["flag"] = 1
        new_segment["message"] = new_message
        #new_segment["tamanno"] = len(new_message)

        next_segment["offset"] += len(new_message)
        next_segment["message"] = next_message
        #next_segment["tamanno"] = len(next_message)

        return [new_segment] + fragment_IP_packet(next_segment,MTU)
    else:
        return [IP_packet]
    
def reassemble_IP_packet(fragment_list):
    final_segment = fragment_list[0].copy()
    final_segment["offset"] = 0
    final_segment["flag"] = 1
    final_segment["message"] = b''
    #final_segment["tamanno"] = 0
    count = 0
    maxx = len(fragment_list)
    while count < maxx:

        print(final_segment)

        if fragment_list[count]["offset"] == len(final_segment["message"]):

            final_segment["message"] += fragment_list[count]["message"]
            final_segment["flag"] = fragment_list[count]["flag"]
            #final_segment["offset"] += len(fragment_list[count]["message"])
            #final_segment["tamanno"] += fragment_list[count]["tamanno"]
            count = 0
            continue

        count += 1

    if final_segment["flag"] == 0:
        return final_segment
    else:
        return None


if __name__ == "__main__":

    reassemple_id = {}
    reassembled_tam = {}

    router_IP = sys.argv[1]
    router_puerto = int(sys.argv[2])
    router_rutas = sys.argv[3]
    #print(f"IP: {router_IP}, Puerto: {router_puerto}, Rutas: {router_rutas}")

    router_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    address = (router_IP,router_puerto)
    router_socket.bind(address)

    while True:
        message, new_address = router_socket.recvfrom(1028)
        segment = parse_packet(message)

        if segment["ttl"] <= 0:
            print(f"Se recibió paquete {segment['message']} con TTL 0")
            continue

        if segment["address"] == address:

            if segment["id"] in reassemple_id:
                reassemple_id[segment["id"]].append(segment)
                reassembled_tam[segment["id"]] += len(segment["message"])
            else:
                reassemple_id[segment["id"]] = [segment]
                reassembled_tam[segment["id"]] = len(segment["message"])

            if reassembled_tam[segment["id"]] >= segment["tamanno"]: 
                reassembled = reassemble_IP_packet(reassemple_id[segment["id"]])
            else:
                reassembled = None

            if reassembled != None:
                print(reassembled["message"].decode())
    
        else:
            next_address,next_mtu = check_routes(router_rutas,segment["address"])
            if next_address:
                segment["ttl"] -= 1

                messages = fragment_IP_packet(segment,next_mtu)

                for m in messages:
                    print(f"redirigiendo paquete {m} con destino final {segment["address"]} desde {address} hacia {next_address}")
                    router_socket.sendto(create_packet(m),next_address)
            else:
                print(f"No hay rutas hacia {segment["address"]} para paquete {segment["message"]}")
    