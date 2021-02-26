import argparse
import enum
import functools

import smart_hasher
import hash_calc

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
        self._parser.add_argument('--input-file', '-if', action="append", help="Specify input files. Key can be specified multiple times")
        self._parser.add_argument('--input-folder', '-ifo', action="append", help="Specify input folders. All files in folder are handled recursively. Key can be specified multiple times")
        self._parser.add_argument('--input-folder-file-mask-include', '-ifoi', help="Specify file mask to include for input folder. All files in the folder considered if not specified. Separate multiple masks with semicolon (;)")
        self._parser.add_argument('--input-folder-file-mask-exclude', '-ifoe', help="Specify file mask to exclude for input folder. It is applied after --input-folder-file-mask-include. Separate multiple masks with semicolon (;)")
        self._parser.add_argument('--hash-file-name-output-postfix', '-op', action='append',
                            help="Specify postfix, which will be appended to the end of output file names. This is to specify for different contextes, "
                            "e.g. if file name ends with \".md5\", then it ends with \"md5.<value>\"")
        self._parser.add_argument('--hash-algo', help=f"Specify hash algo (default: {hash_calc.FileHashCalc.hash_algo_default_str})", default=hash_calc.FileHashCalc.hash_algo_default_str, choices=hash_calc.FileHashCalc.hash_algos)
        self._parser.add_argument('--suppress-console-reporting-output', '-so', help="Suppress console output with progress reporting", action="store_true")
        self._parser.add_argument('--pause-after-file', '-pf', help="Specify pause after every file handled, in seconds. Note, if file is skipped, then no pause applied", type=int)
        self._parser.add_argument('--retry-count-on-data-read-error', help=f"Specify count of retries on data read error (default: {calc.retry_count_on_data_read_error})", default=calc.retry_count_on_data_read_error, type=int)
        self._parser.add_argument('--retry-pause-on-data-read-error', help=f"Specify pause before retrying on data read error, in seconds (default: {calc.retry_pause_on_data_read_error})", default=calc.retry_pause_on_data_read_error, type=int)
        self._parser.add_argument('--force-calc-hash', '-fch', help="If specified than hash calculated always. If not, then hash is not calculated if file with hash already exist", action="store_true")
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
        self._parser.add_argument('--user-comment', '-uc', action="append", help="Specify comment which will be added to output hash file")


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

    def run(self, input_args):
        try:
            self._input_args = input_args
            self._configure_parser()
            # Ref: https://stackoverflow.com/questions/23032514/argparse-disable-same-argument-occurrences
            self._cmd_line_args = self._parser.parse_args(self._input_args)
            self._postprocess_parsed_args()
        except SystemExit as se:
            # Check if error is related to invalid command line parameters
            # Ref: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.error
            if se.code == 2:
                return (None, ExitCode.INVALID_COMMAND_LINE_PARAMETERS)
            raise se
        return (self._cmd_line_args, ExitCode.OK)

