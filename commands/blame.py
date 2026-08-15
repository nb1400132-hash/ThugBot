import nextcord
from nextcord.ext import commands

from utils.config import MAX_TIMES, BLAME_START_PRESET, BLAME_FINISH_PRESET, THANKS_LINE
from utils.helpers import fire_message, parse_times, resolve_target_user, send_ephemeral_note
from utils.logger import log


def build_blame_embed(preset: str, user) -> nextcord.Embed:
    embed = nextcord.Embed(color=0xFF4757)
    mention = user.mention if user else "unknown"
    embed.description = f"# {preset}\n{mention} {THANKS_LINE}"
    return embed


class BlameButton(nextcord.ui.Button):
    def __init__(self, custom_id: str, label: str, preset: str, user):
        super().__init__(label=label, emoji="📌", style=nextcord.ButtonStyle.danger, custom_id=custom_id)
        self.preset = preset
        self.user = user

    async def callback(self, interaction: nextcord.Interaction):
        times: int = self.view.times
        await send_ephemeral_note(interaction, "sending")
        embed = build_blame_embed(self.preset, self.user)
        for _ in range(times):
            ok = await fire_message(interaction, content="", embed=embed)
            if not ok:
                break


class BlameView(nextcord.ui.View):
    def __init__(self, custom_id: str, label: str, preset: str, user, times: int):
        super().__init__(timeout=None)
        self.times = times
        self.add_item(BlameButton(custom_id, label, preset, user))


class BlameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _run(self, interaction: nextcord.Interaction, preset: str, label: str, custom_id: str, button: bool, times: int, user):
        times = parse_times(times)
        target = resolve_target_user(user)
        await send_ephemeral_note(interaction, "sending")
        embed = build_blame_embed(preset, target)

        if button:
            view = BlameView(custom_id, label, preset, target, times)
            try:
                await interaction.followup.send(view=view, ephemeral=True)
            except Exception as e:
                log.warning(f"{label}: ephemeral button failed: {e}")
        else:
            for _ in range(times):
                ok = await fire_message(interaction, content="", embed=embed)
                if not ok:
                    break

    @nextcord.slash_command(name="blamestart", description="start blaming a user for the raid", integration_types=[0, 1], contexts=[0, 1, 2])
    async def blamestart(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = nextcord.SlashOption(name="user", description="who to blame"),
        button: bool = nextcord.SlashOption(
            name="button",
            description="show a spam button (infinite uses)",
            choices={"true": True, "false": False},
            required=False,
        ),
        times: int = nextcord.SlashOption(
            name="times",
            description=f"how many embeds (1-{MAX_TIMES})",
            required=False,
            min_value=1,
            max_value=MAX_TIMES,
        ),
    ):
        await self._run(interaction, BLAME_START_PRESET, "blamestart", "blame_start_spam", button, times, user)

    @nextcord.slash_command(name="blamefinish", description="finish blaming a user for the raid", integration_types=[0, 1], contexts=[0, 1, 2])
    async def blamefinish(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = nextcord.SlashOption(name="user", description="who to thank"),
        button: bool = nextcord.SlashOption(
            name="button",
            description="show a spam button (infinite uses)",
            choices={"true": True, "false": False},
            required=False,
        ),
        times: int = nextcord.SlashOption(
            name="times",
            description=f"how many embeds (1-{MAX_TIMES})",
            required=False,
            min_value=1,
            max_value=MAX_TIMES,
        ),
    ):
        await self._run(interaction, BLAME_FINISH_PRESET, "blamefinish", "blame_finish_spam", button, times, user)


def setup(bot):
    bot.add_cog(BlameCog(bot))
