# Required
from discord import app_commands as slash, Interaction
from discord.ext.commands import Bot, Cog, Context, command

# Configuration
from modules import shared

class CogName(Cog, name='Cog Name'):
  def __init__(self, bot: Bot) -> None:
    self.bot = bot
