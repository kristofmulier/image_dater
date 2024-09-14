#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script renames images based on their date. It parses the exif data of each image file to
# extract the date the photo was taken. The date is then used to rename the image file. The renaming
# is done in the same directory as the original file. The new filename consists of the date and a
# counter to ensure uniqueness.

from typing import *
import os, datetime, argparse, sys, subprocess
import exif_parser

def show_help() -> None:
    '''
    Print help info and quit.
    '''
    print('')
    print('IMAGE DATER')
    print('===========')
    print('This script renames images based on their date. It parses the exif data of each image')
    print('file to extract the date the photo was taken. The date is then used to rename the image')
    print('file. The renaming is done in the same directory as the original file. The new filename')
    print('consists of the date and a counter to ensure uniqueness.')
    print('')
    print('Usage:')
    print('------')
    print('    python image_dater.py -h')
    print('    python image_dater.py -d <directory> [-v] [-n]')
    print('    python image_dater.py -f <file> [-v]')
    print('')
    print('Options:')
    print('--------')
    print('    -h, --help                  Show this help message and exit.')
    print('')
    print('    -d, --directory <directory> Rename all images in the given directory and its sub-')
    print('                                directories according to their dates.')
    print('')
    print('    -f, --file <file>           Show the date the photo was taken for the given file (no')
    print('                                renaming).')
    print('')
    print('    -v, --verbose               Print more information.')
    print('')
    print('    -n, --dry-run               Do not rename files. Only show what would be done.')
    print('')
    print('Notes:')
    print('------')
    print('The script uses the exiftool command-line tool to extract the exif data from the image')
    print('files. Unfortunately this tool is not available on Windows. You can use the Windows')
    print('Subsystem for Linux (WSL) to run the script.')
    print('')
    print('Example:')
    print('--------')
    print('Open WSL and navigate to the folder containing this script:')
    print('    $ cd /mnt/c/Users/krist/Documents/image_dater')
    print('')
    print('Launch this script with the directory containing the images to process. Tip: use the')
    print('yes command to automatically confirm:')
    print('    $ yes | python image_dater.py -d "/mnt/c/Backup/Pictures_2024/unordered"')
    print('')
    return

def parse_and_rename_images(dirpath:str, dry_run:bool=False, verbose:bool=False) -> None:
    '''
    Parse the given folder and its subfolders for images and date them. Then rename the images based
    on those dates, but keep the file extension intact.
    '''
    # First, count the number of files in the directory and its subdirectories. This will be used to
    # draw a progress bar.
    file_count:int = 0
    for root, dirs, files in os.walk(dirpath):
        file_count += len(files)

    # Create a dictionary to store the filepath-date pairs. Filepaths are guaranteed to be unique.
    # The dates are stored in this dictionary as strings. To fill this dictionary, the exif data of
    # each image file is parsed. That requires some time - so we draw a progress bar.
    filepath_date_dict:Dict[str, str] = {}
    file_cntr:int = 0
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            file_cntr += 1
            draw_progress_bar(
                total    = file_count,
                progress = file_cntr,
                label    = 'Parse files ',
            )
            if not f.lower().endswith(('.heic', '.mov', '.jpeg', '.jpg', '.mp4', '.png', '.webp')):
                continue
            filepath = os.path.join(root, f).replace('\\', '/')
            filename = filepath.split('/')[-1]
            date_str:Optional[str] = None
            try:
                date_str = date_to_str(exif_parser.get_photo_taken_date(filepath))
            except:
                print(f'Cannot parse file: {filepath}')
                sys.stdout.flush()
                date_str = None
                # traceback.print_exc()
            if date_str is not None:
                filepath_date_dict[filepath] = date_str
            continue
        continue
    print('')

    # Loop through the 'filepath_date_dict' and rename the files according to their dates. The re-
    # naming is done in the same directory as the original file. The computed filename results from
    # appending the date string to a counter. If the computed filename already exists, the counter
    # is incremented until a unique filename is found.
    # However, if the computed filename equals the current one - then the file is already named
    # correctly. In this case, the file is not renamed.
    file_count = len(filepath_date_dict)
    file_cntr = 0
    for filepath in filepath_date_dict.keys():
        file_cntr += 1
        date_str = filepath_date_dict[filepath]
        src_filepath = filepath
        cntr = 0
        dst_filepath = None
        while True:
            dst_filepath = os.path.join(
                os.path.dirname(filepath),
                f'{date_str}-{cntr:03d}',
            ).replace('\\', '/') + os.path.splitext(filepath)[1]
            if not os.path.exists(dst_filepath):
                break
            if dst_filepath == src_filepath:
                break
            cntr += 1
            continue
        assert dst_filepath is not None
        if dst_filepath == src_filepath:
            if verbose:
                print(f'GOOD: {src_filepath}')
                sys.stdout.flush()
            else:
                draw_progress_bar(
                    total    = file_count,
                    progress = file_cntr,
                    label    = 'Rename files',
                )
            continue
        assert not os.path.exists(dst_filepath)
        if verbose:
            print(f'RENAME: {src_filepath} => {dst_filepath}')
            sys.stdout.flush()
        else:
            draw_progress_bar(
                total    = file_count,
                progress = file_cntr,
                label    = 'Rename files',
            )
        if not dry_run:
            os.rename(src_filepath, dst_filepath)
        continue
    print('')
    return

def date_to_str(date_obj:datetime.datetime) -> str:
    '''
    Convert the date object to a string. This is the string format used for the new filename (to
    which a counter is appended).
    '''
    return date_obj.strftime('%Y%m%d-%H%M%S')

progbar_percent:Optional[int] = None
def draw_progress_bar(total:int, progress:int, label:str):
    """
    Draws a progress bar to the console.

    Args:
        total (int): The total count of the operation (i.e., 100% completion).
        progress (int): The current progress count.
    """
    bar_length:int=50
    global progbar_percent
    # Calculate percentage completion
    percent = int((progress / total) * 100)
    if percent == progbar_percent:
        # No need to draw again
        return
    # Calculate the number of filled positions
    filled_length = int(bar_length * progress // total)
    # Create the bar string
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    # Print the progress bar with carriage return
    sys.stdout.write(f'\r{label}: |{bar}| {percent}%')
    sys.stdout.flush()
    progbar_percent = percent
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Rename images based on their date.',
        add_help    = False,
    )
    parser.add_argument('-h', '--help',      action='store_true')
    parser.add_argument('-d', '--directory', action='store')
    parser.add_argument('-f', '--file',      action='store')
    parser.add_argument('-v', '--verbose',   action='store_true')
    parser.add_argument('-n', '--dry-run',   action='store_true')
    args = parser.parse_args()

    #& Sanitize input
    if not args.help and not args.directory and not args.file:
            print('')
            print('ERROR: No action specified.')
            show_help()
            print('\nQuit image dater tool\n')
            sys.exit(1)
    if args.directory and args.file:
        print('')
        print('ERROR: Cannot use both -d and -f options at the same time.')
        print('\nQuit image dater tool\n')
        sys.exit(1)

    #& Show help and quit
    if args.help:
        show_help()
        print('\nQuit image dater tool\n')
        sys.exit(0)

    #& Test exiftool
    cmd = f'exiftool -ver'
    output = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ).communicate()
    stdout = output[0].decode('utf-8', errors='ignore').lower()
    stderr = output[1].decode('utf-8', errors='ignore').lower()
    if 'not recognized' in stdout or 'not recognized' in stderr:
        print('')
        print('ERROR: exiftool is not installed. Make sure you are on either Linux or WSL')
        print('(Windows Subsystem for Linux). The tool doesn\'t work on Windows.')
        print('\nQuit image dater tool\n')
        sys.exit(1)

    #& Parse directory and rename images
    if args.directory:
        if not os.path.isdir(args.directory):
            print('')
            print(f"ERROR: Cannot find directory: '{args.directory}'")
            if args.directory.startswith('C:/'):
                print('')
                print('The path looks like a Windows path. Make sure you are on Linux or WSL')
                print('(Windows Subsystem for Linux). The tool doesn\'t work on Windows. Paths')
                print('on WSL should start with \'/mnt/c/...\'')
            print('\nQuit image dater tool\n')
            sys.exit(1)
        
        # Parsing a directory in dry-run mode without being verbose is pointless.
        if args.dry_run and not args.verbose:
            print('')
            print('Forcing verbose mode because dry-run mode is enabled...')
            print('')
            args.verbose = True

        # Only ask user input if not in dry-run mode
        user_input = ''
        if not args.dry_run:
            user_input = input(
                f"Rename the pictures in this folder:\n"
                f"'{args.directory}'\n"
                f"Proceed? [yes|no]\n"
            )
        if (user_input.lower() in ('y', 'yes')) or args.dry_run:
            parse_and_rename_images(args.directory, args.dry_run, args.verbose)
        print('\nQuit image dater tool\n')
        sys.exit(0)

    #& Inspect file
    if args.file:
        if args.dry_run:
            print('')
            print('ERROR: Cannot use the -n option with the -f option. With the -f option, you')
            print('only want to inspect the date of a single file. No renaming happens. So this')
            print('is by definition always a dry run.')
            print('\nQuit image dater tool\n')
            sys.exit(1)
        if not os.path.isfile(args.file):
            print('')
            print(f"ERROR: Cannot find file: '{args.file}'")
            if args.file.startswith('C:/'):
                print('')
                print('The path looks like a Windows path. Make sure you are on Linux or WSL')
                print('(Windows Subsystem for Linux). The tool doesn\'t work on Windows. Paths')
                print('on WSL should start with \'/mnt/c/...\'')
            print('\nQuit image dater tool\n')
            sys.exit(1)
        if args.verbose:
            print('')
            print(f"Parsing exif data from: '{args.file}'")
            _date_obj = exif_parser.get_photo_taken_date(args.file, args.verbose)
            print(f"Date taken:   '{_date_obj}'")
        else:
            _date_obj = exif_parser.get_photo_taken_date(args.file, args.verbose)
            print(f"Date taken: {_date_obj}")
        print('\nQuit image dater tool\n')
        sys.exit(0)
    
    show_help()
    print('\nQuit image dater tool\n')
    sys.exit(0)