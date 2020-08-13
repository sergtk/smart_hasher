import unittest
import smart_hasher
import subprocess
import os
import shutil
import filecmp
import asyncio
import tracemalloc

class SimpleCommandLineTestCase(unittest.TestCase):
    """This class contains testing simple functionality from command line"""

    def  setUp(self):
        # Ref: https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        # Ref: https://stackoverflow.com/questions/17353213/init-for-unittest-testcase
        # Ref: https://radek.io/2011/07/21/static-variables-and-methods-in-python/
        self.data_path = os.getcwd() + '/tests/data'
        self.work_path = os.getcwd() + '/tests/tmp'
        self.clean_work_dir()

    def clean_work_dir(self):
        # Ref: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
        for filename in os.listdir(self.work_path):
            file_path = os.path.join(self.work_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                raise Exception(f'Failed to delete "{file_path}"', e)

    def test_calc_hash_for_one_small_file_sha1(self):
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-output')
        
        with open(f'{self.data_path}/file1.txt.sha1', mode='r') as sha1_expected_file:
            sha1_expected = sha1_expected_file.read()

        with open(f'{self.work_path}/file1.txt.sha1', mode='r') as sha1_actual_file:
            sha1_actual = sha1_actual_file.read()
        sha1_actual = sha1_actual[:40]

        self.assertEqual(sha1_expected, sha1_actual, f'Wrong sha1-hash for file "file1.txt". Expected: "{sha1_expected}", actual: "{sha1_actual}"')

    def test_calc_hash_for_one_small_file_md5(self):
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --hash-algo md5 --suppress-output')
        
        with open(f'{self.data_path}/file1.txt.md5', mode='r') as md5_expected_file:
            md5_expected = md5_expected_file.read()

        with open(f'{self.work_path}/file1.txt.md5', mode='r') as md5_actual_file:
            md5_actual = md5_actual_file.read()
        md5_actual = md5_actual[:32]
        self.assertEqual(md5_expected, md5_actual, f'Wrong md5-hash for file "file1.txt". Expected: "{md5_expected}", actual: "{md5_actual}"')

    def test_calc_hash_for_three_small_files_sha1(self):
        for i in range(1, 4):
            shutil.copyfile(f'{self.data_path}/file{i}.txt', f'{self.work_path}/file{i}.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-output')
        
        for i in range(1, 4):
            with open(f'{self.data_path}/file{i}.txt.sha1', mode='r') as sha1_expected_file:
                sha1_expected = sha1_expected_file.read()

            with open(f'{self.work_path}/file{i}.txt.sha1', mode='r') as sha1_actual_file:
                sha1_actual = sha1_actual_file.read()
            sha1_actual = sha1_actual[:40]
            with self.subTest(i = i):
                self.assertEqual(sha1_expected, sha1_actual, f'Wrong sha1-hash for file "file{i}.txt". Expected: "{sha1_expected}", actual: "{sha1_actual}"')

    def test_calc_hash_for_three_small_files_md5(self):
        for i in range(1, 4):
            shutil.copyfile(f'{self.data_path}/file{i}.txt', f'{self.work_path}/file{i}.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --hash-algo md5 --suppress-output')
        
        for i in range(1, 4):
            with open(f'{self.data_path}/file{i}.txt.md5', mode='r') as md5_expected_file:
                md5_expected = md5_expected_file.read()

            with open(f'{self.work_path}/file{i}.txt.md5', mode='r') as md5_actual_file:
                md5_actual = md5_actual_file.read()
            md5_actual = md5_actual[:32]
            with self.subTest(i = i):
                self.assertEqual(md5_expected, md5_actual, f'Wrong md5-hash for file "file{i}.txt". Expected: "{md5_expected}", actual: "{md5_actual}"')

    @unittest.skip("This is sandbox, actually not unit test")
    def _test_sandbox(self):
        # Ref: https://docs.python.org/3/library/tracemalloc.html
        tracemalloc.start()

        print("test_dummy run")
        shutil.copyfile(f'{self.data_path}/file1.txt', f'{self.work_path}/file1.txt')

        os.system(f'smart_hasher --input-folder {self.work_path} --suppress-output')
        
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
        print('^^^^^^^^^^^^^^ completed ^^^^^^^^^^^^^^^^^')

if __name__ == '__main__':
    run_single_test = False
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(SimpleCommandLineTestCase('test_calc_hash_for_one_small_file_sha1'))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()