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
    
  def test_read_existing_item(self):
    self.client.sendline('read 1')
    assert 0 == self.client.expect(r'[^N]Ok')

  def test_update_existing_item(self):
    self.client.sendline('update 1 gloria')
    assert 0 == self.client.expect(r'[^N]Ok')

  def test_delete_existing_item(self):
    self.client.sendline('delete 1')
    assert 0 == self.client.expect(r'[^N]Ok')
    