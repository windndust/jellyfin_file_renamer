import argparse
from pathlib import Path
import re
import json
import typing

class ScriptArgs(typing.Protocol):
    directory_working: Path
    regex_pattern: re.Pattern
    episode_count: int
    dry_run: bool

def parse_commandline_args() -> ScriptArgs:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-d", "--directory-working", required=True, type=Path, help="")
    parser.add_argument("-r", "--regex-pattern", required=True, type=re.compile, help="")
    parser.add_argument("-e", "--episode-count", default=1, type=int, help="")
    parser.add_argument("--dry-run", action="store_true", help="")
    return parser.parse_args()

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
    print("Start")
    args=parse_commandline_args()
    print(f"Passed in arguments::  Directory Working={args.directory_working}, Regex Pattern={args.regex_pattern}")

    log_entries = []
    episode_count=args.episode_count
    files = sorted(list(args.directory_working.iterdir()))
    for file in files:

        if not file.is_file or file.name.startswith("undo"):
            continue

        match = args.regex_pattern.search(file.name)
        print(f"match found {match:}")
        if match:
            start, end = match.span()
            season_count=match.group(1)
            extra_text=match.group(3)
            new_name_piece=f"{season_count}E{episode_count:02d}{extra_text}"
            new_name=file.name[:start]+new_name_piece+file.name[end:]
            episode_count+=1
            if not args.dry_run:
                log_entries.append(f"{new_name}={file.name}\n")
                file.rename(file.with_name(new_name))
            else:
                print(f"Dry-Run rename: {file.name}  -->  {new_name}")
    if not args.dry_run:
        log_the_changes(log_entries, args.directory_working)

    print("Script End")

if __name__ == "__main__":
    main()