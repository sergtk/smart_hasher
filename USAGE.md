    usage: smart_hasher.py [-h] --input_file INPUT_FILE
                           [--hash_file_name_output_postfix HASH_FILE_NAME_OUTPUT_POSTFIX]
                           [--hash_algo {md5,sha224,sha1,sha512,sha384,sha256}]

    This application is to calculate hashes of files with extended features.

    optional arguments:
      -h, --help            show this help message and exit
      --input_file INPUT_FILE, -if INPUT_FILE
                            Specify one or more input files
      --hash_file_name_output_postfix HASH_FILE_NAME_OUTPUT_POSTFIX, -op HASH_FILE_NAME_OUTPUT_POSTFIX
                            Specify postfix, which will be appended to the end of
                            output file names. This is to specify for different
                            contextes, e.g. if file name ends with ".md5", then it
                            ends with "md5.<value>"
      --hash_algo {md5,sha224,sha1,sha512,sha384,sha256}
                            Specify hash algo (default: sha1)
