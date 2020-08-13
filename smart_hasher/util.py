import msvcrt
import math

# Ref: https://en.wikipedia.org/wiki/Megabyte
size_names = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")

# This function convert size in bytes to human readable presentation.
# Ref: "Better way to convert file sizes in Python" https://stackoverflow.com/a/14822210/13441
def convert_size_to_display(size_bytes: float) -> str:
   global size_names

   if size_bytes == 0:
       return "0 " + size_names[0]
   # size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_names[i])

def is_program_interrupted_by_user():
    # Ref: https://stackoverflow.com/questions/24072790/detect-key-press-in-python
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\x1b':
            print("\nExit program? (Press 'y' to exit or other key to continue)\n", end="")
            key = msvcrt.getch()
            if (key == b'y'):
                print("{0}\nProgram interrupted by user".format(str(key)))
                return True
    return False

# Returns:
#   True if pause worked fine
#   False if program interruped
def pause():
    # Ref: https://wiki.python.org/moin/ForLoop
    # Ref: https://stackoverflow.com/questions/44834493/a-single-python-loop-from-zero-to-n-to-zero
    for s in range(cmd_line_args.pause_after_file, 0, -1):
        print(f"Pause {s} seconds... Press ESC to exit program\r", end="")
        # Ref: https://www.journaldev.com/15797/python-time-sleep
        time.sleep(1)
        # Ref: https://stackoverflow.com/questions/24072790/detect-key-press-in-python
        pi = is_program_interrupted_by_user()
        if pi:
            return False;
    print(" " * 60)
    return True;

def format_seconds(seconds: float) -> str:
    # seconds = int(diff.total_seconds());
    sec = int(seconds)
    ret =  "{0}:{1:02d}:{2:02d}".format(int(sec / 60 / 60), int(sec / 60) % 60, sec % 60)
    return ret
