import secrets
import string
import sys

def generate_password(pass_len: int=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(pass_len))

try:
    print(generate_password(sys.argv[1]))
except IndexError:
    print(generate_password())
