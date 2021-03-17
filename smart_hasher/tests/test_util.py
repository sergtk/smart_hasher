import math
import unittest
#import smart_hasher
#import hash_calc
import util

class UtilTestCase(unittest.TestCase):
    """This class contains testing functionality for utils
       In fact this is more about regression tests that the only values allowed for output. If output is improved then tests may be adjusted"""

    def test_convert_size_to_display(self):

        actual_result = util.convert_size_to_display(0)
        self.assertEqual(actual_result, "0 B")

        actual_result = util.convert_size_to_display(1023)
        self.assertEqual(actual_result, "1023.0 B")

        actual_result = util.convert_size_to_display(1024)
        self.assertEqual(actual_result, "1.0 KiB")

        actual_result = util.convert_size_to_display(1025)
        self.assertEqual(actual_result, "1.0 KiB")

        actual_result = util.convert_size_to_display(10 * 1024)
        self.assertEqual(actual_result, "10.0 KiB")

        actual_result = util.convert_size_to_display(10 * 1024)
        self.assertEqual(actual_result, "10.0 KiB")

        actual_result = util.convert_size_to_display(10 * 1024 * 1024)
        self.assertEqual(actual_result, "10.0 MiB")

        actual_result = util.convert_size_to_display(10 * 1024 * 1024 * 1024 * 1024 * 1024)
        self.assertEqual(actual_result, "10.0 PiB")

        actual_result = util.convert_size_to_display(1049359643456945)
        self.assertEqual(actual_result, "954.39 TiB")

        actual_result = util.convert_size_to_display(-100)
        self.assertEqual(actual_result, "-100.0 B")

        actual_result = util.convert_size_to_display(-12345678)
        self.assertEqual(actual_result, "-11.77 MiB")

        actual_result = util.convert_size_to_display(math.inf)
        self.assertEqual(actual_result, "infinity")

        actual_result = util.convert_size_to_display(-math.inf)
        self.assertEqual(actual_result, "-infinity")

if __name__ == '__main__':
    run_single_test = True
    if run_single_test:
        # Run single test
        # https://docs.python.org/3/library/unittest.html#organizing-test-code
        suite = unittest.TestSuite()
        suite.addTest(UtilTestCase('test_convert_size_to_display'))
        #suite.run()
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        unittest.main()
