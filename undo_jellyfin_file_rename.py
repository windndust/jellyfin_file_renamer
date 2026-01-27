from pathlib import Path
import argparse
from typing import Protocol

class ScriptArgs(Protocol):
    directory_working: Path

def parse_commandline_args() -> ScriptArgs:
    parser = argparse.ArgumentParser(description="Read the undo_rename_log.txt created by file_rename.py and undo the renaming of files.")
    parser.add_argument("-d", "--directory-working", required=True, type=Path, help="The working directory containing the files to undo the rename")
    return parser.parse_args()

def main():
    print("Undo File Rename Python script")
    args = parse_commandline_args()

    undo_rename_log = args.directory_working/"undo_rename_log.txt"

    if undo_rename_log.exists():
        with open(undo_rename_log, "r", encoding="utf-8") as log:
            for line in log:
                clean_line = line.strip()
                split_line = clean_line.split("=")
                current_file_name = split_line[0]
                old_file_name = split_line[1]
                file = args.directory_working/current_file_name
                if file.exists():
                    full_old_name = file.with_name(old_file_name)
                    file.rename(full_old_name)

if __name__ == "__main__":
    main()