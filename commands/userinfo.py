import nextcord
from nextcord.ext import commands

from utils.helpers import fire_message, fire_first_message, send_ephemeral_note, can_mass_mention
from utils.logger import log


class UserInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="userinfo", description="pull up info on a user", integration_types=[0, 1], contexts=[0, 1, 2])
    async def userinfo(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = nextcord.SlashOption(
            name="user",
            description="who to look up",
            required=True,
        ),
        button: bool = nextcord.SlashOption(
            name="button",
            description="post anonymously?",
            choices={"true": True, "false": False},
            required=False,
        ),
    ):
        await send_ephemeral_note(interaction, "sending")

        embed = nextcord.Embed(title="user info", color=0x2ED573)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="name", value=user.mention, inline=True)
        embed.add_field(name="id", value=f"`{user.id}`", inline=True)
        embed.add_field(name="account made", value=nextcord.utils.format_dt(user.created_at, "R"), inline=True)

        if isinstance(user, nextcord.Member):
            roles = [r.mention for r in user.roles if r.name != "@everyone"]
            embed.add_field(name="joined", value=nextcord.utils.format_dt(user.joined_at, "R") if user.joined_at else "?", inline=True)
            embed.add_field(name="roles", value=", ".join(roles[:10]) or "none", inline=False)
            embed.add_field(name="boosting", value="yes" if user.premium_since else "no", inline=True)
            embed.color = user.color if user.color.value else 0x2ED573
        else:
            embed.add_field(name="note", value="user is not in this server", inline=False)

        ok = await fire_first_message(interaction, content="", embed=embed)
        if not ok:
            log.warning("userinfo: send failed")


def setup(bot):
    bot.add_cog(UserInfoCog(bot))
