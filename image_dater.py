from typing import *
import subprocess, re, os, datetime, argparse, sys, traceback
import exif_parser

def show_help() -> None:
    '''
    Print help info and quit.
    '''
    print('Rename images based on their date.')
    print('Usage:')
    print('    python image_dater.py -h')
    print('    python image_dater.py -d <directory>')
    print('    python image_dater.py -f <file> [-v]')
    print('Options:')
    print('    -h, --help                  Show this help message and exit.')
    print('')
    print('    -d, --directory <directory> All images in the directory and its subdirectories will')
    print('                                be parsed and renamed according to their date.')
    print('')
    print('    -f, --file <file>           Specify a file to investigate. Show its date taken.')
    print('')
    print('    -v, --verbose               Print more information.')
    print('')
    print('    -n, --dry-run               Do not rename files. Only show what would be done.')
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
            if not f.lower().endswith(('.heic', '.mov', '.jpeg', '.jpg', '.mp4', '.png')):
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
    Convert the date object to a string.
    '''
    return date_obj.strftime('%Y%m%d-%H%M%S')

progbar_percent:Optional[int] = None
def draw_progress_bar(total:int, progress:int, label:str):
    """
    Draws a progress bar to the console.

    Args:
        total (int): The total count of the operation (i.e., 100% completion).
        progress (int): The current progress count.
        bar_length (int): Length of the progress bar in characters. Default is 50.
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
            print('ERROR: No action specified.')
            show_help()
            print('\nQuit image dater tool\n')
            sys.exit(0)
    if args.directory and args.file:
        print('ERROR: Cannot use both -d and -f options at the same time.')
        print('\nQuit image dater tool\n')
        sys.exit(0)

    #& Show help and quit
    if args.help:
        show_help()
        print('\nQuit image dater tool\n')
        sys.exit(0)

    #& Parse directory
    if args.directory:
        if not os.path.isdir(args.directory):
            print(f"ERROR: Cannot find directory: '{args.directory}'")
            print('\nQuit image dater tool\n')
            sys.exit(1)
        parse_and_rename_images(args.directory, args.dry_run, args.verbose)
        print('\nQuit image dater tool\n')
        sys.exit(0)

    #& Inspect file
    if args.file:
        if not os.path.isfile(args.file):
            print(f"ERROR: Cannot find file: '{args.file}'")
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