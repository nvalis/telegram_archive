import telethon
import random
from pathlib import Path


helpers = {}
filters = {}


def register_helper(func):
    global helpers
    helpers[func.__name__] = func
    return func


def register_filter(func):
    global filters
    filters[func.__name__] = func
    return func


@register_helper
def is_service(m):
    return isinstance(m, telethon.types.MessageService)


@register_helper
def is_poll(m):
    return isinstance(m.media, telethon.types.MessageMediaPoll)


@register_helper
def is_photo(m):
    return isinstance(m.media, telethon.types.MessageMediaPhoto)


@register_helper
def is_audio(m):
    if isinstance(m.media, telethon.types.MessageMediaDocument):
        return m.media.document.mime_type.startswith("audio")
    return False


@register_helper
def pagination(current_page, num_pages, adjacents=2, at_ends=1):
    # Don't break up only a few pages
    if num_pages < 7 + adjacents:
        return list(range(1, num_pages + 1))

    # Close to the beginning
    if current_page < 1 + adjacents * 2:
        pages = list(range(1, adjacents * 2 + 1))
        pages.append("...")
        pages += list(range(num_pages - at_ends + 1, num_pages + 1))
        return pages

    # In the middle
    if adjacents < current_page <= num_pages - 2 * adjacents:
        pages = list(range(1, at_ends + 1))
        pages.append("...")
        pages += list(range(current_page - adjacents, current_page + adjacents + 1))
        pages.append("...")
        pages += list(range(num_pages - at_ends + 1, num_pages + 1))
        return pages

    # At the end
    pages = list(range(1, at_ends + 1))
    pages.append("...")
    pages += list(range(num_pages - adjacents * 2, num_pages + 1))
    return pages


@register_helper
def generate_waveform(num_bars=50):
    waveform = [random.uniform(0, 100) for _ in range(num_bars)]
    waveform[random.randint(0, num_bars - 1)] = 100
    return waveform


@register_filter
def channellink(channel_id):
    return f"<a href=\"https://t.me/{channel_id}\">{channel_id}</a>"


@register_filter
def media_filename(message, media_path=""):
    if not media_path:
        return ""
    media_path = Path(media_path)
    try:
        return media_path.glob(f"{message.id:0>7}.*").__iter__().__next__().as_posix()
    except StopIteration:
        return ""


@register_filter
def relative_to(path, target_path):
    target_path = Path(target_path)
    try:
        return Path(path).relative_to(target_path).as_posix()
    except ValueError:
        return ""


@register_filter
def duration(message):
    d = message.document.attributes[0].duration
    return f"{d // 60:0>2}:{d % 60:0>2}"
