#!/usr/bin/env python3

import argparse
import asyncio
import telethon
from telethon.tl.functions.messages import GetHistoryRequest
import pickle
from pathlib import Path
import logging

log = logging.getLogger("archive")
logging.basicConfig(level=logging.DEBUG)
logging.root.handlers[0].addFilter(logging.Filter("archive"))


async def init_client(api_id, api_hash):
    client = telethon.TelegramClient("telegram_archive", api_id, api_hash)
    await client.start()
    return client


def dump_messages(messages, file_path):
    pickle.dump(messages, open(file_path, "wb"))


async def get_channel_messages(
    client, channel_entity, out_file, media_path=None, total_count_limit=0, download_avatars=False
):
    # scrape last n messages from the given channel
    offset_id = 0
    limit = 20

    if out_file.is_file():
        log.info(
            f"File '{out_file}' already exists. Reading already scraped messages..."
        )
        all_messages = pickle.load(open(out_file, "rb"))
        total_messages = len(all_messages)
        log.info(f"Read {total_messages} messages")
    else:
        all_messages = []
        total_messages = 0

    while True:
        if total_count_limit - total_messages < limit:
            limit = total_count_limit - total_messages
        history = await client(
            GetHistoryRequest(
                peer=channel_entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            message.channel_title = (await client.get_entity(message.to_id)).title
            if message.from_id:
                user = await client.get_entity(message.from_id)
                message.from_user = dict(
                    first_name=user.first_name, last_name=user.last_name, id_=user.id,
                    username=user.username)
                if download_avatars and not list(media_path.glob(f"avatar_{user.id:0>10}.*")):
                    await client.download_profile_photo(user, file=media_path / f"avatar_{user.id:0>10}")
        all_messages.extend(messages)
        log.info(f"{len(messages)} new, {len(all_messages)} overall")
        if media_path:
            for message in messages:
                if message.media:
                    if not list(
                        media_path.glob(f"{message.id:07}.*")
                    ):  # file was not already downloaded
                        await client.download_media(
                            message, file=media_path / f"{message.id:07}"
                        )

        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
        dump_messages(all_messages, out_file)
    return all_messages


async def main(args):
    client = await init_client(args.id, args.hash)
    channel = await client.get_entity(args.channel)
    log.info(f"Scraping channel {args.channel}, this might take a while...")

    if args.out:
        out_file = Path(args.out)
        subdir = out_file.parent / args.channel
    else:
        subdir = Path.cwd() / args.channel
        out_file = subdir / f"{args.channel}.pkl"
    subdir.mkdir(exist_ok=True)

    media_path = subdir if args.media or args.avatars else None
    messages = await get_channel_messages(
        client, channel, out_file, media_path=media_path, total_count_limit=args.number,
        download_avatars=args.avatars
    )

    dump_messages(messages, out_file)
    log.info(f"Saved {len(messages)} messages to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Archive messages of a given telegram channel."
    )
    parser.add_argument(
        "-i",
        "--id",
        metavar="api_id",
        type=int,
        help="Telegram API ID (see: https://core.telegram.org/api/obtaining_api_id)",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--hash",
        metavar="api_hash",
        type=str,
        help="Telegram API hash (see: https://core.telegram.org/api/obtaining_api_id)",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--channel",
        metavar="channel_name",
        type=str,
        help="channel name to scrape",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--out",
        metavar="out_file",
        type=str,
        help="save messages to given file, if not set we are using {channel_name}.pkl",
    )
    parser.add_argument(
        "-n",
        "--number",
        metavar="N",
        type=int,
        help="save last n messages, if 0 or not given we will archive all messages",
        default=0,
    )
    parser.add_argument(
        "-m", "--media", help="also archive attached media files", action="store_true"
    )
    parser.add_argument(
        "-a", "--avatars", help="also archive profile avatars", action="store_true"
    )
    args = parser.parse_args()

    asyncio.run(main(args))
