import pexpect

class TestCliente:
  @classmethod
  def setup_class(self):
    self.client = pexpect.spawn('python3 cliente.py')

  def teardown_method(self):
    self.client.sendline() # simula ENTER depois de cada test

  '''
    Testes CRUD OK
  '''  
  def test_create_new_item(self):
    self.client.sendline('create 1 cecilia')
    assert 0 == self.client.expect(r'[^N]Ok') # match somente Ok, e não NOk
    
  def test_read_new_item(self):
    self.client.sendline('read 1')
    assert 0 == self.client.expect(r'[^N]Ok - Item: Chave: 1, Valor: cecilia')

  def test_update_existing_item(self):
    self.client.sendline('update 1 gloria')
    assert 0 == self.client.expect(r'[^N]Ok')

  def test_read_updated_item(self):
    self.client.sendline('read 1')
    assert 0 == self.client.expect(r'[^N]Ok - Item: Chave: 1, Valor: gloria')

  def test_delete_existing_item(self):
    self.client.sendline('delete 1')
    assert 0 == self.client.expect(r'[^N]Ok')
    
  '''
    Testes CRUD NOK
  '''  
  def test_create_new_item_nok(self):
    self.client.sendline('create 2 bruno')
    assert 0 == self.client.expect(r'[^N]Ok') 
    
  def test_create_non_existing_item_nok(self):
    self.client.sendline('create 2 bruno')
    assert 0 == self.client.expect(r'NOk - Chave existente')

  def test_read_non_existing_item_nok(self):
    self.client.sendline('read 3')
    assert 0 == self.client.expect(r'NOk - Chave inexistente')

  def test_update_non_existing_item_nok(self):
    self.client.sendline('update 3 joao')
    assert 0 == self.client.expect(r'NOk - Chave inexistente')    
  
  def test_delete_non_existing_item(self):
    self.client.sendline('delete 3')
    assert 0 == self.client.expect(r'NOk - Chave inexistente')    