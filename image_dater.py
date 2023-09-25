from typing import *
import subprocess, re, os, datetime, argparse, sys, traceback

# Keep a pattern to extract dates from the metadata.
p1 = re.compile(r'(20\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)\.(\d*)')

# The following pattern matches with filenames that are already converted by this script.
p2 = re.compile(r'(20\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)-(\d\d)')

# Keep a dictionary with all the full filepaths as keys (guaranteed to be unique) and dates as the
# values. The dates are already converted into strings here.
filepath_dict:Dict[str, str] = {}

def show_help() -> None:
    '''
    Print help info and quit.
    '''
    print('Rename images based on their date.')

def date_to_str(date_obj:datetime.datetime) -> str:
    '''
    Convert the date object to a string.
    '''
    return date_obj.strftime('%Y%m%d-%H%M%S')

def get_image_dates(filepath) -> List[datetime.datetime]:
    '''
    Extract dates from the given image.
    '''
    # First check if the date can be extracted from the name. If so, just return that date in a one-
    # element list.
    filename = filepath.split('/')[-1]
    m = p2.search(filename)
    if m is not None:
        return [
            datetime.datetime(
                year   = int(m.group(1)),
                month  = int(m.group(2)),
                day    = int(m.group(3)),
                hour   = int(m.group(4)),
                minute = int(m.group(5)),
                second = int(m.group(6)),
            ),
        ]
    # Extract the date(s) from the metadata, then return them in a sorted list (eldest ones first).
    filepath_bsl = filepath.replace('/', '\\')
    filepath_bsl = filepath_bsl.replace('\\', '\\\\')
    cmd = f'cmd.exe /c wmic datafile "{filepath_bsl}" list full'
    output = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ).communicate()[0]
    output_utf = output.decode('utf-8', errors='ignore')
    dates = []
    for m in p1.finditer(output_utf):
        try:
            dates.append(
                datetime.datetime(
                    year        = int(m.group(1)),
                    month       = int(m.group(2)),
                    day         = int(m.group(3)),
                    hour        = int(m.group(4)),
                    minute      = int(m.group(5)),
                    second      = int(m.group(6)),
                    microsecond = int(m.group(7)),
                )
            )
        except ValueError:
            dates.append(
                datetime.datetime(
                    year        = int(m.group(1)),
                    month       = int(m.group(2)),
                    day         = int(m.group(3)),
                    hour        = int(m.group(4)),
                    minute      = int(m.group(5)),
                    second      = int(m.group(6)),
                    microsecond = 0,
                )
            )
    return sorted(dates)

def parse_images(dirpath):
    '''
    Parse the given folder for images and date them.
    '''
    # First fill the dictionary 'filepath_dict' with filepath-date pairs.
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            if not f.lower().endswith(('.heic', '.mov', '.jpeg', '.jpg', '.mp4', '.png')):
                continue
            filepath = os.path.join(root, f).replace('\\', '/')
            filename = filepath.split('/')[-1]
            try:
                date_str = date_to_str(get_image_dates(filepath)[0])
            except:
                print(f'Cannot parse file: {filepath}')
                sys.stdout.flush()
                date_str = None
                traceback.print_exc()
            if date_str is not None:
                filepath_dict[filepath] = date_str
            continue
        continue

    # Now loop through the 'filepath_dict' and eliminate all the files from the dictionary that are
    # clearly already parsed in a previous run of this script. They don't need to be renamed once
    # again, obviously.
    for filepath in list(filepath_dict.keys()):
        filename = filepath.split('/')[-1]
        m = p2.search(filename)
        if m is not None:
            del filepath_dict[filepath]
            print(f'SKIP: {filepath}')
            sys.stdout.flush()
        continue

    # Loop again through the 'filepath_dict' and rename the files according to their dates. 
    for filepath in filepath_dict.keys():
        date_str = filepath_dict[filepath]
        src_filepath = filepath
        cntr = 0
        dst_filepath = None
        while True:
            dst_filepath = os.path.join(
                os.path.dirname(filepath),
                f'{date_str}-{cntr:02d}',
            ).replace('\\', '/') + os.path.splitext(filepath)[1]
            if os.path.exists(dst_filepath):
                cntr += 1
                continue
            break
        assert dst_filepath is not None
        assert not os.path.exists(dst_filepath)
        print(f'RENAME: {src_filepath} => {dst_filepath}')
        sys.stdout.flush()
        os.rename(src_filepath, dst_filepath)
        continue
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Rename images based on their date.',
        add_help    = False,
    )
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-d', '--directory', action='store')
    args = parser.parse_args()
    if args.help:
        show_help()
    if args.directory is not None:
        parse_images(args.directory)

    print('\nQuit image dater tool\n')
