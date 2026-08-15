import nextcord
from nextcord.ext import commands

from utils.config import MAX_TIMES
from utils.helpers import fire_message, parse_times, send_ephemeral_note, can_mass_mention
from utils.logger import log
from utils.media import load_unthugs_message


class UnthugsButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="unthugs", emoji="💀", style=nextcord.ButtonStyle.secondary, custom_id="unthugs_spam")

    async def callback(self, interaction: nextcord.Interaction):
        times: int = self.view.times
        message: str = self.view.message_content
        await send_ephemeral_note(interaction, "sending")
        for _ in range(times):
            ok = await fire_message(interaction, message, allow_mention=False)
            if not ok:
                break


class UnthugsView(nextcord.ui.View):
    def __init__(self, times: int, message: str):
        super().__init__(timeout=None)
        self.times = times
        self.message_content = message
        self.add_item(UnthugsButton())


class UnthugsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="unthugs", description="send the preset unthug message", integration_types=[0, 1], contexts=[0, 1, 2])
    async def unthugs(
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
        message = load_unthugs_message()
        await send_ephemeral_note(interaction, "sending")

        if button:
            view = UnthugsView(times, message)
            try:
                await interaction.followup.send(view=view, ephemeral=True)
            except Exception as e:
                log.warning(f"unthugs: ephemeral button failed: {e}")
        else:
            for _ in range(times):
                ok = await fire_message(interaction, message, allow_mention=False)
                if not ok:
                    break


def setup(bot):
    bot.add_cog(UnthugsCog(bot))
