from datetime import datetime, timezone
import requests
import httpx as arequests

from modules import shared

def _request(verb, key, path, **kwargs):
  server = next((s for s in shared.config.servers if s.name == key), None)
  if server is None:
    raise ValueError(f'Non-existent server key {key}!')
  if path[0] == '/':
    path = path[1:]

  kwargs.setdefault('headers', {})
  kwargs.setdefault('cookies', {})
  if verb == 'HEAD':
    kwargs.setdefault('allow_redirects', False)

  kwargs['headers'].update(server.headers)
  kwargs['cookies'].update(server.cookies)

  url = server.url + path

  return verb, url, kwargs

def request(verb, key, path, **kwargs):
  verb, url, kwargs = _request(verb, key, path, **kwargs)
  return requests.request(verb, url, **kwargs)

async def arequest(verb, key, path, **kwargs):
  verb, url, kwargs = _request(verb, key, path, **kwargs)
  kwargs.setdefault('follow_redirects', kwargs.get('allow_redirects', False))
  cookies = kwargs.pop('cookies')
  kwargs.setdefault('timeout', (5.0, 600.0))
  timeout = kwargs.pop('timeout')
  async with arequests.AsyncClient(cookies=cookies, timeout=timeout) as client:
    return await client.request(verb, url, **kwargs)
