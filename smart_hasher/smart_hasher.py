import sys
import os.path
import time
from datetime import datetime
import math
import argparse
import traceback
import ntpath
import fnmatch
import hash_calc
import util
import enum
import functools
from pprint import pprint
import hash_storages

# Code with values less than 7 are considered like OK, and program can continue execution
# Ref: https://docs.python.org/3.7/library/enum.html
# Ref: https://stackoverflow.com/questions/6060635/convert-enum-to-int-in-python
@enum.unique
@functools.total_ordering
class ExitCode(enum.IntEnum):
    OK = 0
    OK_SKIPPED_ALREADY_CALCULATED = 2
    FAILED = 7
    PROGRAM_INTERRUPTED_BY_USER = 8
    DATA_READ_ERROR = 9
    EXCEPTION_THROWN_ON_PROGRAM_EXECUTION = 10
    INVALID_COMMAND_LINE_PARAMETERS = 11

    # Ref: https://stackoverflow.com/questions/39268052/how-to-compare-enums-in-python
    # Ref: https://www.geeksforgeeks.org/operator-overloading-in-python/
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise Exception("Incompartible arguments")

exit_code_descriptions = {
    ExitCode.OK:                                "everthing fine. Program executed successfully",
    ExitCode.OK_SKIPPED_ALREADY_CALCULATED:     "everything fine. OK may be returned anyway\n     if file(s) is skipped because the hash is already calculated.",
    ExitCode.FAILED:                            "general failure, more specific information is not available.",
    ExitCode.DATA_READ_ERROR:                   "there was error(s) when reading some file(s). Probably hash is not calculated for all files",
}

def get_hash_file_name_postfix():
    global cmd_line_args

    output_file_name = "." + cmd_line_args.hash_algo

    if cmd_line_args.add_output_file_name_timestamp:
        output_file_name += "." + start_time_dic["file_postfix"]

    if cmd_line_args.hash_file_name_output_postfix:
        output_file_name += "." + cmd_line_args.hash_file_name_output_postfix[0]

    return output_file_name


# Ref: "Argparse Tutorial" https://docs.python.org/3/howto/argparse.html
# Ref: "15.4.3. The add_argument() method" https://docs.python.org/2/library/argparse.html#the-add-argument-method
def parse_command_line():
    global cmd_line_args;

    # Ref: https://developer.rhino3d.com/guides/rhinopython/python-statements/
    description = "This application is to calculate hashes of files with extended features: support of show progress,\n" \
        "folders and file masks for multiple files, skip calculation of handled files etc...\n\n"
    
    description += "Application exit codes:\n"
    for ec in ExitCode:
        description += f"{ec:2} - {ec.name}"
        code_desc = exit_code_descriptions.get(ec)
        if (code_desc is not None):
            description += f": {code_desc}"
        description += "\n"

    calc = hash_calc.FileHashCalc()

    try:
        # Ref: https://www.programcreek.com/python/example/6706/argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('--input-file', '-if', action="append", help="Specify one or more input files")
        parser.add_argument('--input-folder', '-ifo', action="append", help="Specify one or more input folders. All files in folder are handled recursively")
        parser.add_argument('--input-folder-file-mask-include', '-ifoi', help="Specify file mask to include for input folder. All files in the folder considered if not specified. Separate multiple masks with semicolon (;)")
        parser.add_argument('--input-folder-file-mask-exclude', '-ifoe', help="Specify file mask to exclude for input folder. It is applied after --input-folder-file-mask-include. Separate multiple masks with semicolon (;)")
        parser.add_argument('--hash-file-name-output-postfix', '-op', action='append', help="Specify postfix, which will be appended to the end of output file names. This is to specify for different contextes, e.g. if file name ends with \".md5\", then it ends with \"md5.<value>\"")
        parser.add_argument('--hash-algo', help=f"Specify hash algo (default: {hash_calc.FileHashCalc.hash_algo_default_str})", default=hash_calc.FileHashCalc.hash_algo_default_str, choices=hash_calc.FileHashCalc.hash_algos)
        parser.add_argument('--suppress-console-reporting-output', '-so', help="Suppress console output with progress reporting", action="store_true")
        parser.add_argument('--pause-after-file', '-pf', help="Specify pause after every file handled, in seconds. Note, if file is skipped, then no pause applied", type=int)
        parser.add_argument('--retry-count-on-data-read-error', help=f"Specify count of retries on data read error (default: {calc.retry_count_on_data_read_error})", default=calc.retry_count_on_data_read_error, type=int)
        parser.add_argument('--retry-pause-on-data-read-error', help=f"Specify pause before retrying on data read error, in seconds (default: {calc.retry_pause_on_data_read_error})", default=calc.retry_pause_on_data_read_error, type=int)
        parser.add_argument('--force-calc-hash', '-fch', help="If specified than hash calculated always. If not, then hash is not calculated if file with hash already exist", action="store_true")
        parser.add_argument('--add-output-file-name-timestamp', help="Add timestamp to the output file names. Note, that the time on program run taken. So it may differ from the file creation time, but it is equal for all files in one run", action="store_true")
        parser.add_argument('--suppress-output-file-comments', help="Don't add comments to output files. E.g. timestamp when hash generated", action="store_true")
        parser.add_argument('--use-absolute-file-names', help="Use absolute file names in output. If argument is not specified, relative file names used", action="store_true")

        # Ref: https://stackoverflow.com/questions/23032514/argparse-disable-same-argument-occurrences
        cmd_line_args = parser.parse_args()

        if (not cmd_line_args.input_file and not cmd_line_args.input_folder):
            parser.error("One or more input files and/or folders should be specified")
        if cmd_line_args.hash_file_name_output_postfix and len(cmd_line_args.hash_file_name_output_postfix) > 1:
            parser.error("--hash-file-name-output-postfix appears several times.")

        if cmd_line_args.pause_after_file and cmd_line_args.pause_after_file < 0:
            parser.error('--pause-after-file must be non-negative')
    except SystemExit as se:
        # Check if error is related to invalid command line parameters
        # Ref: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.error
        if se.code == 2:
            return ExitCode.INVALID_COMMAND_LINE_PARAMETERS
        raise se
    return ExitCode.OK


def get_date_time_str(dateTime: datetime) -> str:
    return dateTime.strftime("%Y.%m.%d %H:%M:%S")

def handle_input_file(hash_storage: hash_storages.HashStorageAbstract, input_file_name) -> ExitCode:
    if not isinstance(hash_storage, hash_storages.HashStorageAbstract):
        raise TypeError(f"HashStorageAbstract expected, {type(hash_storage)} found")

    start_date_time = datetime.now();
    if not cmd_line_args.suppress_console_reporting_output:
        print("Handle file start time: " + get_date_time_str(start_date_time) + " (" + input_file_name + ")")

    # Ref: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
    if (not cmd_line_args.force_calc_hash and hash_storage.has_hash(input_file_name)):
        if not cmd_line_args.suppress_console_reporting_output:
            print("Hash for file '" + input_file_name + "' exists ... calculation of hash skipped.\n")
        return ExitCode.OK_SKIPPED_ALREADY_CALCULATED
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
            return ExitCode.PROGRAM_INTERRUPTED_BY_USER
        elif calc_res == hash_calc.FileHashCalc.ReturnCode.DATA_READ_ERROR:
            return ExitCode.DATA_READ_ERROR
        else:
            raise Exception(f"Error on calculation of the hash: {calc_res}")
    hash = calc.result

    hash_storage.set_hash(input_file_name, hash)

    output_file_name = hash_storage.get_hash_file_name(input_file_name)
    if not cmd_line_args.suppress_console_reporting_output:
        print("HASH: ", hash, "(stored in file '" + output_file_name + "')")

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
            return ExitCode.PROGRAM_INTERRUPTED_BY_USER

    return ExitCode.OK

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
        f"# Hash algorithm: {cmd_line_args.hash_algo}\n"
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

        if h == ExitCode.DATA_READ_ERROR:
            data_read_error = True
        elif h >= ExitCode.FAILED:
            return h

    if data_read_error:
        return ExitCode.DATA_READ_ERROR
    return ExitCode.OK

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
    if __name__ == '__main__':
        fill_start_time_dic()

        parse_res = parse_command_line()
        if parse_res  != ExitCode.OK:
            exit(int(parse_res))

        with hash_storages.HashPerFileStorage(get_hash_file_name_postfix(), cmd_line_args.use_absolute_file_names) as hash_storage:
            e = handle_input_files(hash_storage)
        #print("e = {0}".format(e))
        exit(int(e))

except SystemExit as se:
    exit(se.code)
except BaseException as ex:
    # Ref: https://stackoverflow.com/a/4564595/13441
    # Wierd that `ex` is not used
    print(traceback.format_exc())

    # Short message
    # print("Exception thrown:\n", ex)

    exit(int(ExitCode.EXCEPTION_THROWN_ON_PROGRAM_EXECUTION))
