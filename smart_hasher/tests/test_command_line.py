import unittest
import smart_hasher
import subprocess
import os
import shutil
import filecmp
import asyncio
import tracemalloc
import filecmp
import tests.test_util

class SimpleCommandLineTestCase(unittest.TestCase):
    """This class contains testing simple functionality from command line"""

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

    def test_calc_hash_for_one_small_file_sha1(self):

        data_file_name = f'{self.work_path}/file1.txt';

        shutil.copyfile(f'{self.data_path}/file1.txt', data_file_name)

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output --suppress-output-file-comments')
        
        with open(f'{self.data_path}/file1.txt.sha1', mode='r') as sha1_expected_file:
            sha1_expected = sha1_expected_file.read()

        with open(f'{self.work_path}/file1.txt.sha1', mode='r') as sha1_actual_file:
            sha1_actual = sha1_actual_file.read()
        sha1_actual = sha1_actual[:40]

        self.assertEqual(sha1_expected, sha1_actual, f'Wrong sha1-hash for file "file1.txt". Expected: "{sha1_expected}", actual: "{sha1_actual}"')

        # Ref: https://docs.python.org/3.7/library/filecmp.html
        self.assertTrue(filecmp.cmp(f'{self.data_path}/file1.txt', data_file_name, shallow=False), f"Input data file is corrupted! ({data_file_name})")

    def test_calc_hash_for_one_small_file_md5(self):
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --hash-algo md5 --suppress-console-reporting-output --suppress-output-file-comments')
        
        with open(f'{self.data_path}/file1.txt.md5', mode='r') as md5_expected_file:
            md5_expected = md5_expected_file.read()

        with open(f'{self.work_path}/file1.txt.md5', mode='r') as md5_actual_file:
            md5_actual = md5_actual_file.read()
        md5_actual = md5_actual[:32]
        self.assertEqual(md5_expected, md5_actual, f'Wrong md5-hash for file "file1.txt". Expected: "{md5_expected}", actual: "{md5_actual}"')

    def test_calc_hash_for_three_small_files_sha1(self):
        for i in range(1, 4):
            shutil.copyfile(f'{self.data_path}/file{i}.txt', f'{self.work_path}/file{i}.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output --suppress-output-file-comments')
        
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

    def test_calc_hash_for_three_small_files_md5(self):
        for i in range(1, 4):
            shutil.copyfile(f'{self.data_path}/file{i}.txt', f'{self.work_path}/file{i}.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --hash-algo md5 --suppress-console-reporting-output --suppress-output-file-comments')
        
        for i in range(1, 4):
            with open(f'{self.data_path}/file{i}.txt.md5', mode='r') as md5_expected_file:
                md5_expected = md5_expected_file.read()

            with open(f'{self.work_path}/file{i}.txt.md5', mode='r') as md5_actual_file:
                md5_actual = md5_actual_file.read()
            md5_actual = md5_actual[:32]
            with self.subTest(i = i):
                self.assertEqual(md5_expected, md5_actual, f'Wrong md5-hash for file "file{i}.txt". Expected: "{md5_expected}", actual: "{md5_actual}"')

    def test_specify_non_existent_file(self):
        exit_code = os.system(f'smart_hasher --input-file {self.work_path}/nofile.txt --suppress-console-reporting-output --retry-pause-on-data-read-error 0')
        self.assertEqual(smart_hasher.ExitCode(exit_code), smart_hasher.ExitCode.DATA_READ_ERROR)

    def test_simple_force_calc_hash(self):
        data_file_name = f"{self.work_path}/file1.txt"
        hash_file_name = f"{data_file_name}.sha1"
        wrong_hash = "<wrong_hash_value>"
        corrent_hash = "e8b0faa145c4590e3e424403e758f6d4b5347c45"

        with open(data_file_name, "w") as f:
            f.write("qwerty1234567890")
        with open(hash_file_name, "w") as f:
            f.write(wrong_hash)

        exit_code = os.system(f'smart_hasher --input-file {data_file_name} --suppress-console-reporting-output') 
        self.assertEqual(exit_code, 0)
        with open(hash_file_name, "r") as f:
            actual_hash = f.read()
        self.assertEqual(wrong_hash, actual_hash)

        exit_code = os.system(f'smart_hasher --input-file {data_file_name} --force-calc-hash --suppress-console-reporting-output --suppress-output-file-comments')
        self.assertEqual(exit_code, 0)
        with open(hash_file_name, "r") as f:
            actual_hash_text = f.read()
        actual_hash = actual_hash_text[:40]
        self.assertEqual(corrent_hash, actual_hash)

    def test_calc_hash_with_comments_in_output_file(self):
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        # Check hash in output file without comments

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output --suppress-output-file-comments --hash-file-name-output-postfix test_hash')

        hash_file_name_expected = f'{self.data_path}/file1.txt.sha1';
        hash_file_name_actual = f'{self.work_path}/file1.txt.sha1.test_hash'; # Note, we also added postfix here in file name, so it is also check during testing

        with open(hash_file_name_expected, mode='r') as hash_file_expected:
            hash_expected = hash_file_expected.read()

        with open(hash_file_name_actual, mode='r') as hash_file_actual:
            hash_actual = hash_file_actual.readline()
        hash_actual = hash_actual[:40]

        self.assertEqual(hash_expected, hash_actual, f'Wrong hash for input file "file1.txt". Expected: "{hash_expected}", actual: "{hash_actual}"')

        os.remove(hash_file_name_actual)

        # Check hash in output file with comments
        
        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output')

        hash_file_name_expected = f'{self.data_path}/file1.txt.sha1';
        hash_file_name_actual = f'{self.work_path}/file1.txt.sha1';

        with open(hash_file_name_expected, mode='r') as hash_file_expected:
            hash_expected = hash_file_expected.read()

        with open(hash_file_name_actual, mode='r') as hash_file_actual:
            hash_actual = hash_file_actual.readline()
            has_comment = False
            while hash_actual.startswith("#"):
                hash_actual = hash_file_actual.readline()
                has_comment = True
        self.assertTrue(has_comment, "Output file should have comment")
        hash_actual = hash_actual[:40]

        self.assertEqual(hash_expected, hash_actual, 'Wrong hash for input file "file1.txt". Expected: "{}", actual: "{}"'.format(hash_expected, hash_actual))

    def test_error_report_on_equal_data_and_hash_file_names(self):
        data_file_name = f'{self.data_path}/file1.txt';
        work_file_name = f'{self.work_path}/file1.txt';

        shutil.copyfile(data_file_name, work_file_name)

        exit_code = os.system(f'smart_hasher --input-file {work_file_name} --suppress-console-reporting-output --suppress-hash-file-name-postfix')
        self.assertEqual(exit_code, smart_hasher.ExitCode.APP_USAGE_ERROR)

        # Ref: https://docs.python.org/3.7/library/filecmp.html
        self.assertTrue(filecmp.cmp(data_file_name, work_file_name, shallow=False), f"Input data file is corrupted! ({work_file_name})")

    #@unittest.skip("This is sandbox, actually not unit test")
    def _test_sandbox(self):
        # Ref: https://docs.python.org/3/library/tracemalloc.html
        tracemalloc.start()

        print("test_dummy run")
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-console-reporting-output')
        
        with open(f'{self.data_path}/file1.txt.sha1', mode='r') as sha1_expected_file:
            sha1_expected = sha1_expected_file.read()

        with open(f'{self.work_path}/file1.txt.sha1', mode='r') as  sha1_actual_file:
            sha1_actual = sha1_actual_file.read()
        sha1_actual = sha1_actual[:40]
        self.assertEqual(sha1_expected, sha1_actual, f'Wrong sha1-hash for file "file1.txt". Expected: "{sha1_expected}", actual: "{sha1_actual}"')

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print("[ Top 10 ]")
        for stat in top_stats[:10]:
            print(stat)

if __name__ == '__main__':
    run_single_test = True
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(SimpleCommandLineTestCase('test_error_report_on_equal_data_and_hash_file_names'))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()
