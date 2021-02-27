import sys
import hash_calc
from pprint import pprint
import cmd_line

# breakpoint()
cmd_line_args = None

if __name__ == '__main__':

    cmd_line_adapter = cmd_line.CommandLineAdapter()
    res = cmd_line_adapter.run(sys.argv[1:])

    # cmd_line_args, parse_res = cmd_line.parse_cmd_line()

    sys.exit(int(res[1]))
