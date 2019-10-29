    usage: smart_hasher.py [-h] [--input-file INPUT_FILE]
                           [--input-folder INPUT_FOLDER]
                           [--input-folder-file-mask-include INPUT_FOLDER_FILE_MASK_INCLUDE]
                           [--input-folder-file-mask-exclude INPUT_FOLDER_FILE_MASK_EXCLUDE]
                           [--hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX]
                           [--hash-algo {md5,sha1,sha224,sha256,sha384,sha512}]
                           [--pause-after-file PAUSE_AFTER_FILE]

    This application is to calculate hashes of files with extended features.

    optional arguments:
      -h, --help            show this help message and exit
      --input-file INPUT_FILE, -if INPUT_FILE
                            Specify one or more input files
      --input-folder INPUT_FOLDER, -ifo INPUT_FOLDER
                            Specify one or more input folders. All files in folder
                            are handled recursively
      --input-folder-file-mask-include INPUT_FOLDER_FILE_MASK_INCLUDE, -ifoi INPUT_FOLDER_FILE_MASK_INCLUDE
                            Specify file mask to include for input folder. All
                            files in the folder considered if not specified.
                            Separate multiple mask with semicolon (;)
      --input-folder-file-mask-exclude INPUT_FOLDER_FILE_MASK_EXCLUDE, -ifoe INPUT_FOLDER_FILE_MASK_EXCLUDE
                            Specify file mask to exclude for input folder. It is
                            applied after --input-folder-file-mask-include.
                            Separate multiple mask with semicolon (;)
      --hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX, -op HASH_FILE_NAME_OUTPUT_POSTFIX
                            Specify postfix, which will be appended to the end of
                            output file names. This is to specify for different
                            contextes, e.g. if file name ends with ".md5", then it
                            ends with "md5.<value>"
      --hash-algo {md5,sha1,sha224,sha256,sha384,sha512}
                            Specify hash algo (default: sha1)
      --pause-after-file PAUSE_AFTER_FILE, -pf PAUSE_AFTER_FILE
                            Specify pause after every file handled, in seconds.
                            Note, if file is skipped, then no pause applied
