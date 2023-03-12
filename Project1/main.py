import argparse, sys, re

#used to read from files
def fileReader(filename, verbosity):
    try:
        lines = []
        with open(filename) as f:
            if verbosity:
                print('Reading from: ', filename)
            for line in f:
                lines.append(line.strip())
            if verbosity:
                print('Done reading file: ', filename, '\n')
        return lines
    
    except Exception as e:
        print("Unexpected {e}, {type(e)=}")
        raise

#eliminates traceback so that only exceptions explicity stated are returned
sys.tracebacklimit = 0

#defines parser to parse arguments
parser = argparse.ArgumentParser()

#job = string, verbose = bool, TC = string
parser.add_argument("--job", dest="jobFolder", help="job to process")
parser.add_argument("--verbose", action="store_true", help="show verbose")
parser.add_argument("--TC", dest="timecode", help="Timecode to process")

#parse args and hold them as vars
args = parser.parse_args()

if args.verbose:
    print()

#Read job and TC
if args.jobFolder is None:
    print('No job selected')
    sys.exit(2)
else:
    jobs = args.jobFolder
    try:
        Xycont = fileReader(jobs, args.verbose)
    except Exception as e:
        print('INVALID JOBS PATH')
        sys.exit(1)

if args.timecode is None:
    print('No timecode selected')
    sys.exit(2)
else:
    timecodeTC = args.timecode
    try:
        BLcont = fileReader(timecodeTC, args.verbose)
    except:
        print('INVALID TC PATH')
        sys.exit(1)

#define vars to hold info like producer, operator, job, and notes
worder = ''
producer = ''
operator = ''
job = ''
locs = []
notes = []

#define lines from TC to grab frames to be checked
lines = []

#frames that need to be checked. this will be returned later in the output
frames = []

#grab vars from job
for i in range(len(Xycont)):

    if 'Workorder' in Xycont[i] and worder == '':
        worder = Xycont[i][Xycont[0].find('Workorder') + 10:]
    
    if 'Producer' in Xycont[i] and producer == '':
        producer = Xycont[i][Xycont[0].find('Producer') + 11:]

    if 'Operator' in Xycont[i] and operator == '':
        operator = Xycont[i][Xycont[0].find('Operator') + 11:]

    if 'Job' in Xycont[i] and job == '':
        job = Xycont[i][Xycont[0].find('Job') + 6:]

    if 'Location' in Xycont[i] and locs == []:
        for j in range (i, len(Xycont)):
            if Xycont[j] == '':
                locs = Xycont[i:j]
                break
    
    if 'Notes' in Xycont[i] and notes == []:
        notes = Xycont[i:len(Xycont)]

#grab lines
for i in range(len(BLcont)):
    if BLcont[i] != '':
        lines.append(BLcont[i])

if worder == '' or producer == '' or operator == '' or job == '' or locs == []:
    print('ERROR PARSING FILES GIVEN. CHECK job')
    sys.exit(1)
elif lines == []:
    print('ERROR PARSING FILES GIVEN. CHECK TC')
    sys.exit(1)
else:
    for j in range(len(lines)):

        #longest = [i, length of longest substring]
        longest = [-1, 0]

        for i in range(len(locs)):

            #find largest substring of locs[i] that is in line
            cstart = 0
            while (locs[i][cstart:] not in lines[j]) or (cstart == len(locs[i])):
                cstart += 1

            if longest[1] < len(locs[i][cstart:]):
                longest = [i, len(locs[i][cstart:]), cstart]

        if longest[0] == -1:
            print('ERROR - NO MATCH - CHECK JOBS AND TC FOR MATCHING FILE LOCATIONS')
            sys.exit(1)
        elif longest[1] < 14:   # why 14? -> /abc/abc/a/abc may be the shortest possible combo for any useful information provided to file
                                #eg. /fun/1st/1/car holds useful info but anything less may not
            if args.verbose:
                print('WARNING - LENGTH IS LOW FOR MATCH - CHECK JOB LINE ', longest[0], ' AND VERIFY MANUALLY TC FOR LINE ', j)

        else:
            #we have a match so grab the frames data
            toparse = lines[j][lines[j].find(locs[longest[0]][longest[2]:]) + longest[1] + 1:]

            #parse all frames and put in sequential order
            plist = re.split('\s', toparse)

            #sort by characters then by length of items inside
            plist.sort(key = lambda item: (len(item), item))

            #find all non-numerical frames
            nonNum = []
            num = []
            for i in range(len(plist)):
                try:
                    num.append(int(plist[i]))
                except:
                    if args.verbose:
                        print("WARNING - NON-INTEGER VALUE DETECTED - " + plist[i] + " IN LINE " + str(j + 1) + " OF TC")
                    nonNum.append(i)

            #check sequential entries and then combine into 1 argument
            start = -1
            stop = -1
            s = ''
            i = 0

            if len(num) > 1:      

                #iterate to get all nums in num         
                while i < len(num):
                    start = i
                    for k in range(i + 1, len(num)):
                        if num[k] == num[k - 1] + 1:
                            stop = k
                        elif stop != -1:
                            #there was an increment
                            i = stop
                            s = str(num[start]) + '-' + str(num[stop])
                            stop = -1
                            frames.append(locs[longest[0]] + ' / ' + s)
                            break
                        else:
                            frames.append(locs[longest[0]] + ' / ' + str(num[i]))
                            break

                        if (k == len(num) - 1) and (stop != -1):
                            #there was an increment
                            i = stop
                            s = str(num[start]) + '-' + str(num[stop])
                            frames.append(locs[longest[0]] + ' / ' + s)
                            stop = -1

                    i += 1

                #catch any stray frames that dont have a subsequent frame and are not in sequence
                s = str(num[i-1])
                if s not in frames[len(frames) - 1] and start == i - 1:
                    frames.append(locs[longest[0]] + ' / ' + s)
            
            else:
                #only one number in this set so we will add the single number
                frames.append(locs[longest[0]] + ' / ' + str(num[0]))

#frames now holds all the frames in sequence. print to file
with open('output.txt', 'w') as f:
    f.write('Workorder ' + worder + '/' + producer + '/' + operator + '/' + job + '/')

    for i in range(len(notes)):
        if i == 0:
            f.write(notes[i] + ' ')
        else:
            f.write(notes[i] + '/')

    f.write('\n\n\n')

    for fr in frames:
        f.write(fr + '\n')