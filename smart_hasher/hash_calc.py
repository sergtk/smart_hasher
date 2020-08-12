import hashlib
import os
from datetime import datetime
import util
import enum

class FileHashCalc(object):
    """This is a class to calculate hash for one file"""

    def __init__(self):
        self.retry_count_on_failure = 3
        self.file_name = None
        self.hash_str = "sha1"
        self.suppress_output = False
        self.file_chunk_size = 1024 * 1024
        self.result = None

    # Ref: https://docs.python.org/2/library/hashlib.html
    def __get_hasher(self, hash_str):
        # Ref: https://docs.python.org/3/library/hashlib.html#hashlib.new
        ret = hashlib.new(hash_str);
        return ret;

    # Ref: https://docs.python.org/3.7/library/enum.html
    @enum.unique
    class ReturnCode(enum.Enum):
        OK = 0
        PROGRAM_INTERRUPTED_BY_USER = 1

    def run(self):
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

        data = True
        with open(self.file_name, "rb") as f:
            while data:
                # Read and update digest.
                data = f.read(self.file_chunk_size)
                cur_size += len(data)
                hasher.update(data)

                recent_size += len(data)

                # Calculate progress.
                percent = int(10000 * cur_size / total_size)

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

                    if not self.suppress_output:
                        # Ref: "Using multiple arguments for string formatting in Python (e.g., '%s … %s')" https://stackoverflow.com/a/3395158/13441
                        # Ref: "Display number with leading zeros" https://stackoverflow.com/a/134951/13441
                        print ('{0}.{1:02d}% done ({2:,d} bytes). Remaining time: {3}. File average speed: {4}/sec. Recent speed: {5}/sec.   \r'.
                               format(int(percent / 100), int(percent % 100), cur_size, format_seconds(remain_seconds), speed_readable, recent_speed_readable),
                               end="")
                    prev_percent = percent
        if not self.suppress_output:
            print ('                                                                                      \r', end="") # Clear line
        self.result = hasher.hexdigest()
        return self.ReturnCode.OK
