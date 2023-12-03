from typing import Optional
from datetime import datetime, timedelta
import asyncio

from discord.ext.commands import Bot, Cog, command, check
import modules.asyncio
from modules import utils

class Feature(Cog, name='Discord Sync'):
  def __init__(self, bot: Bot) -> None:
    self.bot = bot
    self.daily_sync = bot.loop.create_task(self.timed_sync(), name='emoji-repack.online:daily-synchronize')

  @command(name='sync')
  @check(utils.is_owner)
  async def sync_commands(self, ctx, *, key: Optional[str] = None) -> None:
    serverID = None
    if key == 'server':
      if ctx.guild is not None:
        serverID = ctx.guild.id
      return
    print("Syncing Commands on", "Global" if serverID is None else serverID)
    for c in self.bot.tree.get_commands(guild=serverID):
      print("-", repr(c))
      if hasattr(c, 'commands'):
        for cc in c.commands:
          print("  -", repr(cc))
    await self.bot.tree.sync(guild=serverID)

  @sync_commands.error
  async def sync_commands_error(ctx, error):
    print(type(error).__name__, ": ", str(error))

  async def timed_sync(self):
    await self.bot.wait_until_ready()
    while True:
      ctime = datetime.fromtimestamp(self.bot.loop.time())
      ntime = (ctime + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
      )
      dtime = (ntime - ctime).total_seconds()
      await asyncio.sleep(dtime)
      if self.bot.is_closed():
        break
      try:
        await self.bot.tree.sync(guild=None)
        for serverID in self.bot.tree._guild_commands.keys():
          await self.bot.tree.sync(guild=serverID)
      except Exception as e:
        print("Error during daily sync.")
        print(type(e).__name__, ":", str(e))
    pass
