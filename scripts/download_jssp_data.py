import requests as req
import argparse
import zipfile as zip
import io
import itertools as it
from pathlib import Path
from dataclasses import dataclass
from typing import Generator


@dataclass
class Args:
    output_dir: Path
    force: bool
    taillard: bool


def get_categories_range() -> Generator[None, None, int]:
    return range(1, 8 + 1)


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Data downloader",
        description="Download input data & solutions for the JSSP experiments",
        epilog="""
            Please note that the "http://jobshop.jjvh.nl" domain, which hosts the data, might be unavailable.
            Authored by Kacper Kafara <kacperkafara@gmail.com>.
        """
    )

    parser.add_argument("output_dir", type=Path, default=Path("."), help="Output directory for the data")
    parser.add_argument("--force", action="store_true", required=False, default=False, help="Whether to ignore errors")
    parser.add_argument("--taillard", action="store_true", required=False, default=True, help="Whether to download Taillard spec alongside standard (UNSUPPORTED YET)")
    return parser


def resolve_files_to_extract(zip_file: zip.ZipFile, include_taillard=True) -> list[Path]:
    if include_taillard:
        return zip_file.namelist()
    else:
        return list(
            filter(lambda path: not str(path).startswith("Taillard"),
                   zip_file.namelist()))


def resolve_category_name(zip_file: zip.ZipFile) -> str:
    namelist = zip_file.namelist()
    if len(namelist) == 0:
        raise ValueError("Zip file must not be empty")

    filename: str = namelist[0]
    if '/' in filename:
        filename = filename.split('/')[-1]

    digits = [str(d) for d in range(0, 10)]
    category_name = it.takewhile(lambda ch: ch not in digits, filename)
    return ''.join(list(category_name)) + '_instances'


# http://jobshop.jjvh.nl/specification_zip.php?catagory_id=1
endpoint = "http://jobshop.jjvh.nl"
specs_endpoint = "http://jobshop.jjvh.nl/specification_zip.php"


def main():
    args: Args = build_cli_parser().parse_args()

    for id in get_categories_range():
        print(f"[INFO] Downloading for category_id {id}")
        # Typo in `catagory` is intentional...
        response: req.Response = req.get(specs_endpoint, {
            'catagory_id': id
        })

        if response.status_code != 200:
            print(f"[ERROR] GET to {response.request.url} failed with status code {response.status_code}")
            if not args.force:
                exit(1)

        zipped_file = zip.ZipFile(io.BytesIO(response.content))
        category_name = resolve_category_name(zipped_file)
        output_dir = args.output_dir.joinpath(category_name)

        # This is potential security risk
        # See: https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.extractall
        zipped_file.extractall(output_dir)


if __name__ == "__main__":
    main()

