import nextcord
from nextcord.ext import commands

from utils.config import MAX_TIMES
from utils.helpers import build_thug_payload, can_mass_mention, fire_message, parse_times, send_ephemeral_note
from utils.logger import log


class ThugButton(nextcord.ui.Button):
    def __init__(self, message: str | None):
        super().__init__(label="thug", emoji="🔥", style=nextcord.ButtonStyle.danger, custom_id="thug_spam")
        self.message = message

    async def callback(self, interaction: nextcord.Interaction):
        times: int = self.view.times
        await send_ephemeral_note(interaction, "sending")
        for _ in range(times):
            content, files = build_thug_payload(self.message)
            allow = can_mass_mention(content)
            ok = await fire_message(interaction, content, allow_mention=allow, files=files)
            if not ok:
                break


class ThugView(nextcord.ui.View):
    def __init__(self, message: str | None, times: int):
        super().__init__(timeout=None)
        self.times = times
        self.add_item(ThugButton(message))


class ThugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="thug", description="drop a thug message with random media from the downloads folder", integration_types=[0, 1], contexts=[0, 1, 2])
    async def thug(
        self,
        interaction: nextcord.Interaction,
        button: bool = nextcord.SlashOption(
            name="button",
            description="show a clickable spam button (infinite uses)",
            choices={"true": True, "false": False},
            required=False,
        ),
        message: str = nextcord.SlashOption(
            name="message",
            description="custom message to attach (optional)",
            required=False,
        ),
        times: int = nextcord.SlashOption(
            name="times",
            description=f"how many messages per click (1-{MAX_TIMES})",
            required=False,
            min_value=1,
            max_value=MAX_TIMES,
        ),
    ):
        await send_ephemeral_note(interaction, "sending")
        times = parse_times(times)

        if button:
            view = ThugView(message, times)
            try:
                await interaction.followup.send(view=view, ephemeral=True)
            except Exception as e:
                log.warning(f"thug: ephemeral button failed: {e}")
        else:
            for _ in range(times):
                content, files = build_thug_payload(message)
                allow = can_mass_mention(content)
                ok = await fire_message(interaction, content, allow_mention=allow, files=files)
                if not ok:
                    break


def setup(bot):
    bot.add_cog(ThugCog(bot))
