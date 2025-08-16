''' discord bot'''
#pylint:disable=line-too-long,missing-function-docstring,unused-argument
import discord
from constants import (TOKEN,
                       CHANNEL_ID,
                       COGS_LIST)

class DndTrackerBot(discord.Bot):
    ''' discord bot with custom data '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []

bot = DndTrackerBot()

@bot.event
async def on_ready():
    ''' test function '''
    channel = bot.get_channel(CHANNEL_ID)
    for cog in COGS_LIST:
        bot.load_extension(f"cogs.{cog}")
    await channel.send("DnD-Tracker bot is ready!")

bot.run(TOKEN)
