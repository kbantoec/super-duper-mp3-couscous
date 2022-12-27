import os
import re

from mutagen.mp3 import MP3
from mutagen.id3 import TRCK, TPOS


def enable_write_permissions(current_permission: str, dir_entry: os.DirEntry):
    # Read-only finishes with 444, and a writable file with 666
    print(f"Current permissions: {current_permission}")

    if current_permission == "444":
        # Make the file writable
        os.chmod(dir_entry.path, 0o666)

        # Check the updated file permissions
        updated_permissions = oct(os.stat(dir_entry.path).st_mode)[-3:]
        print(f"Updated permissions: {updated_permissions}")


def build_regexp() -> tuple[re.Pattern, re.Pattern]:
    chap_pattern: str = r"Chapter\s(?P<chapter_number>\d+)"
    chap_regexp: re.Pattern = re.compile(chap_pattern)

    part_pattern: str = r"Part\s(?P<part_number>\d+)"
    part_regexp: re.Pattern = re.compile(part_pattern)
    return chap_regexp, part_regexp


def get_chapter_part_numbers() -> dict[int, list[int]]:
    """Gets the chapter number and its relative parts numbers, e.g.,
    {7: [1, 2, 3, 4]}, which means that chapter 7 is composed by 4 parts.
    This dictionary object allows us to build the track pairs, e.g., track 1/4,
    meaning that we know how much tracks for each chapter there are.
    Moreover, the dictionary object allows us to know how much chapters there are."""
    chaps_parts: dict[int, list[int]] = {}

    chap_regexp, part_regexp = build_regexp()

    items: list[os.DirEntry] = [e for e in os.scandir("./mp3") if e.name.endswith(".mp3") and e.is_file()]

    for i, dir_entry in enumerate(items):
        # Check the current file permissions
        current_permissions = oct(os.stat(dir_entry.path).st_mode)[-3:]

        enable_write_permissions(current_permissions, dir_entry)

        chap_r = chap_regexp.search(dir_entry.name)
        chapter_number: int = int(chap_r.group("chapter_number"))
        print(f"{chapter_number = }")

        part_r = part_regexp.search(dir_entry.name)
        part_number: int = int(part_r.group("part_number"))
        print(f"{part_number = }")

        if chapter_number not in chaps_parts.keys():
            chaps_parts[chapter_number] = []

        chaps_parts[chapter_number].append(part_number)

    return chaps_parts


def write_mp3_infos() -> None:
    elements: dict[int, list[int]] = get_chapter_part_numbers()
    max_chapter: int = max(elements.keys())

    chap_regexp, part_regexp = build_regexp()

    items: list[os.DirEntry] = [e for e in os.scandir("./mp3") if e.name.endswith(".mp3") and e.is_file()]

    for i, dir_entry in enumerate(items):
        chap_r = chap_regexp.search(dir_entry.name)
        chapter_number: int = int(chap_r.group("chapter_number"))
        print(f"{chapter_number = }")

        part_r = part_regexp.search(dir_entry.name)
        part_number: int = int(part_r.group("part_number"))
        print(f"{part_number = }")

        track_pair: str = f"{part_number}/{max(elements[chapter_number])}"
        album_pair: str = f"{chapter_number}/{max_chapter}"

        audio = MP3(dir_entry.path)
        audio.tags["tracknumber"] = TRCK(encoding=3, text=track_pair)
        audio.tags["#"] = TRCK(encoding=3, text=track_pair)
        audio.tags["discnumber"] = TPOS(text=album_pair)
        audio.save()


def rename_track() -> None:
    items: list[os.DirEntry] = [e for e in os.scandir("./mp3")
                                if e.name.endswith(".mp3") and e.is_file() and e.name.startswith("Napoleon Hill")]

    for item in items:
        name: str = item.name.split(".")[0]
        name_elements: list[str] = name.split(" - ")
        new_name: str = f"{name_elements[2]} - {name_elements[1]} - {name_elements[0]}.mp3"
        os.rename(f"./mp3/{item.name}", f"./mp3/{new_name}")


if __name__ == "__main__":
    write_mp3_infos()
    rename_track()
