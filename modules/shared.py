import yaml

from modules.config import Config

config = None
def load_config(file):
  global config
  c = yaml.load(open(file).read(), Loader=yaml.Loader)
  if config is None:
    config = Config(c)
  else:
    config.update(c)

load_config('config.yml')

__all__ = (
  config, load_config,
)
