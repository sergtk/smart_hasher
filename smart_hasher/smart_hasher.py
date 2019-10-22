import hashlib
import sys
import os.path
import time
from datetime import datetime
import math
import argparse

fileChunkSize = 1024 * 1024
# fileChunkSize = 500

sizeNames = ("B", "Kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb")

# Ref: "Better way to convert file sizes in Python" https://stackoverflow.com/a/14822210/13441
def convertSize(sizeBytes: float) -> str:
   global sizeNames

   if sizeBytes == 0:
       return "0 " + sizeNames[0]
   # sizeNames = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(sizeBytes, 1024)))
   p = math.pow(1024, i)
   s = round(sizeBytes / p, 2)
   return "%s %s" % (s, sizeNames[i])

def formatSeconds(seconds: float) -> str:
    # seconds = int(diff.total_seconds());
    sec = int(seconds)
    ret =  "{0}:{1:02d}:{2:02d}".format(int(sec / 60 / 60), int(sec / 60) % 60, sec % 60)
    return ret

# This function is not used 
def calcHash(fileName):
    # Ref: https://www.guru99.com/reading-and-writing-files-in-python.html
    f = open(fileName, "rb")
    hasher = hashlib.md5()
    hasher.update(f.read())
    hash = hasher.hexdigest()
    return hash

# Ref: https://stackoverflow.com/questions/9181859/getting-percentage-complete-of-an-md5-checksum
def calcHashWithProgress(fileName):
    curSize = 0
    prevPercent = 0
    hasher = hashlib.md5()
    totalSize = os.path.getsize(fileName)

    recentMoment = startMoment = datetime.now();
    recentSize = 0
    recentSpeed = 0
    recentSpeedReadable = "-"

    data = True
    f = open(fileName, "rb")

    while data:
        # Read and update digest.
        data = f.read(fileChunkSize)
        curSize += len(data)
        hasher.update(data)

        recentSize += len(data)

        # Calculate progress.
        percent = int(10000 * curSize / totalSize)

        # Ref: https://www.pythoncentral.io/pythons-time-sleep-pause-wait-sleep-stop-your-code/
        # time.sleep(1)

        if percent > prevPercent:
            curMoment = datetime.now();
            elapsedSeconds = (curMoment - startMoment).total_seconds()
            remainSeconds = elapsedSeconds / percent * (10000 - percent);

            speed = curSize / elapsedSeconds;
            speedReadable = convertSize(speed);

            recentSeconds = (curMoment - recentMoment).total_seconds()
            if (recentSeconds > 3 and recentSize > 0):
                recentSpeed = recentSize / recentSeconds
                recentSpeedReadable = convertSize(recentSpeed)
                recentMoment = curMoment
                recentSize = 0

            # Ref: "Using multiple arguments for string formatting in Python (e.g., '%s … %s')" https://stackoverflow.com/a/3395158/13441
            # Ref: "Display number with leading zeros" https://stackoverflow.com/a/134951/13441
            print ('{0}.{1:02d}% done ({2:,d} bytes). Remaining time: {3}. File average speed: {4}/sec. Recent speed: {5}/sec.   \r'.
                   format(int(percent / 100), int(percent % 100), curSize, formatSeconds(remainSeconds), speedReadable, recentSpeedReadable),
                   end="")
            prevPercent = percent
    f.close()
    print ('                                                                                      \r', end="") # Clear line
    return hasher.hexdigest()

def get_output_file_name(inputFileName):
    output_file_name = inputFileName + ".md5"

    if cmd_line_args.hash_file_name_output_postfix:
        output_file_name += "." + cmd_line_args.hash_file_name_output_postfix
    return output_file_name

# Ref: "Argparse Tutorial" https://docs.python.org/3/howto/argparse.html
# Ref: "15.4.3. The add_argument() method" https://docs.python.org/2/library/argparse.html#the-add-argument-method
def parse_command_line():
    global cmd_line_args;

    parser = argparse.ArgumentParser(description='This app is to check hashes of files with extended features.')
    parser.add_argument('--input_file', '-if', action="append", help="Specify one or more input files", required=True, dest='input_file_names')
    parser.add_argument('--hash_file_name_output_postfix', '-op', help="Specify postfix, which will be appended to the end of output file names")

    cmd_line_args = parser.parse_args()

def getDateTimeStr(dateTime: datetime) -> str:
    return dateTime.strftime("%Y.%m.%d %H:%M:%S")

# Returns false if hash not calculated, probably because it was already calculated.
def handle_input_file(inputFileName):
    startDateTime = datetime.now();
    print("Handle file start time: " + getDateTimeStr(startDateTime) + " (" + inputFileName + ")")
    outputFileName = get_output_file_name(inputFileName)
    # Ref: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
    if (os.path.exists(outputFileName)):
        print("Output file name '" + outputFileName + "' exists ... calculation of hash skipped.")
        return False
    print("Calculate hash for file '" + inputFileName + "'...")
    # hash = calcHash(inputFileName)
    hash = calcHashWithProgress(inputFileName)

    # Ref: https://stackoverflow.com/questions/6159900/correct-way-to-write-line-to-file
    with open(outputFileName, 'a') as outputFile:
        # outputFile.write("# MD5 hash generated by smart_hasher\n\n")
        outputFile.write(hash + " *" + inputFileName + "\n")

    print("HASH: ", hash, "(" + outputFileName + ")")

    endDateTime = datetime.now();
    print("Handle file end time: " + getDateTimeStr(endDateTime) + " (" + inputFileName + ")")
    seconds = int((endDateTime - startDateTime).total_seconds());
    # print("Elapsed time: {0}:{1:02d}:{2:02d}".format(int(seconds / 60 / 60), int(seconds / 60) % 60, seconds % 60))

    fileSize = os.path.getsize(inputFileName)
    speed = fileSize / seconds if seconds > 0 else 0
    print("Elapsed time: {0} (Average speed: {1}/sec)".format(formatSeconds(seconds), convertSize(speed)))
      
    return True
try:
    parse_command_line()

    for input_file_name in cmd_line_args.input_file_names:
        if (not handle_input_file(input_file_name)):
            exit(10)

except Exception as ex:
    print("Exception thrown:\n", ex)
