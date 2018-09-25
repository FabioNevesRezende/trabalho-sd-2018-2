import pexpect

class TestRecovery:
  @classmethod
  def setup_class(self):
    # self.server = pexpect.spawn('python3 servidor.py')
    # self.client = pexpect.spawn('python3 cliente.py')
    self.test_startServer()
    self.items = [1,2,3,4,5]

  def teardown_method(self):
    self.client.sendline() # simula ENTER depois de cada test

  '''
    Teste interação
  '''
  def test_Insert(self):
    for i in range(0,len(self.items)):
        self.client.sendline('create {} {}'.format(i,self.items[i]))
        self.client.sendline()
        self.client.sendline()
    assert True
'''
Inicia o servidor e cliente
'''
  @classmethod
  def test_startServer(self):
    self.server = pexpect.spawn('python3 servidor.py')
    self.client = pexpect.spawn('python3 cliente.py')

'''
Reinicia o servidor e cliente
'''
  def test_RebootServer(self):
      self.server.kill(9)
      self.client.kill(9)
      self.test_startServer()

'''
Valida recuperação por log
'''      
  def test_readCommands(self):
      msg = r'[^N]Ok - Itens: ['
      for i in range(0, len(self.items)):
          msg += '\'Chave: {}, Valor: {}\''
          if i==len(self.items)-1:
              msg += ']'
          else:
              msg += ', '
      assert == self.client.expect(msg)   