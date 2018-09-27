import pexpect
import random

class TestCliente:
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

    client.sendline('create {} 1\n'.format(rand_id))
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

  def clear_log(self):
    pexpect.spawn('rm logs.log')

  def all(self, process_id = None):
    # self.crud_ok(process_id)
    # self.crud_nok(process_id)
    # self.clear_log()
    self.execution(process_id)

  def test_sequencitial(self):
    self.all()
