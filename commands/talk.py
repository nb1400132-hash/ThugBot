import nextcord
from nextcord.ext import commands

from utils.config import MAX_TIMES
from utils.helpers import fire_message, fire_first_message, parse_times, send_ephemeral_note, can_mass_mention
from utils.logger import log


class TalkButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="send", emoji="💬", style=nextcord.ButtonStyle.primary, custom_id="talk_spam")

    async def callback(self, interaction: nextcord.Interaction):
        message: str | None = self.view.message_content
        times: int = self.view.times
        await send_ephemeral_note(interaction, "sending")
        allow = can_mass_mention(message)
        for _ in range(times):
            ok = await fire_message(interaction, message or "yo", allow_mention=allow)
            if not ok:
                break


class TalkView(nextcord.ui.View):
    def __init__(self, message_content: str | None, times: int):
        super().__init__(timeout=None)
        self.message_content = message_content
        self.times = times
        self.add_item(TalkButton())


class TalkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="talk", description="send a message anonymously", integration_types=[0, 1], contexts=[0, 1, 2])
    async def talk(
        self,
        interaction: nextcord.Interaction,
        button: bool = nextcord.SlashOption(
            name="button",
            description="show a clickable spam button",
            choices={"true": True, "false": False},
            required=False,
        ),
        times: int = nextcord.SlashOption(
            name="times",
            description=f"how many messages to send (1-{MAX_TIMES})",
            required=False,
            min_value=1,
            max_value=MAX_TIMES,
        ),
        message: str = nextcord.SlashOption(
            name="message",
            description="what to say",
            required=False,
        ),
    ):
        times = parse_times(times)
        allow = can_mass_mention(message)
        content = message or "yo"

        if button:
            await interaction.response.send_message("sending", ephemeral=True)
            view = TalkView(message, times)
            try:
                await interaction.followup.send(view=view, ephemeral=True)
            except Exception as e:
                log.warning(f"talk: ephemeral button failed: {e}")
        else:
            await send_ephemeral_note(interaction, "sending")
            for _ in range(times):
                ok = await fire_message(interaction, content, allow_mention=allow)
                if not ok:
                    break


def setup(bot):
    bot.add_cog(TalkCog(bot))
