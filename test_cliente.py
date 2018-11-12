import pexpect
import random
import os
from concurrent import futures
import time
import yaml

configs               = yaml.load(open('configs.yml', 'r'))
DB_PARAMS           = configs['DB_PARAMS']

class TestCliente:
  @classmethod
  def setup_class(self):
    self.clients = 10

  '''
    Testes CRUD OK
  '''  
  def crud_ok(self, process_id = None):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'ne'
    rand_id = 1
    regex   = r'[^N]Ok'

    if process_id:
      rand_id = random.randint(3, 999999999)
      p_id    = process_id
      
    client.sendline('create {} old-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex) # match somente Ok, e não NOk

    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: old-{}'.format(rand_id, p_id))

    client.sendline('\nupdate {} new-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex)
    
    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: new-{}'.format(rand_id, p_id))

    client.sendline('\ndelete {}'.format(rand_id))
    assert 0 == client.expect(r'[^N]Ok')

    client.kill(9)
    
  '''
    Testes CRUD NOK
  '''  
  def crud_nok(self, process_id = None):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'ne'
    rand_id = 2
    regex   = r'NOk'

    if process_id:
      rand_id = random.randint(3, 999999999)
      p_id    = process_id

    client.sendline('create {} value-{}'.format(rand_id, p_id))
    assert 0 == client.expect(r'[^N]Ok') 
    
    client.sendline('\ncreate {} value-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex + ' - Chave existente')

    rand_id += 1

    client.sendline('\nread {}'.format(rand_id))
    regex  += ' - Chave inexistente' 
    assert 0 == client.expect(regex)

    client.sendline('\nupdate {} value-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex)    
  
    client.sendline('\ndelete {}'.format(rand_id))
    assert 0 == client.expect(regex)

    client.kill(9)

  '''
    Teste iteração
  '''
  def execution(self, process_id = None):
    client  = pexpect.spawn('python3 cliente.py')
    rand_id = random.randint(3, 999999999) if process_id != None else 0

    client.sendline('create {} 1'.format(rand_id))
    client.sendline()
    client.sendline()

    # for i in range(rand_id + 1, rand_id + 11):
    for i in range(rand_id + 1, rand_id + 1001):
      client.sendline('read {}'.format(i - 1))
      client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
      v = int(client.match.group(1).decode())
      client.sendline('\r\ncreate {} {}\r\n'.format(i, v + 1))

    client.sendline('read {}'.format(i))
    client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
    v = int(client.match.group(1).decode())
    # assert v == 11
    assert v == 1001
  
  @classmethod
  def start_communicaton(self):
    self.server = pexpect.spawn('python3 servidor.py')
    return pexpect.spawn('python3 cliente.py')

  @classmethod
  def reset_communicaton(self, client):
    self.server.kill(9)
    client.kill(9)

  def recovery(self, process_id = None):
    client = TestCliente.start_communicaton()

    p_id  = process_id if process_id != None else 'ne'
    regex = r'[^N]Ok'

    client = pexpect.spawn('python3 cliente.py')

    if process_id == None:
      client.sendline('read\r\n')
      assert 0 == client.expect('NOk') # log limpo, servidor novo. banco vazio

    for _ in range(5):
      rand_id = random.randint(3, 999999999)
      client.sendline('\r\ncreate {} value-{}\r\n'.format(rand_id, p_id))
      assert 0 == client.expect(regex)
    
    # client.sendline('read\r\n')
    # assert 0 == client.expect(regex)
    # assert 0 == client.expect(self.readCommands(0))

    TestCliente.reset_communicaton(client)
    client = TestCliente.start_communicaton()

    client.sendline('\r\nread')
    assert 0 == client.expect(regex)

    for _ in range(5):
      rand_id = random.randint(3, 999999999)
      client.sendline('\r\ncreate {} value-{}\r\n'.format(rand_id, p_id))
      assert 0 == client.expect(regex)

    client.sendline('\r\nread')
    assert 0 == client.expect(regex)
    # assert 0 == client.expect(self.readCommands(5))
  
  # def readCommands(self, offset):
  #   if offset == 0:
  #     return r"Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5'\]"
  #   else:
  #     return r"Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5', 'Chave: 5, Valor: 6', 'Chave: 6, Valor: 7', 'Chave: 7, Valor: 8', 'Chave: 8, Valor: 9', 'Chave: 9, Valor: 10'\]"

  def clear_log(self):
    try:
      os.remove('logs.log')
    except FileNotFoundError:
      pass

  def run_all_but_recovery(self, process_id = None):
    # self.crud_maxLenght(process_id)
    # self.crudId(0)
    self.createInRange()

  def call_and_pass_pid(self):
    self.run_all_but_recovery(os.getpid())

  def test_cruds(self):
    self.run_all_but_recovery()

  # def test_concurrent(self):
  #   time.sleep(30)
  #   self.clear_log()

  #   self.first_call = True
  #   with futures.ProcessPoolExecutor(max_workers=self.clients) as executor:
  #     [executor.submit(self.call_and_pass_pid) for i in range(self.clients)]
  

  

  def crudId(self, id):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'ne'
    rand_id = id
    regex   = r'[^N]Ok'

    
    client.sendline('create {} old-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex) # match somente Ok, e não NOk

    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: old-{}'.format(rand_id, p_id))

    client.sendline('\nupdate {} new-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex)
    
    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: new-{}'.format(rand_id, p_id))

    client.sendline('\ndelete {}'.format(rand_id))
    assert 0 == client.expect(r'[^N]Ok')

    client.kill(9)
  
  def crud_maxLenght(self, process_id = None):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'ne'
    rand_id = self.le_parametros_banco()
    regex   = r'[^N]Ok'

    
    client.sendline('create {} old-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex) # match somente Ok, e não NOk

    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: old-{}'.format(rand_id, p_id))

    client.sendline('\nupdate {} new-{}'.format(rand_id, p_id))
    assert 0 == client.expect(regex)
    
    client.sendline('\nread {}'.format(rand_id))
    assert 0 == client.expect(regex + ' - Item: Chave: {}, Valor: new-{}'.format(rand_id, p_id))

    client.sendline('\ndelete {}'.format(rand_id))
    assert 0 == client.expect(r'[^N]Ok')

    client.kill(9)

  def createInRange(self):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'ne'
    regex   = r'[^N]Ok'

    servidores = self.servidores()

    client.sendline('create {} old-{}\n'.format(servidores[0], p_id))
    # client.sendline('create {} old-{}\n\n\n\n\n'.format(servidores[1], p_id))
    # client.sendline('create {} old-{}\n\n\n\n\n'.format(servidores[2], p_id))
    # client.sendline('create {} old-{}\n\n\n\n\n'.format(servidores[3], p_id))

    # for servidor in self.servidores():
      # client.sendline('create {} old-{}\n\n\n\n\n'.format(servidor, p_id))
        #assert 0 == client.expect(regex) # match somente Ok, e não NOk





  def le_parametros_banco(self):
    dbparams = yaml.load(open(DB_PARAMS, 'r'))
    max_key  = 2 ** int(dbparams['bits']) - 1
    return max_key

  def servidores(self):
    servidores = open('./servidores.txt', 'r')
    listaServidor = []
    for linha in servidores.readlines():
        listaServidor.append(int(linha))
    return listaServidor