import pexpect
import random
import threading
from concurrent import futures

client_amount = 10

def create_item():
  client = pexpect.spawn('python3 cliente.py')
  client.sendline('create {} vla\n\n'.format(random.randint(0, 222222)))
  client.expect('Ok')

# inicia uma thread para cada cliente enviar dados de forma concorrente
def main():
  with futures.ProcessPoolExecutor(max_workers=client_amount) as executor:
    [executor.submit(create_item) for i in range(client_amount)]

if __name__ == '__main__':
  main()