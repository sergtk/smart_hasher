import os
import unittest
import smart_hasher

class SimpleInputsTestCase(unittest.TestCase):
    """This class contains testing simple functionality"""

    data_path = os.getcwd() + "/tests/data"

    def test_calc_hash_for_one_small_file(self):
        # Ref: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
        #cwd = os.getcwd()
        #print("current dir = " + cwd)

        # Ref: https://matthew-brett.github.io/teaching/string_formatting.html#option-2-f-strings-in-python-3-6
        file_name = f"{self.data_path}/file1.txt"

        sha1_expected_file = open(f"{self.data_path}/file1.txt.sha1", mode='r')
        sha1_expected = sha1_expected_file.read()
        sha1_actual = smart_hasher.calc_hash(file_name, "sha1")
        #print(sha1_actual)
        self.assertEqual(sha1_expected, sha1_actual)

        md5_expected_file = open(f"{self.data_path}/file1.txt.md5", mode='r')
        md5_expected = md5_expected_file.read()
        md5_actual = smart_hasher.calc_hash(file_name, "md5")
        #print(md5_actual)
        self.assertEqual(md5_expected, md5_actual)

    def test_calc_hash_for_three_small_files(self):
        for i in range(1, 4):
            file_name = f"{self.data_path}/file{i}.txt"

            sha1_expected_file = open(f"{self.data_path}/file{i}.txt.sha1", mode='r')
            sha1_expected = sha1_expected_file.read()
            sha1_actual = smart_hasher.calc_hash(file_name, "sha1")
            self.assertEqual(sha1_expected, sha1_actual)

            md5_expected_file = open(f"{self.data_path}/file{i}.txt.md5", mode='r')
            md5_expected = md5_expected_file.read()
            md5_actual = smart_hasher.calc_hash(file_name, "md5")
            self.assertEqual(md5_expected, md5_actual)

    def test_dummy(self):
        self.assertTrue('FOO'.isupper())
        # self.assertTrue('foo'.isupper())

if __name__ == '__main__':
    #unittest.main()

    # Run single test
    # https://docs.python.org/3/library/unittest.html#organizing-test-code
    suite = unittest.TestSuite()
    suite.addTest(SimpleInputsTestCase('test_calc_hash_for_one_small_file'))
    #suite.run()
    runner = unittest.TextTestRunner()
    runner.run(suite)
