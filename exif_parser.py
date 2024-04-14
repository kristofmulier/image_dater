#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script extracts the date the photo was taken from the exif data of an image file. It uses the
# exiftool command-line tool to retrieve the exif data and parses it to extract the date. The
# extracted date is returned as a datetime object.
# If the date cannot be extracted or the file does not exist, None is returned. This script can be
# run from the command line with the -f or --file option to specify the image file. If no file is
# specified, the script exits without doing anything.
#
# Example usage: python exif_parser.py -f image.jpg
#
# $ sudo apt install libimage-exiftool-perl
# $ sudo apt install python-is-python3

from typing import *
import subprocess, re, os, datetime, argparse, sys

p1 = re.compile(
    r"^([^:]+):\s+(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2})?Z?)",
    re.MULTILINE,
)

p2 = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(\.\d+)?([+-]\d{2}:\d{2}|Z)?",
)

def get_photo_taken_date(filepath: str, verbose: bool = False) -> Optional[datetime.datetime]:
    '''
    Extract the date the photo was taken from the exif data.
    '''
    date_dict = parse_exif_data(filepath, verbose)
    if not date_dict:
        return None
    # Ordered list of exif fields by their priority
    fields_priority = [
        'Date/Time Original',
        'Creation Date',
        'Media Create Date',
        'Track Create Date',
        'Create Date',
        'Date Created',
        'Modify Date',
        'File Modification Date/Time'
    ]
    for field in fields_priority:
        if field in date_dict:
            if verbose:
                print(f"Chosen field: '{field}'")
            return date_dict[field]
    return None

def parse_exif_data(filepath:str, verbose:bool=False) -> Dict[str, datetime.datetime]:
    '''
    Extract exif data from an image file.
    '''
    cmd = f'exiftool "{filepath}"'
    output = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ).communicate()[0]
    output_utf = output.decode('utf-8', errors='ignore')
    if verbose:
        print('-' * 80)
        print(output_utf)
        print('-' * 80)
    date_dict = {}
    for m in p1.finditer(output_utf):
        label = m.group(1)
        date_str = m.group(2)
        normalized_date_str = to_isoformat_with_microseconds(date_str)
        try:
            date_obj = datetime.datetime.fromisoformat(normalized_date_str)
            date_dict[label.strip()] = date_obj
        except ValueError:
            pass
        continue
    return date_dict

def to_isoformat_with_microseconds(date_str:str) -> str:
    '''
    Normalize a date string to ISO format with microseconds precision. For example:
        - '2024:04:01 05:36:42+02:00'      -> '2024-04-01 05:36:42.000000+02:00'
        - '2024:03:31 22:38:17'            -> '2024-03-31 22:38:17.000000+00:00'
        - '2022:01:01 00:00:00'            -> '2022-01-01 00:00:00.000000+00:00'
        - '2024:03:31 22:38:17.767+08:00'  -> '2024-03-31 22:38:17.767000+08:00'
        - '2024:03:31 14:38:15.29Z'        -> '2024-03-31 14:38:15.290000+00:00'
    '''
    #$ Replace colon separators in the date part to dashes if necessary
    date_str = re.sub(r'^(\d{4}):(\d{2}):(\d{2})', r'\1-\2-\3', date_str.strip())
    #$ Regex to extract the base datetime, the fractional part, and the timezone
    match = p2.match(date_str)
    if not match:
        raise ValueError("Invalid date format")
    base_datetime, fractional_seconds, timezone = match.groups()
    #$ Normalize the fractional seconds to microseconds precision
    if fractional_seconds:
        # Remove the decimal point, extend or trim to 6 digits (microseconds)
        fractional_seconds = (fractional_seconds[1:] + '000000')[:6]
        fractional_seconds = '.' + fractional_seconds
    else:
        # If no fractional part was found, append zero microseconds
        fractional_seconds = '.000000'
    #$ Normalize timezone
    if timezone == 'Z':
        timezone = '+00:00'
    elif not timezone:
        # If no timezone provided, assume UTC
        timezone = '+00:00'
    #$ Reassemble the date string into ISO format
    return f"{base_datetime}{fractional_seconds}{timezone}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Rename images based on their date.',
        add_help    = False,
    )
    parser.add_argument('-h', '--help',      action='store_true')
    parser.add_argument('-f', '--file',      action='store')
    parser.add_argument('-v', '--verbose',   action='store_true')
    args = parser.parse_args()
    if args.help:
        print('\nQuit exif parser tool\n')
        sys.exit(0)

    if args.file:
        if not os.path.isfile(args.file):
            print(f"ERROR: Cannot find file: '{args.file}'")
            sys.exit(1)
        if args.verbose:
            print('')
            print(f"Parsing exif data from: '{args.file}'")
            _date_obj = get_photo_taken_date(args.file, args.verbose)
            print(f"Date taken:   '{_date_obj}'")
        else:
            _date_obj = get_photo_taken_date(args.file, args.verbose)
            print(f"Date taken: {_date_obj}")
        sys.exit(0)
    
    print('\nQuit exif parser tool\n')
    sys.exit(0)