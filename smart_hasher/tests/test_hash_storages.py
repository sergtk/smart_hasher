import smart_hasher
import unittest
import os
import shutil
import tests.test_util
import hash_storages
import filecmp

class SingleFileHashesStorageTestCase(unittest.TestCase):

    def  setUp(self):
        # Ref: https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        # Ref: https://stackoverflow.com/questions/17353213/init-for-unittest-testcase
        # Ref: https://radek.io/2011/07/21/static-variables-and-methods-in-python/
        self.data_path = tests.test_util.get_data_path()
        self.work_path = tests.test_util.get_work_path()
        tests.test_util.clean_work_dir()

    # Ref: https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown
    def  tearDown(self):
        tests.test_util.clean_work_dir()

    def test_hash_storages_load_save(self):
        hash_storage_file = "dummy_hash_storage_2_general_rel.sha1"
        tests.test_util.clean_work_dir()

        work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
        data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
        shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

        hash_storage = hash_storages.SingleFileHashesStorage()
        hash_storage.single_hash_file_name_base = work_hash_storage_file
        hash_storage.suppress_hash_file_comments = True

        hash_storage.load_hashes_info()
        hash_storage.save_hashes_info()

        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file + ".save", shallow=False), f"Wrong data on output")

    # TODO: use relative file names on output
    @unittest.skip("not implemented")
    def test_cli_simple_hash_storages_rel(self):
        for hash_storage_file in ["dummy_hash_storage_1_general_rel.sha1", "dummy_hash_storage_4_non-ascii-UTF-8.sha1"]:
            tests.test_util.clean_work_dir()

            full_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
            shutil.copyfile(os.path.join(self.data_path, "hash_storages", hash_storage_file), full_hash_storage_file)

            cmd_line = f"smart_hasher --input-folder {self.work_path} --input-folder-file-mask-exclude * --suppress-output-file-comments " \
                       f"--single-hash-file-name-base {full_hash_storage_file} --suppress-hash-file-name-postfix"

            # Run command which does not handle any files
            exit_code = os.system(cmd_line)
            # --suppress-console-reporting-output
            self.assertEqual(exit_code, smart_hasher.ExitCode.OK)


    # TODO: use absolute file names on output
    # input file: dummy_hash_storage_1_general_abs.sha1
    @unittest.skip("not implemented")
    def test_cli_simple_hash_storages_abs(self):
        pass
        

if __name__ == '__main__':
    run_single_test = True
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(SingleFileHashesStorageTestCase('test_hash_storages_load_save'))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()
