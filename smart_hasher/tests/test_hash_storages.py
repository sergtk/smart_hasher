import smart_hasher
import unittest
import os
import shutil
import tests.util_test
import hash_storages
import filecmp
import cmd_line

class SingleFileHashesStorageTestCase(unittest.TestCase):

    def  setUp(self):
        # Ref: https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        # Ref: https://stackoverflow.com/questions/17353213/init-for-unittest-testcase
        # Ref: https://radek.io/2011/07/21/static-variables-and-methods-in-python/
        self.data_path = tests.util_test.get_data_path()
        self.work_path = tests.util_test.get_work_path()
        tests.util_test.clean_work_dir()

    # Ref: https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown
    def  tearDown(self):
        tests.util_test.clean_work_dir()

    def test_hash_storages_load_save(self):
        hash_storage_file = "dummy_hash_storage_2_general_rel.sha1"
        tests.util_test.clean_work_dir()

        work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
        data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
        shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

        hash_storage = hash_storages.SingleFileHashesStorage()
        hash_storage.single_hash_file_name_base = work_hash_storage_file
        hash_storage.suppress_hash_file_comments = True
        hash_storage.preserve_unused_hash_records = True

        hash_storage.load_hashes_info()
        hash_storage.save_hashes_info()

        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file + ".save", shallow=False), f"Wrong data on output '{data_hash_storage_file}'")

    def test_cli_simple_hash_storages_rel(self):
        for hash_storage_file in ["dummy_hash_storage_2_general_rel.sha1", "dummy_hash_storage_5_non-ascii.sha1"]:
            tests.util_test.clean_work_dir()

            data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
            work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
            shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

            cl = f"smart_hasher --input-folder {self.work_path} --input-folder-file-mask-exclude * --suppress-output-file-comments " \
                 f"--single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix " \
                 f"--preserve-unused-hash-records"

            # Run command which does not handle any files
            exit_code = os.system(cl)
            # --suppress-console-reporting-output
            self.assertEqual(exit_code, cmd_line.ExitCode.OK)

            self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file + ".save", shallow=False), f"Wrong data on output (file '{data_hash_storage_file}')")

    def test_cli_simple_hash_storages_abs(self):
        hash_storage_file = "dummy_hash_storage_1_general_abs.sha1"
        tests.util_test.clean_work_dir()

        data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
        work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
        shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

        cl = f"smart_hasher --input-folder {self.work_path} --input-folder-file-mask-exclude * --suppress-output-file-comments " \
             f"--single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix --use-absolute-file-names " \
             f"--preserve-unused-hash-records"

        # Run command which does not handle any files
        exit_code = os.system(cl)
        # --suppress-console-reporting-output
        self.assertEqual(exit_code, cmd_line.ExitCode.OK)

        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file + ".save", shallow=False), f"Wrong data on output (file '{data_hash_storage_file}')")

    def test_cli_wrong_input_hash_file(self):
        for fi in [1, 2, 3]:
            tests.util_test.clean_work_dir()

            hash_storage_file = f"dummy_hash_storage_4_wrong_format_{fi}.sha1"

            data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
            work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
            shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

            cl = f"smart_hasher --input-folder {self.work_path} --input-folder-file-mask-exclude * --suppress-console-reporting-output " \
                        f"--single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix --use-absolute-file-names"

            # Run command which does not handle any files
            exit_code = os.system(cl)
            self.assertEqual(exit_code, cmd_line.ExitCode.APP_USAGE_ERROR)
            self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file, shallow=False), f"Invalid input hash file is corrupted (file '{work_hash_storage_file}')")


    # Test that error reported when data file and hash file are the same
    def test_cli_error_on_equal_data_and_hash_file_names(self):
        for single_hash_file in [False, True]:
            tests.util_test.clean_work_dir()

            hash_storage_file = f"dummy_hash_storage_1_general_abs.sha1"

            data_hash_storage_file = os.path.join(self.data_path, "hash_storages", hash_storage_file)
            work_hash_storage_file = os.path.join(self.work_path, hash_storage_file)
            shutil.copyfile(data_hash_storage_file, work_hash_storage_file)

            # cmd_line = f"smart_hasher --input-file {work_hash_storage_file} --single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix " \
            cl = f"smart_hasher --input-file {work_hash_storage_file} --suppress-hash-file-name-postfix" \
                        " --suppress-console-reporting-output"
            if single_hash_file:
                cl += f" --single-hash-file-name-base {work_hash_storage_file}"

            # Run command which does not handle any files
            exit_code = os.system(cl)
            # --suppress-console-reporting-output
            self.assertEqual(exit_code, cmd_line.ExitCode.APP_USAGE_ERROR)
            self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file, shallow=False), f"Input hash file is corrupted (file '{work_hash_storage_file}')")

    def test_cli_unused_hash_records(self):
        for i in range(1, 4):
            shutil.copyfile(f"{self.data_path}/file{i}.txt", f"{self.work_path}/file{i}.txt")

        work_hash_storage_file = f"{self.work_path}/hash_storage.sha1"
        data_hash_storage_file_123 = f"{self.data_path}/hash_storage_123.sha1"
        data_hash_storage_file_24 = f"{self.data_path}/hash_storage_24.sha1"

        exit_code = os.system(f"smart_hasher --input-folder {self.work_path} --single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix "
                               "--suppress-console-reporting-output --suppress-output-file-comments")
        self.assertEqual(exit_code, cmd_line.ExitCode.OK)
        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file_123, shallow=False), f"Incorrect output hash file (file '{work_hash_storage_file}')")

        exit_code = os.system(f"smart_hasher --input-file {self.work_path}/file3.txt --input-file {self.work_path}/file2.txt "
                              f"--preserve-unused-hash-records " # Essence of the test
                              f"--single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix "
                              f"--suppress-console-reporting-output --suppress-output-file-comments")
        self.assertEqual(exit_code, cmd_line.ExitCode.OK)
        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file_123, shallow=False), f"Incorrect output hash file (file '{work_hash_storage_file}')")

        shutil.copyfile(f"{self.data_path}/file4.txt", f"{self.work_path}/file4.txt")
        exit_code = os.system(f"smart_hasher --input-file {self.work_path}/file4.txt --input-file {self.work_path}/file2.txt "
                              f"--single-hash-file-name-base {work_hash_storage_file} --suppress-hash-file-name-postfix "
                              f"--suppress-console-reporting-output --suppress-output-file-comments")
        self.assertEqual(exit_code, cmd_line.ExitCode.OK)
        self.assertTrue(filecmp.cmp(work_hash_storage_file, data_hash_storage_file_24, shallow=False), f"Incorrect output hash file (file '{work_hash_storage_file}')")

    def test_sort_non_ascii_file_names(self):
        for fn in ["а кириллическое.txt", "В прописное.txt", "в строчное.txt", "имя_без_пробелов.txt", "українська мова.txt", "Л_вначале.txt"]:
            shutil.copyfile(os.path.join(self.data_path, "cyrillic_files", fn), os.path.join(self.work_path, fn))

        os.system(f"smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output --suppress-output-file-comments --single-hash-file-name-base {self.work_path}/hash_storage")
        # os.system(f"smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output --suppress-output-file-comments")
        
        return

        for i in range(1, 4):
            with open(f'{self.data_path}/file{i}.txt.sha1', mode='r') as sha1_expected_file:
                sha1_expected = sha1_expected_file.read()

            with open(f'{self.work_path}/file{i}.txt.sha1', mode='r') as sha1_actual_file:
                sha1_actual = sha1_actual_file.read()
            sha1_actual = sha1_actual[:40]
            with self.subTest(i = i):
                self.assertEqual(sha1_expected, sha1_actual, f'Wrong sha1-hash for file "file{i}.txt". Expected: "{sha1_expected}", actual: "{sha1_actual}"')

            with self.subTest(i = i):
                # Ref: https://docs.python.org/3.7/library/filecmp.html
                self.assertTrue(filecmp.cmp(f'{self.data_path}/file{i}.txt', f'{self.work_path}/file{i}.txt', shallow=False), f"Input data file is corrupted! ({'self.work_path}/file{i}.txt'})")


if __name__ == '__main__':
    run_single_test = True
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(SingleFileHashesStorageTestCase("test_sort_non_ascii_file_names"))
        #suite.addTest(SingleFileHashesStorageTestCase("test_cli_simple_hash_storages_rel"))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()
