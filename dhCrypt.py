import configparser
from random import randint


class DiffieHellmanCrypt(object):
    def __init__(self, first_public_key, second_public_key, private_key):
        self.first_public_key = first_public_key
        self.second_public_key = second_public_key
        self.private_key = private_key
        self.full_key = None

    def generate_partial_key(self):
        return self.first_public_key ** self.private_key % self.second_public_key

    def generate_full_key(self, partial_key_r):
        self.full_key = partial_key_r ** self.private_key % self.second_public_key
        return self.full_key

    def encrypt(self, to_encrypt_message):
        encrypted_message = ""
        for i in to_encrypt_message:
            encrypted_message += chr(ord(i) + self.full_key)
        return encrypted_message

    def decrypt(self, encrypted_message):
        decrypted_message = ""
        for i in encrypted_message:
            decrypted_message += chr(ord(i) - self.full_key)
        return decrypted_message


def get_configparser():
    return configparser.ConfigParser()


def set_keys(parser, path):
    config = parser
    config.add_section("Keys")
    public_keys = [str(randint(1000, 10000)) for i in range(100)]
    private_keys = [str(randint(100000, 1000000)) for i in range(100)]
    config.set("Keys", "public", ",".join(public_keys))
    config.set("Keys", "private", ",".join(private_keys))

    with open(path, "w") as config_file:
        config.write(config_file)
    config_file.close()


def get_keys(parser, path):
    config = parser
    config.read(path)
    public_keys_list = config["Keys"]["public"].split(",")
    private_keys_list = config["Keys"]["private"].split(",")

    return public_keys_list, private_keys_list
