import argparse

parser = argparse.ArgumentParser(description='Short sample app')
parser.add_argument('-a', action="store_true", default=False, help="aaaaaaaaaaaaaaaaaaaaaaaaa")
parser.add_argument('--bar', '-b', action="store", dest="b", help="bbbbbbbbbbbbbbbbbbbbbbbb")
parser.add_argument('-c', action="store", dest="c", type=int, help="ccccccccccccccccccccccc")
parser.add_argument('--input_file', '-if', action="append", help="specify one or multiple files")

# args = parser.parse_args(['-a', '--bar=val', '-c', '3'])
args = parser.parse_args()

if not args.input_file:
    print("Input file is not specified")
else:
    print("input file: " + str(args.input_file))

