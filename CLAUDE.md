# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an image processing toolkit for renaming and organizing photos based on their EXIF date metadata. The project consists of three main Python scripts that work together in a pipeline:

1. **exif_parser.py** - Extracts photo dates from EXIF metadata using the `exiftool` command
2. **image_dater.py** - Renames images to date-based filenames (YYYYMMDD-HHMMSS-XXX format)
3. **image_mover.py** - Organizes renamed images into year/month folder structure
4. **image_processer.py** - Wrapper script that runs both dater and mover in sequence

## System Requirements

- **Linux/WSL environment required** - Does not work on native Windows due to `exiftool` dependency
- `exiftool` must be installed: `sudo apt install libimage-exiftool-perl`
- Python 3 with typing support

## Common Commands

Run the complete pipeline on a directory:
```bash
python image_processer.py -d "/path/to/images" -b "/path/to/basefolder"
```

Automatically confirm prompts:
```bash
yes | python image_processer.py -d "/path/to/images" -b "/path/to/basefolder"
```

Dry run to preview changes:
```bash
python image_processer.py -d "/path/to/images" -b "/path/to/basefolder" -n -v
```

Rename only (without moving):
```bash
python image_dater.py -d "/path/to/images"
```

Move only (assumes already renamed):
```bash
python image_mover.py -d "/path/to/images" -b "/path/to/basefolder"
```

Inspect single file date:
```bash
python image_dater.py -f "/path/to/image.jpg"
```

## Architecture Notes

- **File Format Support**: .heic, .mov, .jpeg, .jpg, .mp4, .png, .webp
- **Naming Convention**: Files renamed to `YYYYMMDD-HHMMSS-XXX.ext` where XXX is a 3-digit counter
- **Organization Structure**: Images moved to `{basefolder}/Pictures_YYYY/MM_YYYY/`
- **EXIF Priority**: Uses prioritized list of EXIF fields (Date/Time Original, Creation Date, etc.)
- **Progress Bars**: All scripts show progress for large batches
- **Safety Features**: Dry-run mode, user confirmation prompts, collision detection

## Key Implementation Details

- **Configurable Base Folder**: The basefolder parameter (`-b/--basefolder`) specifies where organized images are stored
- **Argument Validation**: Both `image_processer.py` and `image_mover.py` require basefolder when processing directories
- **Progress Bar Optimization**: Uses global state to avoid redrawing at same percentage
- **Collision Prevention**: Counter incrementation ensures no filename collisions during renaming/moving
- **EXIF Parsing**: Handles various timezone formats and normalizes to ISO format with microsecond precision
- **Safety Features**: All scripts support verbose mode for debugging and dry-run for testing