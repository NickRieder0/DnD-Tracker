''' constants '''
import os
from datetime import timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1405002638147321906 # bot-testing
GUILD_ID = 1403182852262072431 # toolugg's server
COGS_LIST = [
    'create_dnd_poll',
    'message_edit'
]

DEFAULT_POLL_QUESTION = "What days work for you?"
DEFAULT_POLL_DURATION = 24 # hours
NEXT_DAY = timedelta(days=1)
NEXT_WEEKEND = timedelta(days=4)
ADDRESS = "8387 Red Cedar Ct, Florence, KY 41042"
DESCRIPTION = "D&D session at Austin's House"
TIMEZONE = pytz.timezone('America/New_York')
