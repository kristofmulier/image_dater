#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import *
import re, os, datetime, argparse, sys, shutil
basefolder = '/mnt/c/Backup'



def show_help() -> None:
    '''
    Print help info and quit.
    '''
    print('Move images based on their date.')

def date_to_str(date_obj:datetime.datetime) -> str:
    '''
    Convert the date object to a string like:
    '20230601-184100'
    This is the string format used for filenames by the 'image_dater.py' script (to which a counter
    is appended).
    '''
    return date_obj.strftime('%Y%m%d-%H%M%S')

def move_images(dirpath:str, dry_run:bool=False) -> None:
    '''
    Parse the given folder for images and move them if they're already converted by the
    'image_dater.py' script.
    '''
    # The following pattern matches with filenames that are already converted by the
    # 'image_dater.py' script.
    p = re.compile(r'(20\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)-(\d+)')

    # First fill a list with all the files that are already converted by the 'image_dater.py'
    # script.
    filepath_list:List[str] = []
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            if not f.lower().endswith(('.heic', '.mov', '.jpeg', '.jpg', '.mp4', '.png')):
                continue
            filepath = os.path.join(root, f).replace('\\', '/')
            filename = filepath.split('/')[-1]
            m = p.search(filename)
            if m is None:
                continue
            filepath_list.append(filepath)
            continue
        continue

    # Now loop over the list and move the files
    for filepath in filepath_list:
        assert os.path.isfile(filepath)
        filename = filepath.split('/')[-1]
        m = p.search(filename)
        assert m is not None
        year_str   = m.group(1)
        month_str  = m.group(2)
        day_str    = m.group(3)
        hour_str   = m.group(4)
        minute_str = m.group(5)
        second_str = m.group(6)
        cntr_str   = m.group(7)
        filedate = datetime.datetime(
            year   = int(year_str),
            month  = int(month_str),
            day    = int(day_str),
            hour   = int(hour_str),
            minute = int(minute_str),
            second = int(second_str),
        )

        # Compute ideal destination path
        src_filepath   = filepath
        dst_filepath   = f'{basefolder}/Pictures_{year_str}/{month_str}_{year_str}/{filename}'
        dst_folderpath = os.path.dirname(dst_filepath).replace('\\', '/')

        # Source and ideal destination paths are already identical. No need to move anything.
        # Continue to next file.
        if src_filepath == dst_filepath:
            print(f'GOOD: {src_filepath}')
            continue

        # Maybe another file is already at the ideal destination path. Increase a counter in the
        # filename before moving this file.
        if os.path.isfile(dst_filepath):
            cntr = int(cntr_str)
            while True:
                dst_filepath = str(
                    f'{dst_folderpath}/'
                    f'{date_to_str(filedate)}-{cntr:03d}.'
                    f'{os.path.splitext(filename)}'
                )
                if os.path.exists(dst_filepath):
                    cntr += 1
                    continue
                break

        # At this point, we know that the current file must be moved to 'dst_filepath' and the
        # destination doesn't exist yet (the cntr ensured that). Move the file now.
        assert not os.path.exists(dst_filepath)
        if not os.path.isdir(dst_folderpath):
            print(f'CREATE: {dst_folderpath}')
            if not dry_run:
                os.makedirs(dst_folderpath)
        print(f'MOVE: {src_filepath} => {dst_filepath}')
        sys.stdout.flush()
        if not dry_run:
            shutil.move(src_filepath, dst_filepath)
        continue
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Move images based on their date.',
        add_help    = False,
    )
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-d', '--directory', action='store')
    parser.add_argument('-n', '--dry-run',   action='store_true')
    args = parser.parse_args()

    #& Sanitize input
    if not args.help and not args.directory:
        print('ERROR: No action specified')
        show_help()
        sys.exit(1)

    #& Show help and quit
    if args.help:
        show_help()
        print('\nQuit image mover tool\n')
        sys.exit(0)

    #& Parse directory and move images
    if args.directory is not None:
        if not os.path.isdir(args.directory):
            print(f"ERROR: Cannot find directory: '{args.directory}'")
            sys.exit(1)
        user_input = input(
            f"Process the pictures from this folder:\n"
            f"'{args.directory}'\n"
            f"and store them at this location:\n"
            f"'{basefolder}'\n"
            f"Proceed? [yes|no]\n"
        )
        if user_input.lower() in ('y', 'yes'):
            move_images(args.directory, args.dry_run)
        print('\nQuit image mover tool\n')
        sys.exit(0)

    show_help()
    print('\nQuit image mover tool\n')
    sys.exit(0)