# Jellyfin File Renamer
Lightweight python script that reads files in a working directory, matches the file names to an input regex pattern, and renames matching files using an input dictionary

## Why
If media content is split acrosss multiple files (e.g. like an episode with 2 segments where each segment is in its own file), Jellyfin can virtually combine each file into a single unit in the UI (e.g. both segment files will appear as one episode). To do this, the file names need to follow a specific naming pattern. This script can rename file names to Jellyfin's specific naming pattern.

## How
Consider a directory with media files named like this:
- /Show Name
  - Show Name S01E01**A** Title [Optional Data].media
  - Show Name S01E01**B** Title [Optional Data].media
  - Show Name S01E02**A** Title [Optional Data].media
  - Show Name S01E02**B** Title [Optional Data].media

Even though there's 4 files, there's only 2 episodes of the show. Jellyfin won't virtually combine these files since the A and B **suffix** aren't part of the required naming pattern.
The script will rename the files like this to match the required naming pattern.
- /Show Name
  - Show Name S01E01 Title [Optional Data]__-part-1__.media
  - Show Name S01E01 Title [Optional Data]__-part-2__.media
  - Show Name S01E02 Title [Optional Data]__-part-1__.media
  - Show Name S01E02 Title [Optional Data]__-part-2__.media

## Usage

### Arguments

| short | long | required | description |
| --- | --- | --- | --- |
| -d | --directory-working | true | the working directory containing the media files to be renamed |
| -r | --regex-pattern | true | the regex pattern to identify files in the working directory to be renamed |
| -m | --mapping | true | The dictionary string mapping the old suffix to the Jellyfin approved new suffix. The old suffix will be replaced completely by the new suffix |
| | --dry-run | false | Print to the console intended rename changes instead of actually renaming files | 

#### Argument Detail
The script does this:
* Start in __working directory__
* Use __regex__ to match files with this name pattern 'Show Name [Series Coordinates][Old Suffix][Additional Text][File Extension]'
* Use __dictionary__ to map [Old Suffix] to [__New Suffix__] (e.g. A to -part-1, B to -part-2)
* Reorder the name pieces and rename the file 'Show Name [Series Coordinates][Additional Text][New Suffix][File Extension]

###### Regex Pattern 
The script expects 4 capture groups in the regex pattern to perform the rename:
- 1st capture group: Series Coordinates - Text describing the season and episode. The main match-finding muscle. e.g. S01E01, S13E04
- 2nd capture group: __Old Suffix__ - Text indicating this file is part of a single episode or similar media unit. This capture group is used to key into the dictionary and replaced by the fetched value e.g. The A after S01E01A, or the B after S13E04B
- 3rd capture group: Additional Text - any text after the series coordinates describing the file
- 4th capture group: File Extension - the extension of the file.

Any text before the first capture group is preserved.

### Examples
```bash
python .\jellyfin_file_rename.py -d .\test_data\ -r "(S\d\dE\d\d)([AB])(.*)(\.mkv)" -m '{"A": "-part-1", "B": "-part-2"}'
```

## Backup
This script writes a log file, undo_rename_log.txt, to the working directory which can be used by a separate reversal script to undo this script's naming changes.

## Limitations
- The file name breakdown is limited to 4 capture groups and the 2nd capture group gets replaced. This may not fit uses cases where media files are acquired with different naming patterns.
