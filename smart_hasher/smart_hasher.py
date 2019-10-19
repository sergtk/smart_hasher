import hashlib
import sys
import os.path
import time
from datetime import datetime
import math

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

def getOutputFileName(inputFileName):
    outputFileName = inputFileName + ".md5"
    if ("hashFileNameOutputPostfix" in cmdLineArgs):
        if (len(cmdLineArgs["hashFileNameOutputPostfix"]) > 1):
            raise Exception("-hashFileNameOutputPostfix can be specified once only")
        outputFileName += "." + cmdLineArgs["hashFileNameOutputPostfix"][0]
    return outputFileName

# Ref: https://www.pythonforbeginners.com/system/python-sys-argv
def parseCommandLine():
    global cmdLineArgs;

    # Ref: https://www.w3schools.com/python/python_dictionaries.asp
    cmdLineArgs = {
        "exec": [sys.argv[0]]
    }
    argName = ""
    # Ref: "python command line arguments in main, skip script name" https://stackoverflow.com/a/19016716/13441
    for curArg in sys.argv[1:]:
        if (argName == ""):
            argName = curArg
            if (argName[0] != "-"):
                # Ref: "Manually raising (throwing) an exception in Python" https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python
                raise Exception("Command line argument should start with dash (-): " + argName)
            # Ref: https://stackoverflow.com/questions/4945548/remove-the-first-character-of-a-string
            argName = argName[1:]
            if (argName == ""):
                raise Exception("Invalid command line parameter '-'")
        else:
            if (argName in cmdLineArgs):
                cmdLineArgs[argName].append(curArg)
            else:
                cmdLineArgs[argName] = [curArg]
            argName = ""

    # Debug. Output parsed command line
    for argName, argValue in cmdLineArgs.items():
        argValueStr = ", ".join(argValue)
        print('// ' + argName + ' -> ' + argValueStr)

def getDateTimeStr(dateTime: datetime) -> str:
    return dateTime.strftime("%Y.%m.%d %H:%M:%S")

# Returns false if hash not calculated, probably because it was already calculated.
def handleInputFile(inputFileName):
    startDateTime = datetime.now();
    print("Handle file start time: " + getDateTimeStr(startDateTime) + " (" + inputFileName + ")")
    outputFileName = getOutputFileName(inputFileName)
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
        outputFile.write(hash + " *" + inputFileName)

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
    parseCommandLine()

    if (not "inputFile" in cmdLineArgs):
        print ("Input file(s) is not specified")
        exit(5)
   
    for inputFileName in cmdLineArgs["inputFile"]:
        if (not handleInputFile(inputFileName)):
            exit(10)

except Exception as ex:
    print("Exception thrown:\n", ex)
