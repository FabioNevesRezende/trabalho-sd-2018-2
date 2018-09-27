import pexpect
import random
import os
from concurrent import futures

class TestCliente:
  @classmethod
  def setup_class(self):
    self.clients = 10
    self.server  = pexpect.spawn('python3 servidor.py')
    self.itens   = [1, 2, 3, 4, 5]

  '''
    Testes CRUD OK
  '''  
  def crud_ok(self, process_id = None):
    client = pexpect.spawn('python3 cliente.py')

    p_id    = 'value-ne'
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

    p_id    = 'value-ne'
    rand_id = 2
    regex   = r'NOk'

    if process_id:
      rand_id = random.randint(3, 999999999)
      p_id    = process_id

    client.sendline('create {} {}'.format(rand_id, p_id))
    assert 0 == client.expect(r'[^N]Ok') 
    
    client.sendline('\ncreate {} {}'.format(rand_id, p_id))
    assert 0 == client.expect(regex + ' - Chave existente')

    rand_id += 1

    client.sendline('\nread {}'.format(rand_id))
    regex  += ' - Chave inexistente' 
    assert 0 == client.expect(regex)

    client.sendline('\nupdate {} {}'.format(rand_id, p_id))
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

    for i in range(rand_id + 1, rand_id + 1001):
      client.sendline('read {}'.format(i - 1))
      client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
      v = int(client.match.group(1).decode())
      client.sendline('\r\ncreate {} {}\r\n'.format(i, v + 1))

    client.sendline('read {}'.format(i))
    client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
    v = int(client.match.group(1).decode())
    assert v == 1001
  
  # def start_server(self):
    # return pexpect.spawn('python3 servidor.py')

  def recovery(self):
    self.clear_log()

    client = pexpect.spawn('python3 cliente.py')
    server = pexpect.spawn('python3 servidor.py')

    for idx, item in enumerate([1, 2, 3, 4, 5], 0):
      client.sendline('\r\ncreate {} {}\r\n'.format(idx, item))
      assert 0 == client.expect(r'[^N]Ok')
    
    client.sendline('read')
    assert 0 == client.expect(self.readCommands(0))

    server.kill(9)

    server = pexpect.spawn('python3 servidor.py')

    for idx, item in enumerate([6,7,8,9,10], 5):
      client.sendline('\r\ncreate {} {}\r\n'.format(idx, item))
      assert 0 == client.expect(r'[^N]Ok')

    client.sendline('\r\nread')
    assert 0 == client.expect(self.readCommands(5))
  
  def readCommands(self, offset):
    if offset == 0:
      return r"Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5'\]"
    else:
      return r"Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5', 'Chave: 5, Valor: 6', 'Chave: 6, Valor: 7', 'Chave: 7, Valor: 8', 'Chave: 8, Valor: 9', 'Chave: 9, Valor: 10'\]"

  def clear_log(self):
    os.remove('logs.log')

  def all(self, process_id = None):
    # self.crud_ok(process_id)
    # self.crud_nok(process_id)
    self.clear_log()
    # self.execution(process_id)

  def call_and_pass_pid(self):
    self.all(os.getpid())

  def test_sequencitial(self):
    # self.all()
    # self.clear_log()
    self.recovery()

  # def test_concurrent(self):
    # with futures.ProcessPoolExecutor(max_workers=self.clients) as executor:
      # [executor.submit(self.call_and_pass_pid) for i in range(self.clients)]
  