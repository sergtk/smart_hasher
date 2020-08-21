# smart_hasher

## Rationale

This app is to calculate hashes of files with many advanced features.

One of cases e.g. if it is needed to check integrity of the large files with the slow connection. In such case network interruption may happened, slow speed and/or hang up.
When calculating a hash the progress is shown so you can get an idea about network speed.

Another use case is to generate hashes for the large bunch of files, and after some time run smart_hasher again.
Then compare old and new file and get info on change.
To support this scenaria when multiple hashes are stored in one hash file, the lines of that file are sorted by file names.

it is good to quickly diagnose such issues. And if the job is interrupted, it should be easy to continue, preserving previously generated hashes.
Utility just check if hash already calculated, and skip calulcation for that files. So it is easy to resume the work, just to rerun the util. It just skips what is already calculated.

To calculate hash for already calculated file, you may add postfix for output files, in such a way you may have several hash files, which are easy to compare

## Usage

Please check [USAGE.md](USAGE.md) file

## Some features supported

* Show speed for overall file and current speed. This is especially useful on non-robust connection.
* Retry on error.
* Skip files for which hashes already calculated. This is convenient when process is interrupted and resumed later.
* Multiple files.
* Many popular hash algorithms.
* Save hashes for many input files in one output file or for one output file per input file.
