import pexpect
import random
import string
from threading import *

class TesteConcurrency:
  @classmethod
  def setup_class(self):
    self.client_instances = []
    self.client_amount = 100
    self.test_startServer()
    
  @classmethod
  def test_startServer(self):
    self.server = pexpect.spawn('python3 servidor.py')
    for i in range(0, self.client_amount):
      c = pexpect.spawn('python3 cliente.py')
      client_instances.append(c)
        
  # gera uma string aleatória de tamanho <size>
  @classmethod    
  def str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

  @classmethod
  def client_send_data(c):
    c.sendline('create ' + str(random.randint(0,999999999)) + ' ' + self.str_generator(random.randint(0,3000)) + '\r\n')
    
  @classmethod   
  def client_thread(c):
    rolls = 10000000
    while rolls > 0:
        self.client_send_data(c)
        rolls -= 1
        
  # inicia uma thread para cada cliente enviar dados de forma concorrente
  def testa(self):
      for c in self.client_instances:
        fio = Thread(target=self.client_thread, args=(c,))
        fio.daemon = True
        fio.start()
        
        
            
      
  
        
