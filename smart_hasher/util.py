import msvcrt
import math
import time
import os
import datetime

# Ref: https://en.wikipedia.org/wiki/Megabyte
size_names = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")

def convert_size_to_display(size_bytes: float) -> str:
    """
    This function convert size in bytes to human readable presentation.

    Ref: "Better way to convert file sizes in Python" https://stackoverflow.com/a/14822210/13441
    """

    # global size_names

    if size_bytes == 0:
        return "0 " + size_names[0]

    if size_bytes < 0:
        sign = "-"
        size_bytes = -size_bytes
    else:
        sign = ""

    if size_bytes == math.inf:
        return f"{sign}infinity"

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{sign}{s} {size_names[i]}"

def is_program_interrupted_by_user():
    """
    Ref: https://stackoverflow.com/questions/24072790/detect-key-press-in-python
    """
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\x1b':
            print("\nExit program? (Press 'y' to exit or other key to continue)\n", end="")
            key = msvcrt.getch()
            if (key == b'y'):
                print("{0}\nProgram interrupted by user".format(str(key)))
                return True
    return False

def pause(pause_duration = 30):
    """
    Pause with support of interruption by user

    pause_duration - duration of pause, seconds.
    Returns:
        True if pause worked fine
        False if program interruped

    Ref: https://wiki.python.org/moin/ForLoop
    Ref: https://stackoverflow.com/questions/44834493/a-single-python-loop-from-zero-to-n-to-zero
    """
    for s in range(pause_duration, 0, -1):
        print(f"Pause {s} seconds before continue program execution... Press ESC to exit program\r", end="")
        # Ref: https://www.journaldev.com/15797/python-time-sleep
        time.sleep(1)
        # Ref: https://stackoverflow.com/questions/24072790/detect-key-press-in-python
        pi = is_program_interrupted_by_user()
        if pi:
            return False
    if pause_duration > 0:
        print(" " * 60)
    return True

def format_seconds(seconds: float) -> str:
    """    
    seconds = int(diff.total_seconds());
    """

    sec = int(seconds)
    ret =  "{0}:{1:02d}:{2:02d}".format(int(sec / 60 / 60), int(sec / 60) % 60, sec % 60)
    return ret

def rel_file_path(work_file_name, base_file_name, return_absolute_path = False):
    """
    Note, last part after slash in input file names are considered as file name, not a folder

    if return_absolute_path == False
        then returns file with path for `work_file_name` relative to `base_file_name`.
        In other words this function show how to traverse from one file to other.
        Note, if `work_file_name` and `base_file_name` point to different disks then relative path can't be returned, so absolute path returned.

    if return_absolute_path == True
        then returns absolute path for `work_file_name`
        if `work_file_name` is relative than it is considered as relative to `base_file_name`,
        and function return absolute path accounting this.
        if `work_file_name` is absolute than it is returned.

    Ref: https://stackoverflow.com/questions/10149263/extract-a-part-of-the-filepath-a-directory-in-python
    Ref: https://stackoverflow.com/a/7288073/13441
    """

    base_dir = os.path.dirname(os.path.abspath(base_file_name))

    if return_absolute_path:
        if os.path.isabs(work_file_name):
            return work_file_name
        work_abs_path = os.path.join(base_dir, work_file_name)
        work_abs_path = os.path.abspath(work_abs_path)
        return work_abs_path

    if not os.path.isabs(work_file_name):
        return work_file_name

    work_full = os.path.abspath(work_file_name)
    work_dir = os.path.dirname(work_full)
    work_file = os.path.basename(work_full)

    # Ref: https://stackoverflow.com/questions/22328350/check-that-a-string-starts-with-a-drive-letter-in-python
    # Ref: https://www.geeksforgeeks.org/python-os-path-splitdrive-method/
    # Ref: https://docs.python.org/3/library/os.path.html#os.path.splitdrive
    work_drive, _ = os.path.splitdrive(work_dir)
    base_drive, _ = os.path.splitdrive(base_dir)
    if os.path.normcase(work_drive) == os.path.normcase(base_drive):
        work_rel =  os.path.relpath(work_dir, base_dir)
    else:
        # if drives differs it is not possible to get relative path, so path returned unchanged
        work_rel = work_dir

    ret = work_file
    if work_rel != ".":
        ret = str(os.path.join(work_rel, ret))

    return ret

def drive_normcase(path):
    """
    Norm case for drive letter.
    Note this is not the same as `normcase()` for path.
    """
    drive, tail = os.path.splitdrive(path)
    drive = drive.upper()
    ret = os.path.join(drive, tail)
    return ret

def get_datetime_str(dt: datetime) -> str:
    if dt is None:
        return "-"
    ret = dt.strftime("%Y.%m.%d %H:%M:%S")
    return ret

# Ref: https://stackoverflow.com/a/8907269/13441
def get_timedelta_str(td: datetime.timedelta) -> str:
    if td is None:
        return "-"
    hours, min_sec = divmod(td.seconds, 3600)
    hours += td.days * 24
    mins, secs = divmod(min_sec, 60)
    ret = ""
    if hours > 0:
        ret += f"{hours}:"
    ret += f"{mins:02}:{secs:02}"
    return ret

class AppUsageError(Exception):
    """
    This exception is raised when error occurs due to the incorrect usage of the application by user

    Ref: https://docs.python.org/3/library/exceptions.html
    Ref: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
    """

class ProcessingTimeEstimator(object):

    class Result(object):
        def __init__(self):
            self.elapsed_duration = None
            self.estimated_duration_remains = None
            self.estimated_end_time = None

        def get_str(self):
            estimated_end_time_str = get_datetime_str(self.estimated_end_time)
            elapsed_duration_str = get_timedelta_str(self.elapsed_duration)
            estimated_duration_remains_str = get_timedelta_str(self.estimated_duration_remains)
            ret = f"Elapsed time for program run: {elapsed_duration_str}. Estimated duration to completion: {estimated_duration_remains_str}, datetime: {estimated_end_time_str}"
            return ret

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.total_size = 0
        self.handled_size = 0

    def reset_start_time(self, start_time = None):
        if start_time is None:
            self.start_time = datetime.datetime.now()
        else:
            self.start_time = start_time

    def inc_total_size(self, size):
        self.total_size += size

    def inc_total_size_with_files(self, file_name_list):
        for file_name in file_name_list:
            self.total_size += os.path.getsize(file_name)

    def inc_handled_size(self, size):
        self.handled_size += size

    def get_result(self, cur_time = None):
        if cur_time is None:
            cur_time = datetime.datetime.now()
        passed_duration = cur_time - self.start_time
        remained_size = self.total_size - self.handled_size
        ret = self.Result()
        if self.handled_size == 0:
            return ret
        ret.elapsed_duration = passed_duration
        ret.estimated_duration_remains = passed_duration * (remained_size / self.handled_size)
        ret.estimated_end_time = cur_time + ret.estimated_duration_remains
        return ret