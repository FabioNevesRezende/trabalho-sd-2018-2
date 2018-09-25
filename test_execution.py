import pexpect

class TestExecution:
  @classmethod
  def setup_class(self):
    self.client = pexpect.spawn('python3 cliente.py')

  def teardown_method(self):
    self.client.sendline() # simula ENTER depois de cada test

  '''
    Teste iteração
  '''
  def test_execution(self):
      self.client.sendline('create 0 1\r\n')
      for i in range(1,1001):
        self.client.sendline('read '+ str(i-1))
        self.client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
        v = int(self.client.match.group(1).decode())
        self.client.sendline('\r\ncreate {} {}\r\n'.format(i,v+1))

      self.client.sendline('read '+ str(i))
      self.client.expect(r'Ok - Item: Chave: \d*, Valor: (\d*)')
      v = int(self.client.match.group(1).decode())
      assert v == 1001