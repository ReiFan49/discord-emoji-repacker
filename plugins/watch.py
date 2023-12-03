import os
from typing import List
import asyncio
from datetime import datetime

from discord.ext.commands import (
  Bot, Cog, Context,
)
import modules.asyncio
import modules.shared
from modules import utils

FILE_POLLING_TIME = 10

class File(Cog,name='File Watcher'):
  def __init__(self, bot: Bot, files: List[str]) -> None:
    self.bot = bot
    self.files = files
    self.file_mtimes = dict((file, self._obtain_file_mtime_(file)) for file in files)
    self.bg_task = bot.loop.create_task(self.watch_files(), name='emoji-repack.online:file-watcher')
    self.bg_task.add_done_callback(modules.asyncio.exit_on_fail)

  async def watch_files(self) -> None:
    while True:
      await asyncio.sleep(FILE_POLLING_TIME)
      for file in self.files:
        new_mtime = self._obtain_file_mtime_(file)
        if new_mtime == self.file_mtimes[file]:
          continue
        print("File", file, "is changed.")
        self.bot.dispatch('c/file_change', file)
        self.file_mtimes[file] = new_mtime

  def _obtain_file_mtime_(self, file: str) -> None:
    return os.stat(file).st_mtime
