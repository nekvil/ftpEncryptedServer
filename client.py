import os
from socket import *
from threading import Thread
import re
from colorama import init
from dhCrypt import *


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_port():
    while True:
        port = input("[SET PORT] - ")
        if len(port) <= 5 and port.isdigit():
            port = int(port)
            break
        elif not port:
            port = 9090
            break
        else:
            print("[ERROR] Invalid port name")
    return port


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def set_host():
    while True:
        host = input("[SET HOST] - ")
        if not host:
            host = 'localhost'
            break
        elif is_valid_hostname(host):
            break
        else:
            print("[ERROR] Invalid host name")

    return host


def receive():
    while True:
        enc_msg = client_socket.recv(BUF_SIZ).decode("utf8")
        msg = CLIENT.decrypt(enc_msg)
        if msg == "{exit}":
            client_socket.close()
            break
        if not msg:
            break
        # print("\n"+"Encrypted message: "+enc_msg+"\n")
        print(msg)


def send():
    while True:
        try:
            msg = input("")
            client_socket.send(bytes(CLIENT.encrypt(msg), "utf8"))
            if msg == "{exit}":
                break
        except:
            client_socket.close()
            break


if not os.path.isfile("clientKeys"):
    set_keys(get_configparser(), "clientKeys")

init()

HOST = set_host()
PORT = set_port()

BUF_SIZ = 1024
ADDRESS = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDRESS)

public_keys_list, private_keys_list = get_keys(get_configparser(), "clientKeys")
random_public_index = randint(0, len(public_keys_list) - 1)
random_private_index = randint(0, len(private_keys_list) - 1)

# certificate public keys: 7885,3293,1422,6623,6051,1231,8665,4745,1993,1032,2329,4806,2803,7421,2996,2154,5065,2479,
# 9038,4900,5302,2509,4885,6767,9932,2037,8720,5649,2663,9107,1884,6563,3495,7206,5836,6834,9152,8405,9100,7503,1441,
# 1923,9098,8279,5079,3903,8175,4002,5096,7324,3511,2024,3345,4170,6317,2382,2978,5239,4123,9887,2464,5371,1422,9910,
# 9855,8921,4030,3526,1876,6049,1210,6058,5593,9687,9683,1312,7117,3841,9158,1512,7299,8020,7869,7321,2716,3224,7970,
# 6892,8478,2103,5093,9147,5792,9348,4590,4515,5279,7740,3501,9026

clientPublicKEY = 7885
clientPrivateKEY = private_keys_list[random_private_index]

client_socket.send(bytes(str(clientPublicKEY), "utf8"))
serverPublicKEY = client_socket.recv(BUF_SIZ).decode("utf8")

if serverPublicKEY == "Not certified":
    print(f"{BColors.FAIL}[ACCESS DENIED] Your public key isn't certified on the server{BColors.ENDC}")
else:
    print(f"{BColors.OKGREEN}[ACCESS ALLOWED] Your public key is certified on the server{BColors.ENDC}")
    CLIENT = DiffieHellmanCrypt(int(serverPublicKEY), int(clientPublicKEY), int(clientPrivateKEY))
    client_partial = CLIENT.generate_partial_key()

    client_socket.send(bytes(str(client_partial), "utf8"))
    server_partial = client_socket.recv(BUF_SIZ).decode("utf8")

    fullKey = CLIENT.generate_full_key(int(server_partial))
    # print(fullKey)

    receive_thread = Thread(target=receive)
    send_thread = Thread(target=send)
    receive_thread.start()
    send_thread.start()
    receive_thread.join()
    send_thread.join()
