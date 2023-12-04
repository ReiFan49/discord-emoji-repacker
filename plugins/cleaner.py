import re
from time import time
from discord import (
  app_commands as slash, Interaction,
  ChannelType,
  HTTPException, NotFound
)
from discord.ext.commands import Bot, Cog, Context, command, dm_only

from modules import shared

INVITE_REGEX = re.compile(r'(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?')
MESSAGE_PAST_TIME = 86400
CACHE_TIMEOUT = 3600 * 2

async def fetch_invites(client, *codes):
  out = {}
  for c in codes:
    try:
      i = await client.fetch_invite(c)
      out[c] = i
    except (HTTPException, NotFound):
      out[c] = None

  return out

class Startup(Cog, name='DM Cleaner'):
  def __init__(self, bot: Bot) -> None:
    self.bot = bot
    self.dm_cache = {}

  @Cog.listener('on_message')
  async def cleanup_dms(self, msg):
    if msg.channel.type != ChannelType.private:
      return

    ctime = time()

    if msg.author.id in self.dm_cache and ctime - self.dm_cache[msg.author_id] <= CACHE_TIMEOUT:
      return

    self.dm_cache[msg.author.id] = ctime
    async for cmsg in msg.channel.history():
      if cmsg.author.id != self.bot.application_id:
        continue

      codes = INVITE_REGEX.findall(cmsg.content)
      invites = await fetch_invites(self.bot, *codes)

      # There should be no interaction remnants here.
      if cmsg.flags.value & 128 and ctime - cmsg.created_at.timestamp() >= MESSAGE_PAST_TIME:
        print(cmsg.id, 'expired interaction')
        await cmsg.delete()
      # - ALL INVITES are FAILED
      # - INVITE COUNT on given message is STRICTLY 1
      # - message is only consisting of an invite without others.
      elif INVITE_REGEX.fullmatch(cmsg.content) is not None and \
        len(invites) == 1 and all(i is None for i in invites.values()):
        print(cmsg.id, 'expired invite')
        await cmsg.delete()
    else:
      ...
    ...
