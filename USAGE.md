    usage: smart_hasher.py [-h] [--input-file INPUT_FILE]
                           [--input-folder INPUT_FOLDER]
                           [--input-folder-file-mask-include INPUT_FOLDER_FILE_MASK_INCLUDE]
                           [--input-folder-file-mask-exclude INPUT_FOLDER_FILE_MASK_EXCLUDE]
                           [--hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX]
                           [--hash-algo {md5,sha1,sha224,sha256,sha384,sha512}]
                           [--suppress-output]
                           [--pause-after-file PAUSE_AFTER_FILE]
                           [--retry-count-on-data-read-error RETRY_COUNT_ON_DATA_READ_ERROR]
                           [--retry-pause-on-data-read-error RETRY_PAUSE_ON_DATA_READ_ERROR]
                           [--force-calc-hash] [--add-output-file-name-time-stamp]

    This application is to calculate hashes of files with extended features: support of show progress,
    folders and file masks for multiple files, skip calculation of handled files etc...

    Application exit codes:
     0 - OK: everthing fine. Program executed successfully
     2 - OK_SKIPPED_ALREADY_CALCULATED: everything fine. OK may be returned anyway if file(s) is skipped because the hash is already calculated.
     7 - FAILED: general failure, more specific information is not available.
     8 - PROGRAM_INTERRUPTED_BY_USER
     9 - DATA_READ_ERROR: there was error(s) when reading some file(s). Probably hash is not calculated for all files
    10 - EXCEPTION_THROWN_ON_PROGRAM_EXECUTION
    11 - INVALID_COMMAND_LINE_PARAMETERS

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
                            Separate multiple masks with semicolon (;)
      --input-folder-file-mask-exclude INPUT_FOLDER_FILE_MASK_EXCLUDE, -ifoe INPUT_FOLDER_FILE_MASK_EXCLUDE
                            Specify file mask to exclude for input folder. It is
                            applied after --input-folder-file-mask-include.
                            Separate multiple masks with semicolon (;)
      --hash-file-name-output-postfix HASH_FILE_NAME_OUTPUT_POSTFIX, -op HASH_FILE_NAME_OUTPUT_POSTFIX
                            Specify postfix, which will be appended to the end of
                            output file names. This is to specify for different
                            contextes, e.g. if file name ends with ".md5", then it
                            ends with "md5.<value>"
      --hash-algo {md5,sha1,sha224,sha256,sha384,sha512}
                            Specify hash algo (default: sha1)
      --suppress-output, -so
                            Suppress console output
      --pause-after-file PAUSE_AFTER_FILE, -pf PAUSE_AFTER_FILE
                            Specify pause after every file handled, in seconds.
                            Note, if file is skipped, then no pause applied
      --retry-count-on-data-read-error RETRY_COUNT_ON_DATA_READ_ERROR
                            Specify count of retries on data read error (default:
                            5)
      --retry-pause-on-data-read-error RETRY_PAUSE_ON_DATA_READ_ERROR
                            Specify pause before retrying on data read error, in
                            seconds (default: 30)
      --force-calc-hash, -fch
                            If specified than hash calculated always. If not, then
                            hash is not calculated if file with hash already exist
      --add-output-file-name-time-stamp
                            Add time stamp to the output files. Note, that the
                            time on program run taken. So it may differ from the
                            file creation time, but it is equal for all files in
                            one run
