import pexpect

class TestRecovery:
  @classmethod
  def setup_class(self):
    pexpect.spawn('rm logs.log')
    self.items = [1, 2, 3, 4, 5]
    self.offset = 0
    # self.client.sendline()

  # def teardown_method(self):
    # self.client.sendline() # simula ENTER depois de cada test

  def test_Insert(self):
    self.startServer()
    for idx, item in enumerate(self.items, self.offset):
      self.client.sendline('\r\ncreate {} {}\r\n'.format(idx, item))
      assert 0 == self.client.expect(r'[^N]Ok')

  '''
  Inicia o servidor e cliente
  '''
  @classmethod
  def startServer(self):
    self.server = pexpect.spawn('python3 servidor.py')
    self.client = pexpect.spawn('python3 cliente.py')

  '''
  Reinicia o servidor e cliente
  '''
  @classmethod
  def rebootServer(self):
      self.server.kill(9)
      self.client.kill(9)

  '''
  Valida recuperação por log
  '''
  def test_recoveryData(self):
    self.client.sendline('read')
    assert 0 == self.client.expect(self.readCommands())
    
  def test_currentData(self):
    self.items = [6,7,8,9,10]
    self.offset = 5
    self.test_Insert()
    self.client.sendline('\r\nread')
    assert 0 == self.client.expect(self.readCommands())

  def readCommands(self):
    if self.offset == 0:
      return "Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5'\]"
    else:
      return "Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5', 'Chave: 5, Valor: 6', 'Chave: 6, Valor: 7', 'Chave: 7, Valor: 8', 'Chave: 8, Valor: 9', 'Chave: 9, Valor: 10'\]"

# "Ok - Itens: \['Chave: 0, Valor: 1', 'Chave: 1, Valor: 2', 'Chave: 2, Valor: 3', 'Chave: 3, Valor: 4', 'Chave: 4, Valor: 5'\]"
