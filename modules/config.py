class Config:
  def __init__(self, data):
    self.cred = Credential(data['bot'])
    self.server = Server(data['server'])
    self.users = [int(id) for id in data['permitted_users']]

  def update(self, data):
    self.cred.update(data['bot'])
    self.server.update(data['server'])
    self.users[:] = [int(id) for id in data['permitted_users']]

class Credential:
  def __init__(self, data):
    self.update(data)

  def update(self, data):
    self.id = data['id']
    self.token = data['token']

class Server:
  def __init__(self, data):
    self.update(data)

  def update(self, data):
    self.key = data['template']

__all__ = (
  Config,
)
