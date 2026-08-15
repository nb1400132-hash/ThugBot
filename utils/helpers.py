import nextcord
from nextcord.ext import commands

from utils.config import DEFAULT_TIMES, MAX_TIMES, FILES_PER_MESSAGE
from utils.logger import log
from .media import pick_random_files


async def send_ephemeral_note(interaction: nextcord.Interaction, text: str = "sending") -> None:
    try:
        if interaction.response.is_done():
            await interaction.followup.send(text, ephemeral=True)
        else:
            await interaction.response.send_message(text, ephemeral=True)
    except nextcord.HTTPException:
        try:
            await interaction.followup.send(text, ephemeral=True)
        except Exception:
            pass


def parse_times(times: int | None) -> int:
    if times is None:
        return DEFAULT_TIMES
    if times < 1:
        return 1
    if times > MAX_TIMES:
        return MAX_TIMES
    return times


def resolve_target_user(value) -> nextcord.User | nextcord.Member | None:
    if value is None:
        return None
    if isinstance(value, (nextcord.User, nextcord.Member)):
        return value
    return None


def build_thug_payload(message: str | None) -> tuple[str | None, list[nextcord.File]]:
    files = pick_random_files(FILES_PER_MESSAGE)
    content = message if message else None
    if not files and not content:
        content = "thug life."
    return content, files


def can_mass_mention(message: str | None) -> bool:
    if not message:
        return False
    low = message.lower()
    return "@everyone" in low or "@here" in low


async def fire_message(
    interaction: nextcord.Interaction,
    content: str,
    *,
    allow_mention: bool = True,
    embed=None,
    view=None,
    files: list[nextcord.File] | None = None,
) -> bool:
    try:
        allowed = nextcord.AllowedMentions(everyone=True, roles=True, users=True)
        kwargs: dict = {"content": content, "allowed_mentions": allowed}
        if embed is not None:
            kwargs["embed"] = embed
        if view is not None:
            kwargs["view"] = view
        if files:
            kwargs["files"] = files
        await interaction.followup.send(**kwargs)
        return True
    except nextcord.HTTPException as e:
        log.warning(f"send failed: {e.status} {e.text}")
        return False
    except Exception as e:
        log.warning(f"send error: {e}")
        return False


async def fire_first_message(
    interaction: nextcord.Interaction,
    content: str,
    *,
    allow_mention: bool = True,
    embed=None,
    view=None,
    files: list[nextcord.File] | None = None,
) -> bool:
    try:
        allowed = nextcord.AllowedMentions(everyone=True, roles=True, users=True)
        kwargs: dict = {"content": content, "allowed_mentions": allowed}
        if embed is not None:
            kwargs["embed"] = embed
        if view is not None:
            kwargs["view"] = view
        if files:
            kwargs["files"] = files
        if not interaction.response.is_done():
            await interaction.response.send_message(**kwargs)
        else:
            await interaction.followup.send(**kwargs)
        return True
    except nextcord.HTTPException as e:
        log.warning(f"first send failed: {e.status} {e.text}")
        return False
    except Exception as e:
        log.warning(f"first send error: {e}")
        return False
