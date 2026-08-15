import os
import sys

import nextcord
from nextcord.ext import commands

from utils.config import BOT_PREFIX, DISCORD_TOKEN
from utils.logger import log

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = False
intents.presences = False

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    log.info(f"logged in as {bot.user} (id={bot.user.id})")
    local_cmds = bot.get_all_application_commands()
    log.info(f"loaded {len(local_cmds)} commands locally:")
    for cmd in local_cmds:
        log.info(f"  /{cmd.name} — {cmd.description}")
    try:
        await bot.sync_all_application_commands()
        log.info("synced all commands to discord")
    except Exception as e:
        log.error(f"sync failed: {e}")
        return
    try:
        remote = await bot.http.get_global_commands(bot.user.id)
        log.info(f"discord confirms {len(remote)} global commands registered")
        for cmd in remote:
            log.info(f"  /{cmd['name']} — {cmd.get('description', '')}")
    except Exception as e:
        log.warning(f"could not fetch remote commands: {e}")
    log.info(f"invite: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&scope=applications.commands%20bot&permissions=8192")
    log.info("type / in any discord channel — commands should autocomplete within 60 seconds")


INITIAL_COGS = [
    "commands.talk",
    "commands.thug",
    "commands.unthugs",
    "commands.userinfo",
    "commands.serverinfo",
    "commands.blame",
    "commands.preset1",
]


def load_cogs():
    for cog in INITIAL_COGS:
        try:
            bot.load_extension(cog)
            log.info(f"loaded cog: {cog}")
        except Exception as e:
            log.error(f"failed to load {cog}: {e}")


@bot.event
async def on_connect():
    log.info("connected to gateway")


@bot.event
async def on_disconnect():
    log.warning("disconnected from gateway")


def main():
    if not DISCORD_TOKEN or DISCORD_TOKEN.startswith("your_"):
        log.error("DISCORD_TOKEN missing. copy .env.example to .env and paste your bot token.")
        sys.exit(1)
    load_cogs()
    bot.add_all_application_commands()
    log.info(f"registered {len(bot.get_all_application_commands())} application commands with bot")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
