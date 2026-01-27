"""
Jellyfin File Renamer Parts Indicator
---------------------
Description:    Lightweight python script that reads files in a working directory, matches the file names to an input regex pattern, 
                and renames matching files using an input dictionary
---------------------
Goal:           Change arbitrary part indicators in filenames to Jellyfin supported part indicators so distinct media files can be
                virtually combined in the Jellyfin UI
---------------------
Definition:     See explanation of Jellyfin's handling media split into multiple parts here:
                https://jellyfin.org/docs/general/server/media/shows/#multiple-parts
                Parts indicator: A character combination signifying a file is part of a whole
                examples:
                A
                B
                -part-1
                -part-2
---------------------
Author:         WinDnDusT
Date:           Jan 2026 
Github:         https://github.com/windndust/jellyfin_file_renamer
"""
import argparse
from pathlib import Path
import re
from re import Match
import json
from typing import Protocol
from functools import partial

class ScriptArgs(Protocol):
    directory_working: Path
    regex_pattern: re.Pattern
    mapping: dict
    dry_run: bool

def parse_commandline_args() -> ScriptArgs:
    parser = argparse.ArgumentParser(description="Rename files to match Jellyfin's naming scheme for 'Content split into multiple files'")
    parser.add_argument("-d", "--directory-working", required=True, type=Path, help="The working directory containing the files to be renamed")
    parser.add_argument("-r", "--regex-pattern", required=True, type=re.compile, help="The Regex Pattern to identify the files to be renamed")
    parser.add_argument("-m", "--mapping", required=True, type=json.loads, help="The dictionary string mapping the arbitrary part type string to Jellyfin's part type. The arbitrary part type will be replaced by Jellyfin's part type")
    parser.add_argument("--dry-run", action="store_true", help="Print intended rename changes instead of actually renaming files")
    return parser.parse_args()

def generate_new_name(match: Match, suffix_map: dict):
    series_coordinates = match.group(1)
    old_suffix = match.group(2)
    new_suffix = suffix_map.get(old_suffix, old_suffix)
    file_extension = match.group(4)
    return f"{series_coordinates}{new_suffix}{file_extension}"

def log_the_changes(log_entries: list, target_dir: Path):
    if log_entries:
        print("Successfully renamed files, logging changes")
        undo_rename_log = target_dir / "undo_rename_log.txt"
        with open(undo_rename_log, "w", encoding="utf-8") as log_file:
            for log_entry in log_entries:
                log_file.write(log_entry)
    else:
        print("No changes detected")

def main():
    print("File Rename Python script")
    args=parse_commandline_args()
    print(f"Passed in arguments::  Directory Working={args.directory_working}, Regex Pattern={args.regex_pattern}, Mapping={args.mapping}")

    bound_generate_name_logic = partial(generate_new_name, suffix_map=args.mapping)

    log_entries = []
    iterator_generator_object = args.directory_working.iterdir()
    for file_path in iterator_generator_object:

        if not file_path.is_file() or file_path.name.startswith("undo"):
            continue

        file_name = file_path.name
        generated_name = re.sub(args.regex_pattern, bound_generate_name_logic, file_name)

        if generated_name!=file_name:            
            full_file_name = file_path.with_name(generated_name)
            if not full_file_name.exists() and not args.dry_run:
                log_entries.append(f"{generated_name}={file_name}\n")
                file_path.rename(full_file_name)
            else:
                print(f"Dry-Run rename: {file_name}  -->  {generated_name}")
    if not args.dry_run:
        log_the_changes(log_entries, args.directory_working)

if __name__ == "__main__":
    main()