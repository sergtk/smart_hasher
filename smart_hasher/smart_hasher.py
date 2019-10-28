import hashlib
import sys
import os.path
import time
from datetime import datetime
import math
import argparse
import traceback
import ntpath
import fnmatch
from collections import OrderedDict

# Ref: https://docs.python.org/2/library/hashlib.html
# Ref: https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-pythons
# Ref: https://stackoverflow.com/questions/25480089/right-way-to-initialize-an-ordereddict-using-its-constructor-such-that-it-retain
hash_algos = OrderedDict([
    ("md5", hashlib.md5()),
    ("sha1", hashlib.sha1()),
    ("sha224", hashlib.sha224()),
    ("sha256", hashlib.sha256()),
    ("sha384", hashlib.sha384()),
    ("sha512", hashlib.sha512()),
]);

hash_algo_default_str = "sha1"

file_chunk_size = 1024 * 1024
# file_chunk_size = 500

size_names = ("B", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb")


# Ref: "Better way to convert file sizes in Python" https://stackoverflow.com/a/14822210/13441
def convert_size(size_bytes: float) -> str:
   global size_names

   if size_bytes == 0:
       return "0 " + size_names[0]
   # size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_names[i])

def format_seconds(seconds: float) -> str:
    # seconds = int(diff.total_seconds());
    sec = int(seconds)
    ret =  "{0}:{1:02d}:{2:02d}".format(int(sec / 60 / 60), int(sec / 60) % 60, sec % 60)
    return ret

# Ref: https://docs.python.org/2/library/hashlib.html
def get_hasher():
    hash_str = cmd_line_args.hash_algo;
    ret = hash_algos[hash_str];
    return ret;

# Ref: https://stackoverflow.com/questions/9181859/getting-percentage-complete-of-an-md5-checksum
def calc_hash(file_name):
    cur_size = 0
    prev_percent = 0
    hasher = get_hasher()
    total_size = os.path.getsize(file_name)

    recent_moment = start_moment = datetime.now();
    recent_size = 0
    recent_speed = 0
    recent_speed_readable = "-"

    data = True
    f = open(file_name, "rb")

    while data:
        # Read and update digest.
        data = f.read(file_chunk_size)
        cur_size += len(data)
        hasher.update(data)

        recent_size += len(data)

        # Calculate progress.
        percent = int(10000 * cur_size / total_size)

        # Ref: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
        # time.sleep(1)

        if percent > prev_percent:
            cur_moment = datetime.now();
            elapsed_seconds = (cur_moment - start_moment).total_seconds()
            if (elapsed_seconds == 0):
                continue
            remain_seconds = elapsed_seconds / percent * (10000 - percent);

            speed = cur_size / elapsed_seconds;
            speed_readable = convert_size(speed);

            recent_seconds = (cur_moment - recent_moment).total_seconds()
            if (recent_seconds > 3 and recent_size > 0):
                recent_speed = recent_size / recent_seconds
                recent_speed_readable = convert_size(recent_speed)
                recent_moment = cur_moment
                recent_size = 0

            # Ref: "Using multiple arguments for string formatting in Python (e.g., '%s … %s')" https://stackoverflow.com/a/3395158/13441
            # Ref: "Display number with leading zeros" https://stackoverflow.com/a/134951/13441
            print ('{0}.{1:02d}% done ({2:,d} bytes). Remaining time: {3}. File average speed: {4}/sec. Recent speed: {5}/sec.   \r'.
                   format(int(percent / 100), int(percent % 100), cur_size, format_seconds(remain_seconds), speed_readable, recent_speed_readable),
                   end="")
            prev_percent = percent
    f.close()
    print ('                                                                                      \r', end="") # Clear line
    return hasher.hexdigest()

def get_output_file_name(input_file_name):
    output_file_name = input_file_name + "." + cmd_line_args.hash_algo

    if cmd_line_args.hash_file_name_output_postfix:
        output_file_name += "." + cmd_line_args.hash_file_name_output_postfix[0]
    return output_file_name

# Ref: "Argparse Tutorial" https://docs.python.org/3/howto/argparse.html
# Ref: "15.4.3. The add_argument() method" https://docs.python.org/2/library/argparse.html#the-add-argument-method
def parse_command_line():
    global cmd_line_args;

    parser = argparse.ArgumentParser(description='This application is to calculate hashes of files with extended features.')
    parser.add_argument('--input-file', '-if', action="append", help="Specify one or more input files")
    parser.add_argument('--input-folder', '-ifo', action="append", help="Specify one or more input folders. All files in folder are handled recursively")
    parser.add_argument('--input-folder-file-mask-include', '-ifoi', help="Specify file mask to include for input folder. All files in the folder considered if not specified. Separate multiple mask with semicolon (;)")
    parser.add_argument('--input-folder-file-mask-exclude', '-ifoe', help="Specify file mask to exclude for input folder. It is applied after --input-folder-file-mask-include. Separate multiple mask with semicolon (;)")
    parser.add_argument('--hash-file-name-output-postfix', '-op', action='append', help="Specify postfix, which will be appended to the end of output file names. This is to specify for different contextes, e.g. if file name ends with \".md5\", then it ends with \"md5.<value>\"")
    parser.add_argument('--hash-algo', help="Specify hash algo (default: {0})".format(hash_algo_default_str), default=hash_algo_default_str, choices=hash_algos.keys())

    # Ref: https://stackoverflow.com/questions/23032514/argparse-disable-same-argument-occurrences
    cmd_line_args = parser.parse_args()
    if (not cmd_line_args.input_file and not cmd_line_args.input_folder):
        parser.error("One or more input files and/or folders should be specified")
    if cmd_line_args.hash_file_name_output_postfix and len(cmd_line_args.hash_file_name_output_postfix) > 1:
        parser.error("--hash-file-name-output-postfix appears several times.")

def get_date_time_str(dateTime: datetime) -> str:
    return dateTime.strftime("%Y.%m.%d %H:%M:%S")

# Returns false if hash not calculated, probably because it was already calculated.
def handle_input_file(input_file_name):
    start_date_time = datetime.now();
    print("Handle file start time: " + get_date_time_str(start_date_time) + " (" + input_file_name + ")")
    output_file_name = get_output_file_name(input_file_name)
    # Ref: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
    if (os.path.exists(output_file_name)):
        print("Output file name '" + output_file_name + "' exists ... calculation of hash skipped.")
        return False
    print("Calculate hash for file '" + input_file_name + "'...")
    hash = calc_hash(input_file_name)

    # Ref: https://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file
    with open(output_file_name, 'a') as outputFile:
        # outputFile.write("# MD5 hash generated by smart_hasher\n\n")
        outputFile.write(hash + " *" + input_file_name + "\n")

    print("HASH: ", hash, "(" + output_file_name + ")")

    end_date_time = datetime.now();
    print("Handle file end time: " + get_date_time_str(end_date_time) + " (" + input_file_name + ")")
    seconds = int((end_date_time - start_date_time).total_seconds());
    # print("Elapsed time: {0}:{1:02d}:{2:02d}".format(int(seconds / 60 / 60), int(seconds / 60) % 60, seconds % 60))

    file_size = os.path.getsize(input_file_name)
    speed = file_size / seconds if seconds > 0 else 0
    print("Elapsed time: {0} (Average speed: {1}/sec)".format(format_seconds(seconds), convert_size(speed)))
      
    return True

def file_masks_included(file_name):
    # Ref: "Extract file name from path, no matter what the os/path format" https://stackoverflow.com/a/8384788/13441
    base_name = ntpath.basename(file_name)

    # Ref: https://docs.python.org/2/library/fnmatch.html
    # if fnmatch.fnmatch(base_name, '*.txt'):

    if (cmd_line_args.input_folder_file_mask_include):
        file_included = False
        include_masks = cmd_line_args.input_folder_file_mask_include.split(";")
        for include_mask in include_masks:
            if fnmatch.fnmatch(file_name, include_mask):
                file_included = True
                break
        if not file_included:
            return False;

    if (cmd_line_args.input_folder_file_mask_exclude):
        exclude_masks = cmd_line_args.input_folder_file_mask_exclude.split(";")
        for exclude_mask in exclude_masks:
            if fnmatch.fnmatch(file_name, exclude_mask):
                return False;
    return True;

def handle_input_files():
    if (cmd_line_args.input_file):
        for input_file_name in cmd_line_args.input_file:
            handle_input_file(input_file_name)

    if (cmd_line_args.input_folder):
        # Ref: https://docs.python.org/3/library/os.html#os.walk
        # Ref: https://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
        for input_folder in cmd_line_args.input_folder:
            for dir_name, subdir_list, file_list in os.walk(input_folder):
                for base_file_name in file_list:
                    input_file_name = os.path.join(dir_name, base_file_name)
                    if not file_masks_included(input_file_name):
                        continue
                    # print("{0} -> {1}".format(dir_name, base_file_name));
                    handle_input_file(input_file_name)

try:
    parse_command_line()

    handle_input_files()

except Exception as ex:
    # Ref: https://stackoverflow.com/a/4564595/13441
    # Wierd that `ex` is not used
    print(traceback.format_exc())

    # Short message
    # print("Exception thrown:\n", ex)
