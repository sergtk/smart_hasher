import sys
import os.path
import time
from datetime import datetime
import math
import traceback
import ntpath
import fnmatch
import hash_calc
import util
import enum
from pprint import pprint
import hash_storages
import cmd_line

def get_hash_file_name_postfix():
    global cmd_line_args

    postfix = ""

    if not cmd_line_args.suppress_hash_file_name_postfix:
        postfix += "." + cmd_line_args.hash_algo

    if cmd_line_args.add_output_file_name_timestamp:
        postfix += "." + start_time_dic["file_postfix"]

    if cmd_line_args.hash_file_name_output_postfix:
        postfix += "." + cmd_line_args.hash_file_name_output_postfix[0]

    return postfix

def get_date_time_str(dateTime: datetime) -> str:
    return dateTime.strftime("%Y.%m.%d %H:%M:%S")

def handle_input_file(hash_storage: hash_storages.HashStorageAbstract, input_file_name):
    if not isinstance(hash_storage, hash_storages.HashStorageAbstract):
        raise TypeError(f"HashStorageAbstract expected, {type(hash_storage)} found")

    start_date_time = datetime.now();
    if not cmd_line_args.suppress_console_reporting_output:
        print("Handle file start time: " + get_date_time_str(start_date_time) + " (" + input_file_name + ")")

    # Ref: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
    if (not cmd_line_args.force_calc_hash and hash_storage.has_hash(input_file_name)):
        if not cmd_line_args.suppress_console_reporting_output:
            print("Hash for file '" + input_file_name + "' exists ... calculation of hash skipped.\n")
        return cmd_line.ExitCode.OK_SKIPPED_ALREADY_CALCULATED
    if not cmd_line_args.suppress_console_reporting_output:
        print("Calculate hash for file '" + input_file_name + "'...")

    calc = hash_calc.FileHashCalc()
    calc.file_name = input_file_name
    calc.hash_str = cmd_line_args.hash_algo
    calc.suppress_console_reporting_output = cmd_line_args.suppress_console_reporting_output
    calc.retry_count_on_data_read_error = cmd_line_args.retry_count_on_data_read_error;
    calc.retry_pause_on_data_read_error = cmd_line_args.retry_pause_on_data_read_error;

    calc_res = calc.run()
    if calc_res != hash_calc.FileHashCalc.ReturnCode.OK:
        if calc_res == hash_calc.FileHashCalc.ReturnCode.PROGRAM_INTERRUPTED_BY_USER:
            return cmd_line.ExitCode.PROGRAM_INTERRUPTED_BY_USER
        elif calc_res == hash_calc.FileHashCalc.ReturnCode.DATA_READ_ERROR:
            return cmd_line.ExitCode.DATA_READ_ERROR
        else:
            raise Exception(f"Error on calculation of the hash: {calc_res}")
    hash = calc.result

    hash_storage.set_hash(input_file_name, hash)

    output_file_name = hash_storage.get_hash_file_name(input_file_name)
    if not cmd_line_args.suppress_console_reporting_output:
        print("HASH: ", hash, "(storage in file '" + output_file_name + "')")

    end_date_time = datetime.now();
    if not cmd_line_args.suppress_console_reporting_output:
        print("Handle file end time: " + get_date_time_str(end_date_time) + " (" + input_file_name + ")")
    seconds = int((end_date_time - start_date_time).total_seconds());
    # print("Elapsed time: {0}:{1:02d}:{2:02d}".format(int(seconds / 60 / 60), int(seconds / 60) % 60, seconds % 60))

    file_size = os.path.getsize(input_file_name)
    speed = file_size / seconds if seconds > 0 else 0
    if not cmd_line_args.suppress_console_reporting_output:
        print("Elapsed time: {0} (Average speed: {1}/sec)\n".format(util.format_seconds(seconds), util.convert_size_to_display(speed)))
     
    if (cmd_line_args.pause_after_file is not None):
        if not util.pause(cmd_line_args.pause_after_file):
            # Return specific error code
            return cmd_line.ExitCode.PROGRAM_INTERRUPTED_BY_USER

    return cmd_line.ExitCode.OK

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

def handle_input_files(hash_storage: hash_storages.HashStorageAbstract):
    if not isinstance(hash_storage, hash_storages.HashStorageAbstract):
        raise TypeError(f"HashStorageAbstract expected, {type(hash_storage)} found")

    hash_storage.hash_file_header_comments = \
        f"# Timestamp of hash calculation: {start_time_dic['str']}\n" \
        f"# Hash algorithm: {cmd_line_args.hash_algo}\n" \
        f"# File generated by smart_hasher (https://github.com/sergtk/smart_hasher)\n"
    hash_storage.suppress_hash_file_comments = cmd_line_args.suppress_output_file_comments

    input_file_names = []

    if (cmd_line_args.input_file):
        for input_file_name in cmd_line_args.input_file:
            input_file_names.append(input_file_name)

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
                    input_file_names.append(input_file_name)

    # remove duplicates
    # Ref: https://www.w3schools.com/python/python_howto_remove_duplicates.asp
    input_file_names = list(dict.fromkeys(input_file_names))
    input_file_names.sort()

    data_read_error = False

    file_count = len(input_file_names)
    for fi in range(0, file_count):
        if not cmd_line_args.suppress_console_reporting_output:
            print("File {0} of {1}".format(fi + 1, file_count))

        input_file_name = input_file_names[fi]
        h = handle_input_file(hash_storage, input_file_name)

        if h == cmd_line.ExitCode.DATA_READ_ERROR:
            data_read_error = True
        elif h >= cmd_line.ExitCode.FAILED:
            return h

    if data_read_error:
        return cmd_line.ExitCode.DATA_READ_ERROR
    return cmd_line.ExitCode.OK

def fill_start_time_dic():
    global start_time_dic
    # time in different formats when program run
    # Ref: https://www.programiz.com/python-programming/datetime/strftime
    start_time_dic = {"datetime": datetime.now()}
    start_time_dic["file_postfix"] = start_time_dic["datetime"].strftime("%Y-%m-%d_%H-%M-%S")
    

    tz_offset = time.localtime().tm_gmtoff
    tz_hours = abs(tz_offset) // 60 // 60
    tz_minutes = abs(tz_offset) // 60 % 60
    if tz_offset < 0:
        tz_sign = "-"
    else:
        tz_sign = "+"
    tz_str = f"UTC{tz_sign}{tz_hours:02d}:{tz_minutes:02d}";

    # Ref: https://howchoo.com/g/ywi5m2vkodk/working-with-datetime-objects-and-timezones-in-python
    start_time_dic["str"] = start_time_dic["datetime"].strftime("%Y-%m-%d %H:%M:%S") + f" {tz_str}";

    #pprint(start_time_dic)

try:
    # breakpoint()

    if __name__ == '__main__':
        cmd_line_args = None
        fill_start_time_dic()

        cmd_line_args, parse_res = cmd_line.parse_cmd_line()
        if parse_res != cmd_line.ExitCode.OK:
            exit(int(parse_res))
        if cmd_line_args.single_hash_file_name_base:
            hash_storage = hash_storages.SingleFileHashesStorage()
            hash_storage.single_hash_file_name_base = cmd_line_args.single_hash_file_name_base[0]
            hash_storage.preserve_unused_hash_records = cmd_line_args.preserve_unused_hash_records
        else:
            hash_storage = hash_storages.HashPerFileStorage()

        hash_storage.hash_file_name_postfix = get_hash_file_name_postfix()
        hash_storage.use_absolute_file_names = cmd_line_args.use_absolute_file_names
        hash_storage.load_hashes_info()
        e = handle_input_files(hash_storage)
        hash_storage.save_hashes_info() # Note, hash info is not stored on exception, because it is not clear if we can trust to that data

        #print("e = {0}".format(e))
        sys.exit(int(e))

except SystemExit as se:
    sys.exit(se.code)
except util.AppUsageError as aue:
    if cmd_line_args is None or not cmd_line_args.suppress_console_reporting_output:
        print(f"\nIncorrect usage of the application: {aue.args[0]}", file=sys.stderr)
    sys.exit(int(cmd_line.ExitCode.APP_USAGE_ERROR))
except BaseException as ex:
    # Ref: https://stackoverflow.com/a/4564595/13441
    # Wierd that `ex` is not used
    if cmd_line_args is None or not cmd_line_args.suppress_console_reporting_output:
        print(traceback.format_exc(), file=sys.stderr)

    # Short message
    # print("Exception thrown:\n", ex)

    sys.exit(int(cmd_line.ExitCode.EXCEPTION_THROWN_ON_PROGRAM_EXECUTION))
