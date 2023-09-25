from typing import *
import subprocess, re, os, datetime, argparse, sys, traceback

# Keep a pattern to extract dates from the metadata.
p = re.compile(r'(20\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)\.(\d*)')

# Keep a dictionary with all the full filepaths as keys (guaranteed to be unique) and dates as the
# values. The dates are already converted into strings here.
filepath_dict:Dict[str, str] = {}

# Keep a flipped dictionary, with the dates as keys and the original names as values.
flipped_dict:Dict[str, List[str]] = {}

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
    filepath = filepath.replace('/', '\\')
    filepath = filepath.replace('\\', '\\\\')
    cmd = f'cmd.exe /c wmic datafile "{filepath}" list full'
    output = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ).communicate()[0]
    output_utf = output.decode('utf-8', errors='ignore')
    dates = []
    for m in p.finditer(output_utf):
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
    for root, dirs, files in os.walk(dirpath):
        for f in files:
            if not f.lower().endswith(('.heic', '.mov', '.jpeg', '.jpg', '.mp4')):
                continue
            filepath = os.path.join(root, f).replace('\\', '/')
            try:
                date_str = date_to_str(get_image_dates(filepath)[0])
            except:
                print(f'Cannot parse file: {filepath}')
                date_str = None
                traceback.print_exc()
            if date_str is not None:
                filepath_dict[filepath] = date_str
            continue
        continue

    for filepath in filepath_dict.keys():
        date_str = filepath_dict[filepath]
        cntr = 0
        if date_str not in flipped_dict.keys():
            flipped_dict[date_str] = [filepath, ]
        else:
            cntr = len(flipped_dict[date_str])
            flipped_dict[date_str].append(filepath)
        src_filepath = filepath
        dst_filepath = os.path.join(
            os.path.dirname(filepath),
            f'{date_str}-{cntr:02d}',
        ).replace('\\', '/') + os.path.splitext(filepath)[1]
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
