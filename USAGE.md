    usage: smart_hasher.py [-h] --input-file INPUT_FILE
                           [--hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX]
                           [--hash-algo {sha256,md5,sha512,sha224,sha384,sha1}]

    This application is to calculate hashes of files with extended features.

    optional arguments:
      -h, --help            show this help message and exit
      --input-file INPUT_FILE, -if INPUT_FILE
                            Specify one or more input files
      --hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX, -op HASH_FILE_NAME_OUTPUT_POSTFIX
                            Specify postfix, which will be appended to the end of
                            output file names. This is to specify for different
                            contextes, e.g. if file name ends with ".md5", then it
                            ends with "md5.<value>"
      --hash-algo {sha256,md5,sha512,sha224,sha384,sha1}
                            Specify hash algo (default: sha1)
