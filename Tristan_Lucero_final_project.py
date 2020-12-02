## Tristan Lucero (R#11597605) | Final Project | 12/1/20
##
## This is a program to simulate cellular life 100 times based on some basic rules.
## An input file is given with O's and .'s, and based on it's neighbords the cell shoudl stay alive or die on the next turn.
## The rules:
# 1) Any position in the matrix with a period ‘.’ is considered “dead” during the current time step.
# 2) Any position in the matrix with a capital ‘O’ is considered “alive” during the current time step.
# 3) If an “alive” square has exactly two, three, or four living neighbors, then it continues to be “alive” in the
# next time step.
# 4) If a “dead” square has an even number greater than 0 living neighbors, then it will be “alive” in the next
# time step.
# 5) Every other square dies or remains dead, causing it to be “dead” in the next time step.
# This program takes 3 arges -i for input file, -o for output file which are both required.
# and finally -t for threads, which is optional. If no threads are given, program will be ran serially.

#imports, we need argparse for args, threading for threads, and time to check runtime.
import argparse
import threading
import time
#global file array, will get updated with each life
fileArray = []

#function to check positive value of arg
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

#function to check if read file path is good
def checkReadFile(filePath):
    try:
        f = open(filePath, "r")
        f.close()
        return filePath
    except:
        print("ERROR: Invalid file path")

#function to check if write file path is good
def checkWriteFile(filePath):
    try:
        f = open(filePath, "w")
        f.close()
        return filePath
    except:
        print("ERROR: Invalid file path")


def processBlock(fileText, xs, ys, xstep, ystep, lastRow, outputFile):
    #Loop to loop from lower y to upper y bound of split content array
    for lineNum in range(ys, ystep):
        #targetLst2 is the target row
        targetLst2 = [0] * len(fileText[lineNum])
        #This makes the upper row the one above, or the one below. Except in the case of top in bottom. Where the top of the up most
        #row is actually the bottom, and the bottom of the bottom most row is the top
        up = (lineNum - 1) % (lastRow + 1)
        down = (lineNum + 1) % (lastRow + 1)
        # neighbors array
        n = [0, 0, 0, 0, 0, 0, 0, 0]
        #for each target cell in the row
        for target in range(xstep):
            #gets left neighbor, will be left side except for left most cell where neightbor will be on the right hand side.
            #similar for nRight
            nLeft = (target - 1) % xstep
            nRight = (target + 1) % xstep
            #set all neighbor in neighbor array
            n = [fileText[up][nLeft], fileText[up][target], fileText[up][nRight], fileText[lineNum][nLeft],
                 fileText[lineNum][nRight], fileText[down][nLeft], fileText[down][target], fileText[down][nRight]]
            #checking conditions for if cell should be alive based on conditions
            if fileText[lineNum][target] == 1 and (n.count(1) == 2 or n.count(1) == 3 or n.count(1) == 4):
                targetLst2[target] = 1
            elif fileText[lineNum][target] == 0 and n.count(1) % 2 == 0 and n.count(1) > 0:
                targetLst2[target] = 1
            else:
                targetLst2[target] = 0
        #update that line in fileArray with what it should be next life
        fileArray[lineNum] = targetLst2[:]


def main():
    global fileArray

    inputFile = ""
    outputFile = ""

    #get arguemnts for input file, output file, and threadInput
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=checkReadFile, required=True)
    parser.add_argument('-o', type=checkWriteFile, required=True)
    parser.add_argument('-t', type=check_positive, required=False)
    option = parser.parse_args()
    inputFile = option.i
    outputFile = option.o
    #if no threadInput given, set equal to 1
    threadInput = 1
    #if option.t arg isn't None then set threadInput equal to arg
    if option.t is not None:
        threadInput = option.t

    #open file and save contents as ints
    with open(inputFile, "r") as f:
        content = f.readlines()
    content = [[".O".find(z) for z in x.strip()] for x in content]
    #set file array equal to contents
    fileArray = [row[:] for row in content]
    open(outputFile, "w").close()

    finalStr = ""

    row_len = len(content[0])
    col_len = len(content)
    #upper bound of x is just row len
    xstep = row_len
    #lower bounds of x and y
    xs = 0
    ys = 0
    #split contents
    splitContents = list(chunk(content, threadInput))

    #if thread is not serial
    if threadInput != 1:
        # Do this 100 times, this is the amount of lifes to simulate
        for z in range(100):
            threads = list()
            # ystep is the y lower bound
            ystep = 0
            for i in splitContents:
                # set upper y to last ystep
                ys = ystep
                # ystep equals the length of current i element
                ystep += len(i)
                # call processBlock and create new thread to process the block 1 life and pass info
                myThread = threading.Thread(target=processBlock,
                                            args=(content[:], xs, ys, xstep, ystep, len(content) - 1, outputFile,))
                #star thread
                myThread.start()
                #add thread to threads array
                threads.append(myThread)
            #join all threads together
            for thread in threads:
                thread.join()
            # update the content with the new information from fileArray that we got from processBlock
            content = [row[:] for row in fileArray]
        # save final output to file
        with open(outputFile, "w") as f:
            for item in fileArray:
                f.write("%s\n" % "".join([".O"[x] for x in item]))
    #If threadInput == 1, then run serially
    else:
        #Do this 100 times, this is the amount of lifes to simulate
        for z in range(100):
            #ystep is the y lower bound, for serial it will always be len(splitConents[0]) which is full contents furthest down row
            ystep = 0
            #iterates through splitContents, for serial it just does this once
            for i in splitContents:
                #set upper y to last ystep
                ys = ystep
                #ystep equals the length of current i element
                ystep += len(i)
                #call processBlock to process the block 1 life and pass info
                processBlock(content[:], xs, ys, xstep, ystep, len(content) - 1, outputFile,)
            #update the content with the new information from fileArray that we got from processBlock
            content = [row[:] for row in fileArray]
        #save final output to file
        with open(outputFile, "w") as f:
            for item in fileArray:
                f.write("%s\n" % "".join([".O"[x] for x in item]))

#Function to split up list into semi-equal chunk size parts, returns list of the lists of chunk size parts
def chunk(alist, wanted_parts):
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]


if __name__ == "__main__":
    #Test for printing args
    # print(sys.argv[1:])
    start_time = time.time()
    print("Project :: R11597605")
    main()
    #Print runtime
    print("--- %s seconds ---" % (time.time() - start_time))
