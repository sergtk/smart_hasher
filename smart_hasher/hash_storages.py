import abc
import os
import util
import re
import locale

class HashStorageAbstract(abc.ABC):

    def __init__(self):
        self.hash_file_name_postfix = ""
        self.use_absolute_file_names = False
        self.hash_file_header_comments = None # The default is None to throw exception if not assigned so to catch error early
        self.suppress_hash_file_comments = False
        self.norm_case_file_names = False

    def _check_data_hash_files_names_equal(self, data_file_name, hash_file_name):
        # Ref: https://docs.python.org/3/library/os.path.html#os.path.realpath
        if os.path.normcase(os.path.realpath(data_file_name)) == os.path.normcase(os.path.realpath(hash_file_name)):
            raise util.AppUsageError(f"Data and hash file names are the same: '{data_file_name}'. Data and hash file names should specify different files to avoid data loss of data file")

    @abc.abstractmethod
    def load_hashes_info(self): pass

    @abc.abstractmethod
    def save_hashes_info(self): pass

    # This function is just for reporting.
    # To check if the data file has hash the function call `has_hash` should be made
    @abc.abstractmethod
    def get_hash_file_name(self, data_file_name): pass

    @abc.abstractmethod
    def has_hash(self, data_file_name): pass

    @abc.abstractmethod
    def set_hash(self, data_file_name, hash_value): pass # force re-hash should be checked

    # Ref: https://www.geeksforgeeks.org/with-statement-in-python/ - it looks fine for __enter__, but not for __exit__
    def __enter__ (self):
        self.load_hashes_info()
        return self

    # Ref: https://stackoverflow.com/questions/22417323/how-do-enter-and-exit-work-in-python-decorator-classes
    # Ref: https://docs.python.org/3/reference/datamodel.html#object.__exit__
    def __exit__ (self, exc_type, exc_value, traceback):
        self.save_hashes_info()
        return False

class HashPerFileStorage(HashStorageAbstract):

    def load_hashes_info(self):
        pass

    def save_hashes_info(self):
        pass

    def get_hash_file_name(self, data_file_name):
        ret = os.path.abspath(data_file_name) + self.hash_file_name_postfix
        self._check_data_hash_files_names_equal(data_file_name, ret)
        return ret

    def has_hash(self, data_file_name):
        # Ref: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists/
        hash_file_name = self.get_hash_file_name(data_file_name)
        self._check_data_hash_files_names_equal(data_file_name, hash_file_name)

        if not os.path.exists(hash_file_name):
            return False
        if not os.path.isfile(hash_file_name):
            raise util.AppUsageError(f"Path '{hash_file_name}' is dir and can't be used to save hash value")
        return True

    def set_hash(self, data_file_name, hash_value):
        hash_file_name = self.get_hash_file_name(data_file_name)
        self._check_data_hash_files_names_equal(data_file_name, hash_file_name)
        
        # Ref: https://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file
        with open(hash_file_name, 'w') as hash_file:
            if not self.suppress_hash_file_comments:
                hash_file.write(self.hash_file_header_comments)
            if self.use_absolute_file_names:
                data_file_name_user = os.path.abspath(data_file_name)
            else:
                data_file_name_user = util.rel_file_path(data_file_name, hash_file_name, False)

            if self.norm_case_file_names:
                data_file_name_user = os.path.normcase(data_file_name_user)

            hash_file.write(hash_value + " *" + data_file_name_user + "\n")

class SingleFileHashesStorage(HashStorageAbstract):

    def __init__(self):
        super().__init__()
        #self.single_hash_file_name_base = single_hash_file_name_base
        self.single_hash_file_name_base = None
        self.hash_data = dict()
        self.preserve_unused_hash_records = False

    def __input_hash_file_error_message(self, error_message, hash_file_name, lineIndex, line):
        return f"{error_message}.\n    File {hash_file_name}, Line {lineIndex}: {line[0:200]}"

    # Ref: https://docs.python.org/3.7/library/collections.html#collections.OrderedDict
    # Ref: https://docs.python.org/3/library/re.html
    def load_hashes_info(self):
        if self.single_hash_file_name_base is None:
            raise Exception("Input file name base is not specified")
        
        hash_file_name = self.get_hash_file_name(None)
        if not os.path.exists(hash_file_name):
            return

        # Dictionary stores pair "absolute file name" -> "hash"
        self.hash_data = dict()

        comment_pattern = re.compile("\s*(#.*)?\n?")
        # Ref: https://stackoverflow.com/questions/50618116/regex-for-finding-file-paths
        # Ref: https://stackoverflow.com/questions/2758921/regular-expression-that-finds-and-replaces-non-ascii-characters-with-python
        hash_record_pattern = re.compile("(?P<hash>[0-9A-Fa-f]+)\s+\*(?P<file>[\\\\/\w.: \u0080-\uFFFF]+)\n?")

        with open(hash_file_name, "r") as f:
            line = f.readline()
            lineIndex = 1
            while line:
                # Parse and skip comments
                if comment_pattern.fullmatch(line):
                    line = f.readline()
                    lineIndex += 1
                    continue
                # print(f"line for work: {line}")
                match = hash_record_pattern.fullmatch(line)
                if match is None:
                    raise util.AppUsageError(self.__input_hash_file_error_message("Input file with hashes has wrong format", hash_file_name, lineIndex, line))
                hash = match.group("hash").lower()
                data_file_name = match.group("file")

                #data_file_name =  os.path.abspath(data_file_name)
                data_file_name = util.rel_file_path(data_file_name, hash_file_name, True)
                if self.norm_case_file_names:
                    data_file_name = os.path.normcase(data_file_name)

                if self.hash_data.get(data_file_name) is not None:
                    raise util.AppUsageError(self.__input_hash_file_error_message("Input hash file contains duplicated entry for file '{data_file_name}'", hash_file_name, lineIndex, line))
                
                # False in tuple specify that element was not accessed. This mean that it should not be saved in output file.
                # True should be later specfieid to save info
                self.hash_data[data_file_name] = (hash, False)

                line = f.readline()
                lineIndex += 1

    def save_hashes_info(self):
        hash_file_name = self.get_hash_file_name(None)
        with open(hash_file_name, "w") as hash_file:
            if not self.suppress_hash_file_comments:
                hash_file.write(self.hash_file_header_comments)

            hash_data_sorted = []

            # Ref: https://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops
            #for data_file_name, hash in self.hash_data.items():
            for data_file_name, hash in self.hash_data.items():
                if self.use_absolute_file_names:
                    data_file_name_user = data_file_name
                    assert os.path.isabs(data_file_name_user)
                else:
                    data_file_name_user = util.rel_file_path(data_file_name, hash_file_name, False)
                hash_data_sorted.append((data_file_name_user, hash))

            # Ref: https://stackoverflow.com/questions/1097908/how-do-i-sort-unicode-strings-alphabetically-in-python
            #locale.setlocale(locale.LC_ALL, "")
            hash_data_sorted.sort(key = lambda v : (os.path.normcase(v[0]), v[0])) # Compare in norm case. If equal, then compare original strings
            for data_file_name, hash_info in hash_data_sorted:
                # Check that current hash entry should be stored
                if self.preserve_unused_hash_records or hash_info[1]:
                    hash_file.write(f"{hash_info[0]} *{data_file_name}\n")

            if not self.suppress_hash_file_comments:
                hash_file.write("# End of file\n")

    def get_hash_file_name(self, _):
        ret = f"{self.single_hash_file_name_base}{self.hash_file_name_postfix}"
        return ret

    def has_hash(self, data_file_name):
        self._check_data_hash_files_names_equal(data_file_name, self.get_hash_file_name(None))

        fn = os.path.abspath(data_file_name)
        # Ref: https://docs.python.org/3.2/library/os.path.html#os.path.normcase
        if self.norm_case_file_names:
            fn = os.path.normcase(fn)
        ret = fn in self.hash_data
        if ret:
            self.hash_data[fn] = (self.hash_data[fn][0], True)
        return ret

    def set_hash(self, data_file_name, hash_value):
        self._check_data_hash_files_names_equal(data_file_name, self.get_hash_file_name(None))

        fn = os.path.abspath(data_file_name)
        # Ref: https://docs.python.org/3.2/library/os.path.html#os.path.normcase
        if self.norm_case_file_names:
            fn = os.path.normcase(fn)
        self.hash_data[fn] = (hash_value, True)
