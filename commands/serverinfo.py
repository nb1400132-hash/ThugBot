import nextcord
from nextcord.ext import commands

from utils.helpers import fire_first_message, send_ephemeral_note
from utils.logger import log


class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="serverinfo", description="pull up info on this server", integration_types=[0, 1], contexts=[0, 1, 2])
    async def serverinfo(
        self,
        interaction: nextcord.Interaction,
        button: bool = nextcord.SlashOption(
            name="button",
            description="post anonymously?",
            choices={"true": True, "false": False},
            required=False,
        ),
    ):
        await send_ephemeral_note(interaction, "sending")
        g = interaction.guild
        if g is None:
            await interaction.followup.send("this only works in servers.", ephemeral=True)
            return

        embed = nextcord.Embed(title="server info", color=0x2ED573)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="name", value=g.name, inline=True)
        embed.add_field(name="id", value=f"`{g.id}`", inline=True)
        embed.add_field(name="owner", value=f"<@{g.owner_id}>", inline=True)
        embed.add_field(name="members", value=str(g.member_count), inline=True)
        embed.add_field(name="channels", value=str(len(g.channels)), inline=True)
        embed.add_field(name="roles", value=str(len(g.roles)), inline=True)
        embed.add_field(name="boosts", value=f"lvl {g.premium_tier} ({g.premium_subscription_count})", inline=True)
        embed.add_field(name="made", value=nextcord.utils.format_dt(g.created_at, "R"), inline=True)
        embed.add_field(name="verification", value=str(g.verification_level), inline=True)

        ok = await fire_first_message(interaction, content="", embed=embed)
        if not ok:
            log.warning("serverinfo: send failed")


def setup(bot):
    bot.add_cog(ServerInfoCog(bot))
