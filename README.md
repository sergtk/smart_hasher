# smart_hasher

## Rationale

This app is to calculate hashes of files with extended features.

One of cases e.g. if it is needed to check integrity of the large files with the slow connection. In such case network interruption may happened, slow speed and/or hang up.
When calculating a hash the progress is shown so you can get an idea about network speed.

it is good to quickly diagnose such issues. And if the job is interrupted, it should be easy to continue, preserving previously generated hashes.
Utility just check if hash already calculated, and skip calulcation for that files. So it is easy to resume the work, just to rerun the util. It just skip what is already calculated.

To calculate hash for already calculated file, you may add postfix for output files, in such a way you may have several hash files, which are easy to compare

## Usage

Please check [USAGE.md](USAGE.md) file
