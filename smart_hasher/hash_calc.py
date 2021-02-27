import hashlib
import os
from datetime import datetime
import util
import enum
import time
import random
import sys

class FileHashCalc(object):
    """This is a class to calculate hash for one file"""

    hash_algos = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512");
    hash_algo_default_str = "sha1"

    def __init__(self):
        self.file_name = None
        self.hash_str = FileHashCalc.hash_algo_default_str
        self.suppress_console_reporting_output = False
        self.file_chunk_size = 1024 * 1024
        self.result = None
        self.retry_count_on_data_read_error = 5
        self.retry_pause_on_data_read_error = 60 # in seconds

    # Ref: https://docs.python.org/2/library/hashlib.html
    def __get_hasher(self, hash_str):
        # Ref: https://docs.python.org/3/library/hashlib.html#hashlib.new
        ret = hashlib.new(hash_str);
        return ret;

    # Ref: https://docs.python.org/3.7/library/enum.html
    @enum.unique
    class ReturnCode(enum.IntEnum):
        """
        Return codes of run() function
        """
        OK = 0
        PROGRAM_INTERRUPTED_BY_USER = 8
        DATA_READ_ERROR = 9 # Error when reading data from file. This may be caused by network issues, and retrying does not help

    def _info(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self.suppress_console_reporting_output:
            return
        print(*objects, sep=sep, end=end, file=file, flush=flush)

    def _run_single(self):
        """
        Ref: https://stackoverflow.com/questions/9181859/getting-percentage-complete-of-an-md5-checksum
        """

        self.result = None
        
        if self.file_name is None:
            raise Exception("File name is not specified")

        cur_size = 0
        prev_percent = 0
        hasher = self.__get_hasher(self.hash_str)
        total_size = os.path.getsize(self.file_name)

        recent_moment = start_moment = datetime.now();
        recent_size = 0
        recent_speed = 0
        recent_speed_readable = "-"
        
        con_report_len = 0

        data = True
        with open(self.file_name, "rb") as f:
            while data:
                #time.sleep(random.random())
                #time.sleep(0.3)
                # Read and update digest.
                data = f.read(self.file_chunk_size)
                cur_size += len(data)
                hasher.update(data)

                recent_size += len(data)

                # Calculate progress.
                if total_size > 0:
                    percent = int(10000 * cur_size / total_size)
                else:
                    percent = 0

                #if percent > 1000:
                #    raise OSError(10, "Dummy error", "dummfilename.txt")

                if util.is_program_interrupted_by_user():
                    return self.ReturnCode.PROGRAM_INTERRUPTED_BY_USER

                # Ref: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
                # time.sleep(1)

                if percent > prev_percent:
                    cur_moment = datetime.now();
                    elapsed_seconds = (cur_moment - start_moment).total_seconds()
                    if (elapsed_seconds == 0):
                        continue
                    remain_seconds = elapsed_seconds / percent * (10000 - percent);

                    speed = cur_size / elapsed_seconds;
                    speed_readable = util.convert_size_to_display(speed);

                    recent_seconds = (cur_moment - recent_moment).total_seconds()
                    if (recent_seconds > 3 and recent_size > 0):
                        recent_speed = recent_size / recent_seconds
                        recent_speed_readable = util.convert_size_to_display(recent_speed)
                        recent_moment = cur_moment
                        recent_size = 0

                    # Ref: "Using multiple arguments for string formatting in Python (e.g., '%s … %s')" https://stackoverflow.com/a/3395158/13441
                    # Ref: "Display number with leading zeros" https://stackoverflow.com/a/134951/13441
                    con_report = '{0}.{1:02d}% done ({2:,d} bytes). Remaining time: {3}. File average speed: {4}/sec. Recent speed: {5}/sec.'. \
                            format(int(percent / 100), int(percent % 100), cur_size, util.format_seconds(remain_seconds), speed_readable, recent_speed_readable);
                    con_report_len_new = len(con_report)
                    if con_report_len_new < con_report_len:
                        con_report += " " * (con_report_len - con_report_len_new)
                    con_report_len = con_report_len_new
                    self._info(f"{con_report}\r", end="")
                    prev_percent = percent
        self._info(" " * con_report_len + "\r", end="") # Clear line
        self.result = hasher.hexdigest()
        return self.ReturnCode.OK

    def run(self):
        """
        This is a main function of the class, which should be called after setup of all parameters
        """

        for cur_try in range(1, self.retry_count_on_data_read_error + 1):
            # Ref: https://stackoverflow.com/questions/2083987/how-to-retry-after-exception
            try:
                res = self._run_single()
                return res
            except OSError as err:
                self._info()
                self._info(f"OS Error. {type(err)}: {err.strerror} (errno = {err.errno}, filename = {err.filename})")
                if (not util.pause(self.retry_pause_on_data_read_error)):
                    return self.ReturnCode.PROGRAM_INTERRUPTED_BY_USER
                if cur_try < self.retry_count_on_data_read_error:
                    self._info(f"Retry {cur_try + 1} of {self.retry_count_on_data_read_error}")
                else:
                    self._info(f"Skip file. The hash for it can't be calculated due to the errors.\n")
                    return self.ReturnCode.DATA_READ_ERROR
