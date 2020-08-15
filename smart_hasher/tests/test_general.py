import os
import unittest
#import smart_hasher
import hash_calc

class SimpleInputsTestCase(unittest.TestCase):
    """This class contains testing simple functionality"""

    data_path = os.getcwd() + '/tests/data'

    def test_calc_hash_for_one_small_file(self):
        # Ref: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
        #cwd = os.getcwd()
        #print('current dir = ' + cwd)

        # Ref: https://matthew-brett.github.io/teaching/string_formatting.html#option-2-f-strings-in-python-3-6
        file_name = f'{self.data_path}/file1.txt'

        calc = hash_calc.FileHashCalc()
        calc.file_name = file_name
        calc.suppress_console_reporting_output = True

        with open(f'{self.data_path}/file1.txt.sha1', mode='r') as sha1_expected_file:
            sha1_expected = sha1_expected_file.read()

        calc.hash_str = "sha1"
        calc_res = calc.run()
        self.assertEqual(calc_res, hash_calc.FileHashCalc.ReturnCode.OK)
        sha1_actual = calc.result
        self.assertEqual(sha1_expected, sha1_actual)

        with open(f'{self.data_path}/file1.txt.md5', mode='r') as md5_expected_file:
            md5_expected = md5_expected_file.read()

        calc.hash_str = "md5"
        calc_res = calc.run()
        self.assertEqual(calc_res, hash_calc.FileHashCalc.ReturnCode.OK)
        md5_actual = calc.result
        self.assertEqual(md5_expected, md5_actual)

    def test_calc_hash_for_three_small_files(self):
        calc = hash_calc.FileHashCalc()
        calc.suppress_console_reporting_output = True

        for i in range(1, 4):
            file_name = f'{self.data_path}/file{i}.txt'
            calc.file_name = file_name

            with open(f'{self.data_path}/file{i}.txt.sha1', mode='r') as sha1_expected_file:
                sha1_expected = sha1_expected_file.read()
            calc.hash_str = "sha1"
            calc_res = calc.run()
            self.assertEqual(calc_res, hash_calc.FileHashCalc.ReturnCode.OK)
            sha1_actual = calc.result
            self.assertEqual(sha1_expected, sha1_actual)

            with open(f'{self.data_path}/file{i}.txt.md5', mode='r') as md5_expected_file:
                md5_expected = md5_expected_file.read()
            calc.hash_str = "md5"
            calc_res = calc.run()
            self.assertEqual(calc_res, hash_calc.FileHashCalc.ReturnCode.OK)
            md5_actual = calc.result
            self.assertEqual(md5_expected, md5_actual)

if __name__ == '__main__':
    run_single_test = True
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(SimpleInputsTestCase('test_calc_hash_for_one_small_file'))
        #suite.run()
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()
