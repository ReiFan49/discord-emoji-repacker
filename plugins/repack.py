import sys
import json
import traceback
import asyncio
from io import BytesIO
from time import time, sleep
from typing import Optional
from zipfile import ZipFile

import requests
from discord import (
  app_commands as slash, Interaction,
  Attachment, ChannelType,
  NotFound, HTTPException
)
from discord.ext.commands import Bot, Cog, Context, command, dm_only

from modules import shared

MAXIMUM_EMOTE_BASE = 50

async def check_template(i: Interaction) -> bool:
  i.extras['skel'] = None
  if shared.config.server.key is None:
    return False

  try:
    skel = await i.client.fetch_template(shared.config.server.key)
  except (NotFound, HTTPException):
    return False

  i.extras['skel'] = skel
  return True

def ensure_interact_zip(i: Interaction) -> bool:
  map_data = dict((d['name'], d['value']) for d in i.data['options'])
  if map_data.get('data') is None:
    return False
  attachment = i.data['resolved']['attachments'][map_data['data']]
  return ensure_zip(attachment['content_type'])

def ensure_zip(content_type: str) -> bool:
  return content_type == 'application/zip'

class Packer(Cog, name='Emoji Repacker'):
  def __init__(self, bot: Bot) -> None:
    self.bot = bot

  @slash.command(
    name='recreate',
    description='Recreate emoji server based on given server',
  )
  @slash.describe(
    name='Server name to override from metadata.json',
    data='Server content as described on Documentation',
  )
  @dm_only()
  @slash.check(ensure_interact_zip)
  @slash.check(check_template)
  @slash.default_permissions()
  async def recreate(
    self, i: Interaction,
    name: Optional[str],
    data: Attachment,
  ):
    await self._process_recreate(i=i, name=name, url=data.url)

  async def _process_recreate(
    self, i: Interaction,
    name: Optional[str],
    url: str,
  ):
    b = await self._process_recreate_fetch_data(i, url)
    if not b:
      return False

    with ZipFile(b) as zio:
      await self._process_recreate_read_contents(i, zio, name=name)

  async def _process_recreate_fetch_data(self, i, url):
    await i.response.defer(ephemeral=True, thinking=True)
    b = BytesIO()
    try:
      r = requests.get(url)
      if not ensure_zip(r.headers['Content-Type']):
        raise TypeError(f"Expects application/zip, given {r.headers['Content-Type']}")
      b.write(r.content)
    except:
      await i.edit_original_response(content='recreate failed on fetching resources.')
      return False

    b.seek(0)
    return b

  async def _process_recreate_read_contents(self, i, zio, name: str = ''):
    i.extras['server'] = None

    server_meta = json.load(zio.open('metadata.json'))
    emotes      = json.load(zio.open('emotes.json'))
    for emote in emotes:
      fn = f"e/{emote['id']}.{emote['ext']}"
      emote['data'] = zio.read(fn) if fn in zio.namelist() else None

    server_icon = None
    if not name:
      name = server_meta['name']
    if 'icon.png' in zio.namelist():
      server_icon = zio.read('icon.png')

    async def add_emoji_to_server(server, emote):
      try:
        await server.create_custom_emoji(
          name=emote['name'],
          image=emote['data'],
          reason='via Emoji Repacker',
        )
      except HTTPException as e:
        print(str(e))

    def wait_for_join(server):
      def check(member):
        return member.guild == server

    async def baton_pass_and_leave(server, user):
      await server.edit(owner=user)
      await server.leave()

    async def assign_on_join_get(server):
      user = await self.bot.wait_for('member_join', check=wait_for_join(server))
      if user is None:
        raise Exception('failed')

      top_role = server.roles[-1]
      await user.add_roles(top_role, reason='superuser invite used')
      return user

    async def assign_and_leave_on_join(server):
      user = await assign_on_join_get(server)

      await baton_pass_and_leave(server, user)
      if i.extras['server'] == server:
        i.extras['server'] = None

    async def assign_and_bg_on_join(server, overflow_emotes):
      user = None

      async def assign_user():
        nonlocal user
        user = await assign_on_join_get(server)

      async def consume_emotes():
        for emote in overflow_emotes:
          await add_emoji_to_server(server, emote)

      async def wait_for_everything():
        nonlocal user

        try:
          await asyncio.gather(
            assign_user(),
            consume_emotes(),
          )
          await baton_pass_and_leave(server, user)
        except asyncio.CancelledError:
          pass
        except Exception as e:
          print(type(e).__name__, ": ", str(e), ", occured on", task.get_name(), file=sys.stderr)

      i.extras['server'] = None

      bg = self.bot.loop.create_task(
        wait_for_everything(),
        name=f"{server.id}:bg-emote-extra-process",
      )

    await i.edit_original_response(content='Preparing the server...')

    try:
      static_emotes , animated_emotes = [], []
      for emote in emotes:
        if emote['data'] is None:
          continue
        (static_emotes, animated_emotes)[emote['animated']].append(emote)

      for cue in range(0, max(len(static_emotes), len(animated_emotes)), MAXIMUM_EMOTE_BASE):
        emote_chunks = sorted(
          static_emotes[cue:cue + MAXIMUM_EMOTE_BASE] +
          animated_emotes[cue:cue + MAXIMUM_EMOTE_BASE],
          key=lambda emote: int(emote['id'], 10),
        )
        if not emote_chunks:
          break

        server = i.extras['server'] = await i.extras['skel'].create_guild(
          name=name, icon=server_icon,
        )
        text_channels = sorted(
          (c for c in await server.fetch_channels() if c.type == ChannelType.text),
          key=lambda c: (c.position, c.id),
        )

        top_channel = text_channels[0]
        server_invite = await top_channel.create_invite(reason='via Emoji Repacker')
        print(server_invite.url)

        for n, emote in zip(range(len(emote_chunks[:50])), emote_chunks[:50]):
          await add_emoji_to_server(server, emote)
          await i.edit_original_response(content=f"Uploaded {n+1}/{len(emote_chunks)} emotes..")

        if len(emote_chunks) <= 50:
          await i.edit_original_response(content=server_invite.url)
          await assign_and_leave_on_join(server)
        else:
          await i.edit_original_response(content=f"Due to Discord Rate Limiting concern, emote migration takes a background queue.")
          await i.followup.send(content=server_invite.url)
          await assign_and_bg_on_join(server, emote_chunks[50:])
    except Exception as e:
      raise e
    else:
      await i.edit_original_response(content=f'{name} server repacked.')
    finally:
      if i.extras['server'] is not None:
        await i.extras['server'].delete()

  @recreate.error
  async def recreate_error(self, i, error):
    if not i.response.is_done():
      await i.response.defer(ephemeral=True, thinking=True)

    print(type(error).__name__, str(error))
    for li in traceback.format_exception(type(error), error, error.__traceback__):
      print('', li.strip())

    await i.edit_original_response(content='Unknown error occurred.')
