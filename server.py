import json
import logging
import signal
import time
import socket
from threading import Thread
import bcrypt
from fileManager import *
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


def ftp_command(n, home_dir):

    if n.isspace() or n == "":
        return n
    elif "wd" in n:
        return home_dir
    elif n == "help":
        return help_()
    elif n == "ls":
        return ls(home_dir)
    elif "crdir" in n:
        if len(n.split()) != 2:
            return "\033[31m" + 'Usage: crdir [dir_name]' + '\033[0m'
        else:
            return mkdir(os.path.join(home_dir, n.split()[1]))
    elif "dldir" in n:
        if len(n.split()) != 2:
            return "\033[31m" + 'Usage: dldir [dir_name]' + '\033[0m'
        else:
            return rmdir(os.path.join(home_dir, n.split()[1]))
    elif "dl" in n:
        if len(n.split()) != 2:
            return "\033[31m" + 'Usage: dl [file_name]' + '\033[0m'
        else:
            return rm(os.path.join(home_dir, n.split()[1]))
    elif "cd" in n:
        if len(n.split()) == 1:
            my_str = home_dir.replace('\\', ' ')
            if len(my_str.split()) != 1:
                new_str = my_str.split()[:-1]
                home_dir = "\\".join(new_str)
            return home_dir
        elif len(n.split()) > 2:
            return "\033[31m" + 'Usage: cd [dir_name]' + '\033[0m'
        else:
            home_dir = cd(n.split()[1], home_dir)
            return home_dir
    elif "create" in n:
        if len(n.split()) != 2:
            return "\033[31m" + 'Usage: create [file_name]' + '\033[0m'
        else:
            return touch(os.path.join(home_dir, n.split()[1]))
    elif "read" in n:
        if len(n.split()) != 2:
            return "\033[31m" + 'Usage: read [file_name]' + '\033[0m'
        else:
            return cat(os.path.join(home_dir, n.split()[1]))
    elif "write" in n:
        if len(n.split()) <= 2:
            return "\033[31m" + 'Usage: write [file_name][info]' + '\033[0m'
        else:
            return write(os.path.join(home_dir, n.split()[1]), ' '.join(n.split()[2:]))
    elif "rnm" in n:
        if len(n.split()) != 3:
            return "\033[31m" + 'Usage: rnm [file_name][new_file_name]' + '\033[0m'
        else:
            return rename(os.path.join(os.getcwd(), home_dir, n.split()[1]), os.path.join(os.getcwd(), home_dir, n.split()[2]))
    elif "copy" in n:
        if len(n.split()) != 3:
            return "\033[31m" + 'Usage: copy [file_name][dir_name]' + '\033[0m'
        else:
            if home_dir in os.path.join(os.getcwd(), home_dir, n.split()[1]):
                return cp(os.path.join(os.getcwd(), home_dir, n.split()[1]), n.split()[2], n.split()[1])
            else:
                if n.split()[2] == home_dir:
                    server_path = os.path.join(os.getcwd(), home_dir)
                else:
                    server_path = os.path.join(os.getcwd(), home_dir, n.split()[2])
                    if not os.path.exists(server_path):
                        return "\033[31m" + '[ERROR] Path doesnt exist' + '\033[0m'
                return cp(n.split()[1], server_path, os.path.basename(n.split()[1]))
    else:
        return f"\033[31m" + '[ERROR] Unknown command ' + "\"" + str(n) + "\"." + 'Try help' + '\033[0m'


def commands():
    n = ""
    while True:
        try:
            n = input("")
            if n.isspace() or n == "":
                continue
            elif n == "{exit}":
                break
            elif n == "cls":
                cls()
                continue
            elif n == "rdlog":
                read_log()
                continue
            elif n == "cllog":
                clear_log()
                continue
            elif n == "cldata":
                clear_data()
                continue
            elif n == "help":
                _help()
                continue
            elif "ipm" in n:
                if len(n.split()) != 2:
                    print(f"{BColors.FAIL}[ERROR] Usage: ipm [mode]{BColors.ENDC}")
                else:
                    ipm(n.split()[1])
                continue
            else:
                print("\033[31m" + ('[ERROR] Unknown command ' + "\""+str(n)+"\"."+'Try help') + '\033[0m')
                continue
        except:
            print("\033[31m" + ('[ERROR] Unknown command ' + "\""+str(n)+"\"."+'Try help') + '\033[0m')
            continue
    os.kill(os.getpid(), signal.SIGTERM)


def _help():
    print(f"{BColors.OKGREEN}\nCommands: ")
    print(f"{{exit}} - Exit from program")
    print("cls - Clear the console")
    print("rdlog - Read log file")
    print("cllog - Clear log file")
    print("ipm - Change ip mode. [ip, ipp]")
    print(f"cldata - Clear data file{BColors.ENDC}\n")
    return


def ipm(mode):
    global ip_only

    if mode == "ip":
        ip_only = True
        info = "Now server is working in IP only mode"
    elif mode == "ipp":
        ip_only = False
        info = "Now server is working in IP+PORT mode"
    else:
        return print(f"{BColors.FAIL}[ERROR] Wrong mode name! Try help{BColors.ENDC}")

    return print(f"{BColors.OKGREEN}[INFO] {info}{BColors.ENDC}")


def cls():
    return os.system('cls' if os.name == 'nt' else 'clear')


def clear_data():
    try:
        with open('data.json', 'w+', encoding='utf-8') as file:
            json.dump(dict(), file, ensure_ascii=False, indent=4)
        print(f"{BColors.OKGREEN}[INFO] Successfully cleaned data file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def clear_log():
    try:
        open('app.log', 'w').close()
        print(f"{BColors.OKGREEN}[INFO] Successfully cleaned log file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def read_log():
    try:
        with open('app.log') as fd:
            lines = fd.readlines()
        for line in lines:
            print(line.strip())
        print(f"{BColors.OKGREEN}[INFO] Ended reading log file{BColors.ENDC}")
    except:
        print(f"{BColors.FAIL}[ERROR] File does not exist{BColors.ENDC}")
    return


def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def check_password(data):
    return re.fullmatch(r'^((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*]))((.)(?!\3{3})){8,26}$', data)


def check_free_port(port, rais=True):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.listen(5)
        sock.close()
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.bind(('::1', port))
        sock.listen(5)
        sock.close()
    except socket.error as e:
        if rais:
            print(f"{BColors.WARNING}[WARNING] The server is already running on port {port} {BColors.ENDC}")
            logging.warning(f"[WARNING] The server is already running on port {port}")
        return False
        # if rais:
        #     raise RuntimeError(
        #         "The server is already running on port {0}".format(port))
    return True


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


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print(f"{BColors.OKGREEN}[NEW CONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has connected{BColors.ENDC}")
        logging.info(f"[NEW CONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has connected")
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(client, client_address):
    try:

        public_keys_list, private_keys_list = get_keys(get_configparser(), "serverKeys")
        random_public_index = randint(0, len(public_keys_list) - 1)
        random_private_index = randint(0, len(private_keys_list) - 1)

        server_public_key = public_keys_list[random_public_index]
        server_private_key = private_keys_list[random_private_index]

        client_public_key = client.recv(BUF_SIZ).decode("utf8")

        if client_public_key not in public_keys_list:
            client.send(bytes("Not certified", "utf8"))
            client.close()
        else:
            client.send(bytes(str(server_public_key), "utf8"))

        serv = DiffieHellmanCrypt(int(server_public_key), int(client_public_key), int(server_private_key))
        server_partial = serv.generate_partial_key()

        client_partial = client.recv(BUF_SIZ).decode("utf8")
        client.send(bytes(str(server_partial), "utf8"))

        full_key = serv.generate_full_key(int(client_partial))
        # print(full_key)

        user = {}
        with open("data.json", "r") as read_file:
            json_addresses = json.load(read_file)

        if ip_only:
            address = f"{client_address[0]}"
        else:
            address = f"{client_address[0]}:{client_address[1]}"

        if address in json_addresses:

            name = json_addresses[address]["name"]
            client.send(bytes(serv.encrypt(f"{BColors.OKGREEN}[INFO] Welcome back, {name}!{BColors.ENDC}"), "utf8"))
            # Вход в аккаунт
            try_count = 4
            while True:
                client.send(bytes(serv.encrypt("[PASSWORD] Type your password and press enter"), "utf8"))
                password = serv.decrypt(client.recv(BUF_SIZ).decode("utf8"))

                if bcrypt.checkpw(bytes(password, "utf8"), json_addresses[address]["password"].encode("utf8")):
                    client.send(bytes(serv.encrypt(f"{BColors.OKGREEN}[INFO] Successfully logging{BColors.ENDC}"), "utf8"))
                    break
                elif try_count == 0:
                    client.send(bytes(serv.encrypt(f"{BColors.FAIL}[ERROR] You have exceeded the number of allowed attempts to sign in{BColors.ENDC}"), "utf8"))
                    client.close()
                    break
                else:
                    client.send(bytes(serv.encrypt(f"{BColors.WARNING}[WARNING] Wrong password. Try again{BColors.ENDC}"), "utf8"))
                    try_count -= 1

        else:

            client.send(bytes(serv.encrypt("[NAME] Type your name and press enter"), "utf8"))
            name = serv.decrypt(client.recv(BUF_SIZ).decode("utf8"))
            user["name"] = name

            while True:
                client.send(bytes(serv.encrypt("[PASSWORD] Type your password and press enter"), "utf8"))
                password = serv.decrypt(client.recv(BUF_SIZ).decode("utf8"))
                if not check_password(password):
                    client.send(bytes(serv.encrypt(f"{BColors.WARNING}[WARNING] Your password must be at least 8 characters long, be of mixed case and also contain a digit or symbol.{BColors.ENDC}"), "utf8"))
                else:
                    break
            user["password"] = bcrypt.hashpw(bytes(password, "utf8"), bcrypt.gensalt()).decode('utf8')

            mkdir(name)
            user_path = os.path.join(os.path.abspath(os.path.dirname(name)), name)
            user["homeDIR"] = user_path

            addresses[address] = user
            json_addresses.update(addresses)

            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(json_addresses, f, ensure_ascii=False, indent=4)

        welcome = f'Hello {BColors.OKGREEN}{name}{BColors.ENDC}! If you ever want to quit, type {BColors.WARNING}{{exit}}{BColors.ENDC} to exit.'
        client.send(bytes(serv.encrypt(welcome), "utf8"))

        clients[client] = name
        paths[client] = name

        while True:
            enc_msg = client.recv(BUF_SIZ).decode("utf8")
            msg = serv.decrypt(enc_msg)
            if msg != "{exit}":
                home_dir = ftp_command(msg, paths[client])
                if name in home_dir:
                    paths[client] = home_dir
                client.send(bytes(serv.encrypt(home_dir), "utf8"))
                print(f"[MESSAGE {get_timestamp()}] {BColors.OKGREEN}{name}{BColors.ENDC}: {msg}")

                logging.info(f"[MESSAGE {client_address[0]} {get_timestamp()}] {name}: {msg}")
            else:
                client.send(bytes(serv.encrypt("{exit}"), "utf8"))
                client.close()

                print(f"{BColors.WARNING}[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected{BColors.ENDC}")
                logging.info(f"[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected")

                del clients[client]
                # broadcast(
                #     bytes(f"{BColors.WARNING}[LEFT {get_timestamp()}] {name} has left the chat{BColors.ENDC}", "utf8"))
                break
    except:
        client.close()
        print(f"{BColors.WARNING}[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected{BColors.ENDC}")
        logging.info(f"[NEW DISCONNECTION {get_timestamp()}] {client_address[0]}:{client_address[1]} has disconnected")
        return


def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


init()
addresses = {}
paths = {}
clients = {}
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

HOST = ''
PORT = set_port()
BUF_SIZ = 1024
ip_only = False

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if check_free_port(PORT):
    SERVER.bind((HOST, PORT))
else:
    SERVER.bind((HOST, 0))

if not os.path.exists('data.json'):
    with open('data.json', 'w+', encoding='utf-8') as f:
        json.dump(dict(), f, ensure_ascii=False, indent=4)

if not os.path.isfile("serverKeys"):
    set_keys(get_configparser(), "serverKeys")

if __name__ == "__main__":

    print(f"{BColors.OKGREEN}[STARTING] Server is starting...{BColors.ENDC}")
    logging.info("[STARTING] Server is starting...")

    if ip_only:
        ip_mode_info = "Working in IP only mode"
    else:
        ip_mode_info = "Working in IP+PORT mode"

    print(f"{BColors.WARNING}[IP MODE] {ip_mode_info}{BColors.ENDC}")
    logging.info(f"[IP MODE] {ip_mode_info}")

    print(f"[BINDING] Binding address {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")
    logging.info(f"[BINDING] Binding address {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")

    print(f"[LISTENING {get_timestamp()}] Server is listening on {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")
    logging.info(
        f"[LISTENING {get_timestamp()}] Server is listening on {SERVER.getsockname()[0]}:{SERVER.getsockname()[1]}")

    SERVER.listen(5)

    print("[WAITING] Waiting for connection...")
    logging.info("[WAITING] Waiting for connection...")

    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    MAIN_THREAD = Thread(target=commands)
    MAIN_THREAD.start()
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    MAIN_THREAD.join()
    SERVER.close()
