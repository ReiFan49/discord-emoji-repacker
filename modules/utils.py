from modules import shared

async def is_owner(ctx):
  return ctx.author.id in shared.config.users

is_manager = is_owner
