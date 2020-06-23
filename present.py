#!/usr/bin/env python3
import argparse
import pickle
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from shutil import copy
from helpers import filters, helpers
from pathlib import Path
from math import ceil


def render_page(file, messages, **kwargs):
    env = Environment(loader=FileSystemLoader("templates"))
    env.filters.update(filters)
    template = env.get_template("index.html")
    template.globals.update(helpers)
    output_from_parsed_template = template.render(messages=messages, **kwargs)
    with file.open("w") as f:
        f.write(output_from_parsed_template)


def generate_pages(messages, target_path, media_path=None, entries_per_page=1000, **kwargs):
    num_pages = ceil(len(messages) / entries_per_page)
    for page in range(1, num_pages + 1):
        render_page(
            target_path / f"page_{page:0>4}.html",
            messages[(page - 1) * entries_per_page:page * entries_per_page],
            target_path=target_path, media_path=media_path, current_page=page, num_pages=num_pages,
            **kwargs)


def main(args):
    target_path = Path(args.output_folder)
    media_path = Path(args.media_folder) if args.media_folder else None
    with open(args.input, "rb") as f:
        messages = pickle.load(f)
    generate_pages(messages[::-1], target_path=target_path, media_path=media_path,
                  entries_per_page=args.num_entries_per_page, channel_name=args.channel)
    copy(target_path / "page_0001.html", target_path / "index.html")
    copy_tree("static", (target_path / "static").as_posix())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert pickled archive to html."
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Path to the pickled archive.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        help="Path to the output folder.",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--media-folder",
        help="Path to the media folder (a relative path will be used in the html files).",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-n",
        "--num-entries-per-page",
        type=int,
        help="Number of entries for page.",
        required=False,
        default=1000,
    )
    parser.add_argument(
        "-c",
        "--channel",
        metavar="channel_name",
        help="channel name used for the header (automatic fetching not supported at the moment).",
        required=False,
    )
    args = parser.parse_args()

    main(args)
