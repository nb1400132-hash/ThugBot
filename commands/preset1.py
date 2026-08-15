import nextcord
from nextcord.ext import commands

from utils.config import FILES_PER_MESSAGE, MAX_TIMES
from utils.helpers import fire_message, parse_times, send_ephemeral_note, can_mass_mention
from utils.logger import log
from utils.media import load_preset_message, pick_preset1_files


class Preset1Button(nextcord.ui.Button):
    def __init__(self, message: str):
        super().__init__(label="preset1", emoji="📢", style=nextcord.ButtonStyle.primary, custom_id="preset1_spam")
        self.message = message

    async def callback(self, interaction: nextcord.Interaction):
        times: int = self.view.times
        message: str = self.view.message_content
        await send_ephemeral_note(interaction, "sending")
        allow = can_mass_mention(message)
        for _ in range(times):
            files = pick_preset1_files(FILES_PER_MESSAGE)
            ok = await fire_message(interaction, message, allow_mention=allow, files=files)
            if not ok:
                break


class Preset1View(nextcord.ui.View):
    def __init__(self, times: int, message: str):
        super().__init__(timeout=None)
        self.times = times
        self.message_content = message
        self.add_item(Preset1Button(message))


class Preset1Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="preset1", description="send the preset1.txt message with random media from preset1files", integration_types=[0, 1], contexts=[0, 1, 2])
    async def preset1(
        self,
        interaction: nextcord.Interaction,
        button: bool = nextcord.SlashOption(
            name="button",
            description="show a spam button (infinite uses)",
            choices={"true": True, "false": False},
            required=False,
        ),
        times: int = nextcord.SlashOption(
            name="times",
            description=f"how many messages (1-{MAX_TIMES})",
            required=False,
            min_value=1,
            max_value=MAX_TIMES,
        ),
    ):
        times = parse_times(times)
        message = load_preset_message("preset1.txt")
        await send_ephemeral_note(interaction, "sending")
        allow = can_mass_mention(message)

        if button:
            view = Preset1View(times, message)
            try:
                await interaction.followup.send(view=view, ephemeral=True)
            except Exception as e:
                log.warning(f"preset1: ephemeral button failed: {e}")
        else:
            for _ in range(times):
                files = pick_preset1_files(FILES_PER_MESSAGE)
                ok = await fire_message(interaction, message, allow_mention=allow, files=files)
                if not ok:
                    break


def setup(bot):
    bot.add_cog(Preset1Cog(bot))
