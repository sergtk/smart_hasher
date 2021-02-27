import argparse
import enum
import functools
import util
import traceback
import sys
import math
import fnmatch
import time
import locale
import ntpath
import os.path
from datetime import datetime
import shlex
import platform

import smart_hasher
import hash_calc
import hash_storages

@enum.unique
@functools.total_ordering
class ExitCode(enum.IntEnum):
    """
    Code with values less than 7 are considered like OK, and program can continue execution
    Ref: https://docs.python.org/3.7/library/enum.html
    Ref: https://stackoverflow.com/questions/6060635/convert-enum-to-int-in-python
    """
    OK = 0
    OK_SKIPPED_ALREADY_CALCULATED = 2
    FAILED = 7
    PROGRAM_INTERRUPTED_BY_USER = 8
    DATA_READ_ERROR = 9
    EXCEPTION_THROWN_ON_PROGRAM_EXECUTION = 10
    INVALID_COMMAND_LINE_PARAMETERS = 11
    APP_USAGE_ERROR = 12

    # Ref: https://stackoverflow.com/questions/39268052/how-to-compare-enums-in-python
    # Ref: https://www.geeksforgeeks.org/operator-overloading-in-python/
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise Exception("Incompartible arguments")

#  Description for some error codes especially for ones which are not self descriptive, or have some specific details
exit_code_descriptions = {
    ExitCode.OK:                                "everthing fine. Program executed successfully",
    ExitCode.OK_SKIPPED_ALREADY_CALCULATED:     "everything fine. OK may be returned anyway\n     if file(s) is skipped because the hash is already calculated.",
    ExitCode.FAILED:                            "general failure, more specific information is not available.",
    ExitCode.DATA_READ_ERROR:                   "there was error(s) when reading some file(s). It is likely that hashes are not calculated for all input files",
    ExitCode.APP_USAGE_ERROR:                   "incorrect usage of the application",
}

############################################################################################################

class CommandLineAdapter(object):

    def __init__(self):
        self._input_args = None # This should be specified by caller
        self._parser = None
        self._cmd_line_args = None

    def _fill_start_time_dict(self):
        """
        Save time in different formats at the start of the program run
    
        Ref: https://www.programiz.com/python-programming/datetime/strftime
        """
        self._start_time_dict = {"datetime": datetime.now()}
        self._start_time_dict["file_postfix"] = self._start_time_dict["datetime"].strftime("%Y-%m-%d_%H-%M-%S")

        tz_offset = time.localtime().tm_gmtoff
        tz_hours = abs(tz_offset) // 60 // 60
        tz_minutes = abs(tz_offset) // 60 % 60
        if tz_offset < 0:
            tz_sign = "-"
        else:
            tz_sign = "+"
        tz_str = f"UTC{tz_sign}{tz_hours:02d}:{tz_minutes:02d}";

        # Ref: https://howchoo.com/g/ywi5m2vkodk/working-with-datetime-objects-and-timezones-in-python
        self._start_time_dict["str"] = self._start_time_dict["datetime"].strftime("%Y-%m-%d %H:%M:%S") + f" {tz_str}";

    def _info(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        if self._cmd_line_args is not None and self._cmd_line_args.suppress_console_reporting_output:
            return
        print(*objects, sep=sep, end=end, file=file, flush=flush)

    def _configure_parser(self):
        """    
        Ref: "Argparse Tutorial" https://docs.python.org/3/howto/argparse.html
        Ref: "15.4.3. The add_argument() method" https://docs.python.org/2/library/argparse.html#the-add-argument-method
        """

        if self._input_args is None:
            raise Exception("Arguments are not specified")

        # Ref: https://developer.rhino3d.com/guides/rhinopython/python-statements/
        description = "This is a command line tool to calculate hashes for one or many files at once with many convenient features: support of show progress,\n" \
            "folders and file masks for multiple files, skip calculation of handled files etc...\n\n"
    
        description += "Application exit codes:\n"
        for ec in ExitCode:
            description += f"{ec:2} - {ec.name}"
            code_desc = exit_code_descriptions.get(ec)
            if (code_desc is not None):
                description += f": {code_desc}"
            description += "\n"

        calc = hash_calc.FileHashCalc()

        autosave_timeout_default = 300

        # Ref: https://www.programcreek.com/python/example/6706/argparse.RawDescriptionHelpFormatter
        self._parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
        self._parser.add_argument('--input-file', '-i', action="append", help="Specify input files. Key can be specified multiple times")
        self._parser.add_argument('--input-folder', action="append", help="Specify input folders. All files in folder are handled recursively. Key can be specified multiple times")
        self._parser.add_argument('--input-folder-file-mask-include', help="Specify file mask to include for input folder. All files in the folder considered if not specified. Separate multiple masks with semicolon (;)")
        self._parser.add_argument('--input-folder-file-mask-exclude', help="Specify file mask to exclude for input folder. It is applied after --input-folder-file-mask-include. Separate multiple masks with semicolon (;)")
        self._parser.add_argument('--hash-file-name-output-postfix', action='append',
                            help="Specify postfix, which will be appended to the end of output file names. This is to specify for different contextes, "
                            "e.g. if file name ends with \".md5\", then it ends with \"md5.<value>\"")
        self._parser.add_argument('--hash-algo', help=f"Specify hash algo (default: {hash_calc.FileHashCalc.hash_algo_default_str})", default=hash_calc.FileHashCalc.hash_algo_default_str, choices=hash_calc.FileHashCalc.hash_algos)
        self._parser.add_argument('--suppress-console-reporting-output', '-s', help="Suppress console output with progress reporting", action="store_true")
        self._parser.add_argument('--pause-after-file', '-p', help="Specify pause after every file handled, in seconds. Note, if file is skipped, then no pause applied", type=int)
        self._parser.add_argument('--retry-count-on-data-read-error', help=f"Specify count of retries on data read error (default: {calc.retry_count_on_data_read_error})", default=calc.retry_count_on_data_read_error, type=int)
        self._parser.add_argument('--retry-pause-on-data-read-error', help=f"Specify pause before retrying on data read error, in seconds (default: {calc.retry_pause_on_data_read_error})", default=calc.retry_pause_on_data_read_error, type=int)
        self._parser.add_argument('--force-calc-hash', help="If specified than hash calculated always. If not, then hash is not calculated if file with hash already exist", action="store_true")
        self._parser.add_argument('--add-output-file-name-timestamp', action="store_true",
                                  help="Add timestamp to the output file names. Note, that the time on program run taken. So it may differ from the file creation time, "
                                  "but it is equal for all files in one run")
        self._parser.add_argument('--suppress-output-file-comments', help="Don't add comments to output files. E.g. timestamp when hash generated", action="store_true")
        self._parser.add_argument('--use-absolute-file-names', help="Use absolute file names in output. If argument is not specified, relative file names used", action="store_true")
        self._parser.add_argument('--single-hash-file-name-base', help="If specified then all hashes are stored in one file specified as a value for this argument. Final file name include postfix", action="append")
        self._parser.add_argument('--single-hash-file-name-base-json', help="This is the same key as --single-hash-file-name-base. But postfix json is added. Result data stored in JSON", action="append")
        self._parser.add_argument('--suppress-hash-file-name-postfix', help="Suppress adding postfix in the hash file name for hash algo name", action="store_true")
        self._parser.add_argument('--preserve-unused-hash-records', action="store_true",
                                  help="This key works with --single-hash-file-name-base. By default if file with hashes already exists then records for files which not handled are deleted to avoid records for non-existing files. "
                                 "If this key specified, then such records preserved in hash file")
        self._parser.add_argument('--norm-case-file-names', action="store_true",
                                  help="Use normalized case of file names on output. This is more robust, but file names may differ which may look inconvenient. It is also platform dependent. "
                                  "Refer for details to https://docs.python.org/3/library/os.path.html#os.path.normcase")
        self._parser.add_argument('--sort-by-hash-value', action="store_true",
                                  help="Specify to store hash records sorted by hash values in case when multiple hashes are stored in one file. By default without this option hash records are sorted by file name")
        self._parser.add_argument('--autosave-timeout', default=autosave_timeout_default, type=int,
                                  help=f"Save accumulated hashes after interval specified as argument, in seconds (default: {autosave_timeout_default}). "
                                  "Specify 0 to save hash info after handling every file, this may result in large overhead when many files on input. "
                                  "Specify -1 to disable autosave, this may result the accumulated hash data missed if execution interrupts unexpectedly. "
                                  "This is essential when multiple hashes stored in one file.")
        self._parser.add_argument('--user-comment', '-u', action="append", help="Specify comment which will be added to output hash file")

    def _postprocess_parsed_args(self):
        if (not self._cmd_line_args.input_file and not self._cmd_line_args.input_folder):
            self._parser.error("One or more input files and/or folders should be specified")

        if self._cmd_line_args.hash_file_name_output_postfix and len(self._cmd_line_args.hash_file_name_output_postfix) > 1:
            self._parser.error("--hash-file-name-output-postfix appears several times.")

        if self._cmd_line_args.pause_after_file and self._cmd_line_args.pause_after_file < 0:
            self._parser.error('--pause-after-file must be non-negative')

        if self._cmd_line_args.single_hash_file_name_base is not None and len(self._cmd_line_args.single_hash_file_name_base) > 0 and \
           self._cmd_line_args.single_hash_file_name_base_json is not None and len(self._cmd_line_args.single_hash_file_name_base_json) > 0:
            self._parser.error("--single-hash-file-name-base and --single-hash-file-name-base-json are mutually exclusive. Only one of them can be specified")

        if self._cmd_line_args.single_hash_file_name_base:
            if len(self._cmd_line_args.single_hash_file_name_base) > 1:
                self._parser.error("--single-hash-file-name-base should be either specified once or not specified")
            self._cmd_line_args.single_hash_file_name_base = self._cmd_line_args.single_hash_file_name_base[0]

        if self._cmd_line_args.single_hash_file_name_base_json:
            if len(self._cmd_line_args.single_hash_file_name_base_json) > 1:
                self._parser.error("--single-hash-file-name-base-json should be either specified once or not specified")
            self._cmd_line_args.single_hash_file_name_base_json = self._cmd_line_args.single_hash_file_name_base_json[0]

    def _get_hash_file_name_postfix(self):

        postfix = ""

        if not self._cmd_line_args.suppress_hash_file_name_postfix:
            postfix += "." + self._cmd_line_args.hash_algo
            if self._cmd_line_args.single_hash_file_name_base_json:
                postfix += ".json"

        if self._cmd_line_args.add_output_file_name_timestamp:
            postfix += "." + self._start_time_dict["file_postfix"]

        if self._cmd_line_args.hash_file_name_output_postfix:
            postfix += "." + self._cmd_line_args.hash_file_name_output_postfix[0]

        return postfix

    def _get_date_time_str(self, dateTime: datetime) -> str:
        return dateTime.strftime("%Y.%m.%d %H:%M:%S")

    def _handle_input_file(self, hash_storage: hash_storages.HashStorageAbstract, input_file_name):
        """
        Handle single input file input_file_name
        """
        if not isinstance(hash_storage, hash_storages.HashStorageAbstract):
            raise TypeError(f"HashStorageAbstract expected, {type(hash_storage)} found")

        start_date_time = datetime.now();
        self._info("Handle file start time: " + self._get_date_time_str(start_date_time) + " (" + input_file_name + ")")

        # Ref: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
        if not self._cmd_line_args.force_calc_hash and hash_storage.has_hash(input_file_name):
            self._info("Hash for file '" + input_file_name + "' exists ... calculation of hash skipped.\n")
            return ExitCode.OK_SKIPPED_ALREADY_CALCULATED
        self._info("Calculate hash for file '" + input_file_name + "'...")

        calc = hash_calc.FileHashCalc()
        calc.file_name = input_file_name
        calc.hash_str = self._cmd_line_args.hash_algo
        calc.suppress_console_reporting_output = self._cmd_line_args.suppress_console_reporting_output
        calc.retry_count_on_data_read_error = self._cmd_line_args.retry_count_on_data_read_error;
        calc.retry_pause_on_data_read_error = self._cmd_line_args.retry_pause_on_data_read_error;

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
        self._info("HASH:", hash, "(storage in file '" + output_file_name + "')")

        end_date_time = datetime.now();
        self._info("Handle file end time: " + self._get_date_time_str(end_date_time) + " (" + input_file_name + ")")
        seconds = int((end_date_time - start_date_time).total_seconds());
        # print("Elapsed time: {0}:{1:02d}:{2:02d}".format(int(seconds / 60 / 60), int(seconds / 60) % 60, seconds % 60))

        file_size = os.path.getsize(input_file_name)
        speed = file_size / seconds if seconds > 0 else 0
        self._info("Elapsed time: {0} (Average speed: {1}/sec)\n".format(util.format_seconds(seconds), util.convert_size_to_display(speed)))
     
        if (self._cmd_line_args.pause_after_file is not None):
            if not util.pause(self._cmd_line_args.pause_after_file):
                # Return specific error code
                return ExitCode.PROGRAM_INTERRUPTED_BY_USER

        return ExitCode.OK

    def _file_masks_included(self, file_name):
        """
        Ref: "Extract file name from path, no matter what the os/path format" https://stackoverflow.com/a/8384788/13441
        """
        base_name = ntpath.basename(file_name)

        # Ref: https://docs.python.org/2/library/fnmatch.html
        # if fnmatch.fnmatch(base_name, '*.txt'):

        if (self._cmd_line_args.input_folder_file_mask_include):
            file_included = False
            include_masks = self._cmd_line_args.input_folder_file_mask_include.split(";")
            for include_mask in include_masks:
                if fnmatch.fnmatch(file_name, include_mask):
                    file_included = True
                    break
            if not file_included:
                return False

        if (self._cmd_line_args.input_folder_file_mask_exclude):
            exclude_masks = self._cmd_line_args.input_folder_file_mask_exclude.split(";")
            for exclude_mask in exclude_masks:
                if fnmatch.fnmatch(file_name, exclude_mask):
                    return False
        return True

    def _handle_input_files(self, hash_storage: hash_storages.HashStorageAbstract):
        """
        Handle input files according to the parameters from user
        """

        if not isinstance(hash_storage, hash_storages.HashStorageAbstract):
            raise TypeError(f"HashStorageAbstract expected, {type(hash_storage)} found")

        header_comments = [
            f"File generated by Smart Hasher (https://github.com/sergtk/smart_hasher)",
            f"Timestamp of hash calculation: {self._start_time_dict['str']}",
            f"Hash algorithm: {self._cmd_line_args.hash_algo}"]
        if self._cmd_line_args.user_comment:
            header_comments = header_comments + [f"User comment: {cmt}" for cmt in self._cmd_line_args.user_comment]
        hash_storage.hash_file_header_comments = header_comments

        hash_storage.suppress_hash_file_comments = self._cmd_line_args.suppress_output_file_comments

        input_file_names = []

        if (self._cmd_line_args.input_file):
            for input_file_name in self._cmd_line_args.input_file:
                if not os.path.isfile(input_file_name):
                    self._info(f"Input file does not exist: {input_file_name}")
                    return ExitCode.DATA_READ_ERROR
                input_file_names.append(input_file_name)

        if (self._cmd_line_args.input_folder):
            # Ref: https://docs.python.org/3/library/os.html#os.walk
            # Ref: https://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
            for input_folder in self._cmd_line_args.input_folder:
                if not os.path.isdir(input_folder):
                    self._info(f"Input folder does not exist: {input_folder}")
                    return ExitCode.DATA_READ_ERROR
                for dir_name, subdir_list, file_list in os.walk(input_folder):
                    for base_file_name in file_list:
                        input_file_name = os.path.join(dir_name, base_file_name)
                        if not self._file_masks_included(input_file_name):
                            continue
                        # print("{0} -> {1}".format(dir_name, base_file_name));
                        input_file_names.append(input_file_name)

        # remove duplicates
        # Ref: https://www.w3schools.com/python/python_howto_remove_duplicates.asp
        input_file_names = list(dict.fromkeys(input_file_names))
    
        # Sort accounting unicode
        key1 = lambda v: (locale.strxfrm(v).casefold(), locale.strxfrm(v))
        input_file_names.sort(key=key1)

        data_read_error = False

        file_count = len(input_file_names)
        for fi in range(0, file_count):
            self._info(f"File {fi + 1} of {file_count}")

            input_file_name = input_file_names[fi]
            h = self._handle_input_file(hash_storage, input_file_name)

            if h == ExitCode.DATA_READ_ERROR:
                data_read_error = True
            elif h >= ExitCode.FAILED:
                return h

        if data_read_error:
            return ExitCode.DATA_READ_ERROR
        return ExitCode.OK

    def _handle_input(self):
        if self._cmd_line_args.single_hash_file_name_base or self._cmd_line_args.single_hash_file_name_base_json:
            hash_storage = hash_storages.SingleFileHashesStorage()
            
            if self._cmd_line_args.single_hash_file_name_base:
                hash_storage.single_hash_file_name_base = self._cmd_line_args.single_hash_file_name_base
            else:
                assert self._cmd_line_args.single_hash_file_name_base_json
                hash_storage.single_hash_file_name_base = self._cmd_line_args.single_hash_file_name_base_json
                hash_storage.json_format = True

            hash_storage.preserve_unused_hash_records = self._cmd_line_args.preserve_unused_hash_records
            hash_storage.sort_by_hash_value = self._cmd_line_args.sort_by_hash_value
        else:
            hash_storage = hash_storages.HashPerFileStorage()

        hash_storage.hash_file_name_postfix = self._get_hash_file_name_postfix()
        hash_storage.use_absolute_file_names = self._cmd_line_args.use_absolute_file_names
        hash_storage.norm_case_file_names = self._cmd_line_args.norm_case_file_names
        hash_storage.autosave_timeout = self._cmd_line_args.autosave_timeout

        hash_storage.load_hashes_info()
        exit_code = self._handle_input_files(hash_storage)
        hash_storage.save_hashes_info() # Note, hash info is not stored on exception, because it is not clear if we can trust to that data

        # Ref: https://stackoverflow.com/questions/24487405/enum-getting-value-of-enum-on-string-conversion
        self._info(f"ExitCode: {exit_code.name} ({exit_code})")

        return exit_code

    # input_args is a list of command line arguments. Typically the following value is passed: sys.argv[1:]
    def run(self, input_args):
        try:
            self._fill_start_time_dict()
            self._input_args = input_args
            self._configure_parser()
            # Ref: https://stackoverflow.com/questions/23032514/argparse-disable-same-argument-occurrences
            self._cmd_line_args = self._parser.parse_args(self._input_args)
            self._postprocess_parsed_args()
            ret = self._handle_input()
            return ret
        except SystemExit as se:
            # Check if error is related to invalid command line parameters
            # Ref: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.error
            if se.code == 2:
                return ExitCode.INVALID_COMMAND_LINE_PARAMETERS
            return se.code
        except util.AppUsageError as aue:
            self._info(f"\nIncorrect usage of the application: {aue.args[0]}", file=sys.stderr)
            return ExitCode.APP_USAGE_ERROR
        except BaseException as ex:
            # Ref: https://stackoverflow.com/a/4564595/13441
            # Wierd that `ex` is not used
            self._info(traceback.format_exc(), file=sys.stderr)

            # Short message
            # print("Exception thrown:\n", ex)
            return ExitCode.EXCEPTION_THROWN_ON_PROGRAM_EXECUTION

        return ExitCode.OK

    # `cmd_line` is the string, which contains CLI parameters without script itself.
    # This function is primarily for testing
    def run_cmd_line(self, cmd_line):
        # Ref: https://stackoverflow.com/questions/19719971/why-do-i-need-4-backslashes-in-a-python-path
        if platform.platform().startswith('Windows'):
            cmd_line = cmd_line.replace(os.sep, os.sep + os.sep)
        # Ref: https://stackoverflow.com/questions/899276/how-to-parse-strings-to-look-like-sys-argv
        input_args = shlex.split(cmd_line)
        ret = self.run(input_args)
        return ret
