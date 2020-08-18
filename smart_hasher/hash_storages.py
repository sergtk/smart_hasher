import abc
import os
import util

class HashStorageAbstract(abc.ABC):

    def __init__(self, hash_file_name_postfix, use_absolute_file_names = False):
        self.hash_file_name_postfix = hash_file_name_postfix
        self.use_absolute_file_names = use_absolute_file_names
        self.hash_file_header_comments = None # The default is None to throw exception if not assigned so to catch error early
        self.suppress_hash_file_comments = False

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
        return ret

    def has_hash(self, data_file_name):
        # Ref: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists/
        hash_file_name = self.get_hash_file_name(data_file_name)
        if not os.path.exists(hash_file_name):
            return False
        if not os.path.isfile(hash_file_name):
            raise Exception(f"Path '{hash_file_ame}' is dir and can't be used to save hash value")
        return True

    def set_hash(self, data_file_name, hash_value):
        hash_file_name = self.get_hash_file_name(data_file_name)
        
        # Ref: https://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file
        with open(hash_file_name, 'w') as hash_file:
            if not self.suppress_hash_file_comments:
                hash_file.write(self.hash_file_header_comments)
            data_file_name_user = util.rel_file_path(data_file_name, hash_file_name, self.use_absolute_file_names)
            hash_file.write(hash_value + " *" + data_file_name_user + "\n")

class SingleFileHashesStorage(HashStorageAbstract):

    def load_hashes_info(self):
		# TODO: implement
        pass

    def save_hashes_info(self):
		# TODO: implement
        pass

    def get_hash_file_name(self, data_file_name):
		# TODO: implement
        ret = os.path.abspath(data_file_name) + self.hash_file_name_postfix
        return ret

    def has_hash(self, data_file_name):
		# TODO: implement
        # Ref: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists/
        hash_file_name = self.get_hash_file_name(data_file_name)
        if not os.path.exists(hash_file_name):
            return False
        if not os.path.isfile(hash_file_name):
            raise Exception(f"Path '{hash_file_ame}' is dir and can't be used to save hash value")
        return True

    def set_hash(self, data_file_name, hash_value):
		# TODO: implement
        hash_file_name = self.get_hash_file_name(data_file_name)
        
        # Ref: https://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file
        with open(hash_file_name, 'w') as hash_file:
            if not self.suppress_hash_file_comments:
                hash_file.write(self.hash_file_header_comments)
            data_file_name_user = util.rel_file_path(data_file_name, hash_file_name, self.use_absolute_file_names)
            hash_file.write(hash_value + " *" + data_file_name_user + "\n")

