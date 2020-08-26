import abc
import os
import util
import re
import locale
import json
import shutil
import time
import uuid

class HashStorageAbstract(abc.ABC):
    """
    This is a base class for storages of hash information
    """

    def __init__(self):
        self.hash_file_name_postfix = ""
        self.use_absolute_file_names = False
        self.hash_file_header_comments = None # It should contain list of strings. The default is None to throw exception if not assigned so to catch error early
        self.suppress_hash_file_comments = False
        self.norm_case_file_names = False
        self.autosave_timeout = -1

    def _check_data_hash_files_names_equal(self, data_file_name, hash_file_name):
        """
        Ref: https://docs.python.org/3/library/os.path.html#os.path.realpath
        """
        if os.path.normcase(os.path.realpath(data_file_name)) == os.path.normcase(os.path.realpath(hash_file_name)):
            raise util.AppUsageError(f"Data and hash file names are the same: '{data_file_name}'. Data and hash file names should specify different files to avoid data loss of data file")
        
    @abc.abstractmethod
    def load_hashes_info(self):
        """
        Load hashes from file or other sources if there are already calculated ones which corresponce to the parameters of the class
        """
        pass

    @abc.abstractmethod
    def save_hashes_info(self):
        """
        Save calculated hashes info to file(s) or other destination with a given format etc...
        """
        pass

    @abc.abstractmethod
    def get_hash_file_name(self, data_file_name):
        """
        This function is just for reporting.
        To check if the data file has hash the function call `has_hash` should be made
        """
        pass
    
    @abc.abstractmethod
    def has_hash(self, data_file_name):
        """
        Check if the hash for file data_file_name is already calculated
        """
        pass

    @abc.abstractmethod
    def set_hash(self, data_file_name, hash_value):
        """
        Force re-hash should be accounted
        """
        pass

    def __enter__ (self):
        """
        Ref: https://www.geeksforgeeks.org/with-statement-in-python/ - it looks fine for __enter__, but not for __exit__
        """
        self.load_hashes_info()
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        """
        Ref: https://stackoverflow.com/questions/22417323/how-do-enter-and-exit-work-in-python-decorator-classes
        Ref: https://docs.python.org/3/reference/datamodel.html#object.__exit__
        """
        self.save_hashes_info()
        return False

class HashPerFileStorage(HashStorageAbstract):
    """
    This is a hash storage to save hash information one hash file for one data  file
    """

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
                comments = "# " + "\n# ".join(self.hash_file_header_comments) + "\n"
                hash_file.write(comments)
            if self.use_absolute_file_names:
                data_file_name_user = os.path.abspath(data_file_name)
            else:
                data_file_name_user = util.rel_file_path(data_file_name, hash_file_name, False)

            if self.norm_case_file_names:
                data_file_name_user = os.path.normcase(data_file_name_user)

            hash_file.write(f"{hash_value} *{data_file_name_user}\n")

class SingleFileHashesStorage(HashStorageAbstract):
    """
    This is a hash information storage to save hash information in one hash file for many data files

    This storage supports traditional hash files and json-storages.
    """

    def __init__(self):
        super().__init__()
        #self.single_hash_file_name_base = single_hash_file_name_base
        self.single_hash_file_name_base = None
        self.hash_data = dict()
        self.preserve_unused_hash_records = False
        self.sort_by_hash_value = False
        self.json_format = False # Use JSON format for reading and writting data
        self.last_time_load_save = time.time() # Strictly speaking this is not correct value, but construction time is good value to avoid non-initialized variable
        self.__backup_hash_file_name = ""

    def __input_hash_file_error_message(self, error_message, hash_file_name, lineIndex, line):
        return f"{error_message}.\n    File {hash_file_name}, Line {lineIndex}: {line[0:200]}"

    def __load_hash_info_entry(self, data_file_name, hash, hash_file_name):
        if self.hash_data.get(data_file_name) is not None:
            raise util.AppUsageError(self.__input_hash_file_error_message("Input hash file contains duplicated entry for file '{data_file_name}'", hash_file_name, lineIndex, line))

        #data_file_name =  os.path.abspath(data_file_name)
        data_file_name = util.rel_file_path(data_file_name, hash_file_name, True)

        if self.norm_case_file_names:
            data_file_name = os.path.normcase(data_file_name)
                
        # False in tuple specify that element was not accessed. This mean that it should not be saved in output file.
        # True should be later specfieid to save info
        self.hash_data[data_file_name] = (hash, False)
    
    def __load_hashes_info_from_text(self, hash_file_name):
        """
        Ref: https://docs.python.org/3.7/library/collections.html#collections.OrderedDict
        Ref: https://docs.python.org/3/library/re.html
        """
        comment_pattern = re.compile("\s*(#.*)?\n?")
        # Ref: https://stackoverflow.com/questions/50618116/regex-for-finding-file-paths
        # Ref: https://stackoverflow.com/questions/2758921/regular-expression-that-finds-and-replaces-non-ascii-characters-with-python
        hash_record_pattern = re.compile("(?P<hash>[0-9A-Fa-f]+)\s+\*(?P<file>[\\\\/\w.: \\-\u0080-\uFFFF]+)\n?")

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

                self.__load_hash_info_entry(data_file_name, hash, hash_file_name)

                line = f.readline()
                lineIndex += 1

    def __load_hashes_info_from_json(self, hash_file_name):
        """
        Ref: https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        Ref: https://docs.python.org/2/library/json.html
        """
        with open(hash_file_name, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        for hash_record in json_data["data"]:
            data_file_name = hash_record["file_name"]
            hash = hash_record["hash"]
            self.__load_hash_info_entry(data_file_name, hash, hash_file_name)

    def load_hashes_info(self):
        if self.single_hash_file_name_base is None:
            raise Exception("Input file name base is not specified")
        
        hash_file_name = self.get_hash_file_name(None)
        if not os.path.exists(hash_file_name):
            return

        # Dictionary stores pair "absolute file name" -> "(hash, unused status)"
        self.hash_data = dict()

        if self.json_format:
            self.__load_hashes_info_from_json(hash_file_name)
        else:
            self.__load_hashes_info_from_text(hash_file_name)

        self.last_time_load_save = time.time()

    def __save_hashes_info_file(self):
        if not self.suppress_hash_file_comments:
            all_comments = self.hash_file_header_comments
            # Ref: https://blog.finxter.com/python-how-to-count-elements-in-a-list-matching-a-condition/
            # Ref: https://stackoverflow.com/questions/3013449/list-comprehension-vs-lambda-filter
            record_number = sum((v[1][1] or self.preserve_unused_hash_records) for v in self.hash_data.items())
            all_comments.append(f"Number of records: {record_number}.")

        hash_file_name = self.get_hash_file_name(None)

        if self.json_format:
            json_data = {}
        else:
            # Create empty file
            # Ref: https://stackoverflow.com/questions/12654772/create-empty-file-using-python
            open(hash_file_name, "w").close()

        if not self.suppress_hash_file_comments:
            if self.json_format:
                # Ref: https://stackoverflow.com/questions/244777/can-comments-be-used-in-json
                json_data["_comment"] = all_comments
                pass
            else:
                comment_str = "# " + "\n# ".join(all_comments) + "\n"
                with open(hash_file_name, "a") as hash_file:
                    hash_file.write(comment_str)

        if self.json_format:
            # We added data after _comment, so the "_comment" follow above the data.
            # Strictly speaking JSON writer may not preserve such order, but usually does.
            json_data["data"] = []

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

        if self.sort_by_hash_value:
            # Sort by hash. If hashes equal, sort by file name
            key1 = lambda v: (v[1][0].lower(), locale.strxfrm(v[0]).casefold(), locale.strxfrm(v[0]))
        else:
            # Ref: https://stackoverflow.com/questions/1097908/how-do-i-sort-unicode-strings-alphabetically-in-python
            # Ref: https://stackoverflow.com/a/50437802/13441
            # Ref: https://stackoverflow.com/a/1318709/13441
            key1 = lambda v: (locale.strxfrm(v[0]).casefold(), locale.strxfrm(v[0]))
                
        hash_data_sorted.sort(key=key1)

        try:
            if not self.json_format:
                hash_file = open(hash_file_name, "a")

            for data_file_name, hash_info in hash_data_sorted:
                # Check that current hash entry should be stored
                if self.preserve_unused_hash_records or hash_info[1]:
                    if self.json_format:
                        json_data["data"].append({"file_name": data_file_name, "hash": hash_info[0]})
                    else:
                        hash_file.write(f"{hash_info[0]} *{data_file_name}\n")
        finally:
            if not self.json_format:
                hash_file.close()

        if not self.suppress_hash_file_comments:
            if not self.json_format:
                with open(hash_file_name, "a") as hash_file:
                    hash_file.write("# End of file\n")

        if self.json_format:
            with open(hash_file_name, 'w', encoding="utf-8") as f:
                # Ref: https://stackoverflow.com/questions/12943819/how-to-prettyprint-a-json-file
                # Ref: https://stackoverflow.com/questions/16291358/python-saving-json-files-as-utf-8
                json.dump(json_data, f, indent=4, ensure_ascii=False)

    def save_hashes_info(self):
        self.__hash_file_make_backup()
        self.__save_hashes_info_file()
        # Note, in case of exception backup is not cleaned up. But actually this is what we want, because in case of exception we may need to restore data from backup.
        self.__hash_file_del_backup()
        self.last_time_load_save = time.time()

    def get_hash_file_name(self, _):
        ret = f"{self.single_hash_file_name_base}{self.hash_file_name_postfix}"
        return ret

    def __get_backup_hash_file_name(self):
        """
        Return backup file name based on hash file name. Hash file name should be prefix of it

        If there is backup file name then it is generated.
        """
        hash_file_name = self.get_hash_file_name(None)
        if self.__backup_hash_file_name.startswith(hash_file_name):
            return self.__backup_hash_file_name

        # Ref: https://docs.python.org/2/library/uuid.html
        self.__backup_hash_file_name = f"{hash_file_name}.back.{uuid.uuid1()}"
        return self.__backup_hash_file_name

    def __hash_file_make_backup(self):
        hash_file_name = self.get_hash_file_name(None)
        backup_hash_file_name = self.__get_backup_hash_file_name()
        if os.path.isfile(hash_file_name):
            shutil.copyfile(hash_file_name, backup_hash_file_name)
	        #time.sleep(5)

    def __hash_file_del_backup(self):
        backup_hash_file_name = self.__get_backup_hash_file_name()
        if os.path.isfile(backup_hash_file_name):
            os.remove(backup_hash_file_name)

    def has_hash(self, data_file_name):
        self._check_data_hash_files_names_equal(data_file_name, self.get_hash_file_name(None))

        fn = os.path.abspath(data_file_name)
        fn = util.drive_normcase(fn)
        # Ref: https://docs.python.org/3.2/library/os.path.html#os.path.normcase
        if self.norm_case_file_names:
            fn = os.path.normcase(fn)
        ret = fn in self.hash_data
        if ret:
            self.hash_data[fn] = (self.hash_data[fn][0], True)
        return ret

    def __autosave_if_needed(self):
        if self.autosave_timeout == -1:
            return

        if self.autosave_timeout == 0:
            self.save_hashes_info()
            return

        # Ref: https://stackoverflow.com/questions/3638532/find-time-difference-in-seconds-as-an-integer-with-python
        # Ref: https://docs.python.org/3/library/time.html#time.time
        if time.time() - self.last_time_load_save > self.autosave_timeout:
            self.save_hashes_info()
            return

    def set_hash(self, data_file_name, hash_value):
        self._check_data_hash_files_names_equal(data_file_name, self.get_hash_file_name(None))

        fn = os.path.abspath(data_file_name)
        fn = util.drive_normcase(fn)

        # Ref: https://docs.python.org/3.2/library/os.path.html#os.path.normcase
        if self.norm_case_file_names:
            fn = os.path.normcase(fn)
        self.hash_data[fn] = (hash_value, True)

        self.__autosave_if_needed()