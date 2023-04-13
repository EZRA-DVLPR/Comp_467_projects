import argparse, datetime, pymongo
from getpass import getuser
from re import split

#set up db connection and collections - outputs: client, db, and collections 1 & 2
def dbSet():
    myclient = pymongo.MongoClient('mongodb+srv://admin:password1234@cluster0.4prujhr.mongodb.net/?retryWrites=true&w=majority')

    mydb = myclient['Project2']

    userData = mydb['userData']

    framesData = mydb['framesData']

    return [myclient, mydb, userData, framesData]

#add data to the db in the given collection
def addDataDB(collection, data):
    if collection.full_name == 'Project2.userData':
    
        #User that ran script - Machine - Name of User on File - Date of File - Date Submitted
        tDict = {
            'User that ran Script': data[0],
            'Machine': data[1],
            'Name of User on File': data[2],
            'Date on File': data[3],
            'Date Submitted': data[4]
        }
        
        collection.insert_one(tDict)
    else:

        #Name of user on file - Date of file - location - frame/ranges  
        tDict = {
            'Name of User on File': data[0],
            'Date on File': data[1],
            'Location': data[2],
            'Frame/Ranges': data[3]
        }

        collection.insert_one(tDict)

#check that the dates match in all the given strings (filenames)
def dateChecker(*filenames):
    
    #first find the date within the Xytech file to compare to the rest of the files
    date = filenames[0][len(filenames[0]) - 1][filenames[0][len(filenames[0]) - 1].rfind('_') + 1:len(filenames[0][len(filenames[0]) - 1]) - 4]

    #once date is found check and see if the date is the same across all the files relative to the Xytech file
    for file in filenames[0]:
        if date not in file:
            return False

    return True

#lists all occurrences of the given character within a string
def find(str, ch):
    return [i for i, ltr in enumerate(str) if ltr == ch]

#extracts all the frames from a given string and appends the values to a list. Any sequences of frames are changed to this sequence
def extractFrames(str):
    allFrames = []

    if (str.find(' ') == -1):
        #only one item so we append it to the allFrames
        allFrames.append(str[:len(str) - 1])

    else:
        #more than one item so we have to check for sequences
        start = 1
        end = -1

        #split into separate strings when it encounters whitespace
        #then sorts by characters followed by the length of items inside
        splitFrames = split('\s', str)
        splitFrames.sort(key = lambda item: (len(item), item))

        #find the sequential frames and append the sequence to allFrames
        #any non-numerical values will be appended as is
        #note: that if there are non-numerical values, they will always be the last values of splitFrames
        for i in range(2,len(splitFrames)):
            #print(splitFrames[i])
            try:
                #check if i is the next number sequentially
                if int(splitFrames[i]) - 1 == int(splitFrames[i - 1]):
                    end = i
                    continue
                elif end != -1:
                    #there was a sequence but this sequence has stopped at the current i
                    allFrames.append(splitFrames[start] + '-' + splitFrames[end])
                    start = i
                    end = -1
                    continue
                else:
                    #no sequence and not pre-existing sequence so append it as a singleton frame
                    allFrames.append(splitFrames[i - 1])
                    start = i
                    end = -1

            except Exception as e:
                #encountered a non-numerical value
                #if there is a sequence then stop the sequence and append the sequence to the list
                if end != -1:
                    allFrames.append(splitFrames[start] + '-' + splitFrames[end])
                else:
                    #singleton before the non-numerical value so we just add it as is
                    allFrames.append(splitFrames[i - 1])
                
                allFrames.append(splitFrames[i])
                start = i
                end = -1
                continue
                
        #account for stragglers at end of list
        try:
            int(splitFrames[len(splitFrames) - 1])
            if end != -1:
                allFrames.append(splitFrames[start] + '-' + splitFrames[end])
            else:
                allFrames.append(splitFrames[len(splitFrames) - 1])
        except:
            pass

    return allFrames

#the additional assignment for the project submission
def dbCalls(dbStuff):
    a1, a2, a3, a4 = [], [], [], []

    for x in dbStuff[3].find({}):
        # 1 - All work done by TDanza
        if x['Name of User on File'] == 'TDanza':
            a1.append(x['Frame/Ranges'])

    names = []
    # 2 - all work done before 3-25-23 on Flame
    #find the users of flame in userData then find all work done before 3-25-23 with user's name in framesData
    for x in dbStuff[2].find({}):
        if x['Machine'] == 'Flame':
            names.append(x['Name of User on File'])
    for y in dbStuff[3].find({}):
        if y['Date on File'] < '20230325' and y['Name of User on File'] in names:
            a2.append(y['Frame/Ranges'])
            
    for x in dbStuff[3].find({}):
        # 3 - work done on hpsans13 on 3-26-23
        if 'hpsans13' in x['Location'] and x['Date on File'] == '20230326':
            a3.append(x['Frame/Ranges'])

    for x in dbStuff[2].find({}):
        # 4 - name of all autodesk flame users
        if x['Machine'] == 'Flame' and x['Name of User on File'] not in a4:
            a4.append(x['Name of User on File'])

    print(a1)
    print(a2)
    print(a3)
    print(a4)
    return

parser = argparse.ArgumentParser()

#arguments:
#   files - all the baselight/flames files to be read
#   xytech - the xytech file to be read
#   verbose
#   output - choose CSV or DB to output info
parser.add_argument('--files', action='append', help='path to Baselight or Flames txt files for processing', nargs='+', required=True, type=argparse.FileType('r'))
parser.add_argument('--xytech', dest='xytechPath', help='path to Xytech txt file for processing', required=True, type=argparse.FileType('r'))
parser.add_argument('--verbose', action='store_true', help='show verbose')
parser.add_argument('--output', choices=['CSV', 'DB'], dest='output', help='choose output to CSV or DB', required=True)

args = parser.parse_args()

#wrap in try-catch and raise exceptions when things go awry
dbStuff = []
try:
    
    #files is the list of Baselight and Flame files to read data from
    files = []
    if args.verbose:
        print('Reading files:')
    for file in args.files[0]:
        if args.verbose:
            print(file.name, end=' ')
        files.append(file.name)
    if args.verbose:       
        print(args.xytechPath.name, '\n')

    #read the folders from the given xytech file
    xytFolders = []
    csvData = []
    if 'Xytech' not in args.xytechPath.name:
        raise NameError ('WRONG FILE GIVEN AS XYTECH FILE - PLEASE ENTER A XYTECH FILE FOR THE XYTECH ARGUMENT', args.xytechPath.name)
    else:
        with open(args.xytechPath.name) as f:
            isNote = False
            for line in f:
                
                #grab the workorder, name, operator, job, and notes
                if args.output == 'CSV' and (('Workorder' in line) or ('Producer:' in line) or ('Operator:' in line) or ('Job:' in line)):
                    csvData.append(line)
                elif args.output == 'CSV' and 'Notes:' in line:
                    csvData.append(line)
                    isNote = True
                elif args.output == 'CSV' and isNote:
                    csvData.append(line)

                if '/' in line:
                    xytFolders.append(line[:len(line) - 1])
        
    if args.verbose and len(xytFolders) < 1:
        print('WARNING - NO DIRECTORIES FOUND IN XYTECH FILES')

    #check to see if baselight and flame files are given
    for file in files:    
        if ('Baselight' not in file) and ('Flame' not in file):
            raise NameError ('WRONG FILE GIVEN AS BASELIGHT/FLAME FILE(S) - PLEASE ENTER A PROPER FILE FOR DATA INPUT', file)
    
    #check the dates of the given files to see if they all match
    files.append(args.xytechPath.name[args.xytechPath.name.rfind('/') + 1:])
    if dateChecker(files):
        files.pop()
    else:
        raise NameError ('DIFFERENT DATES FOR FILES GIVEN - ENSURE THAT THE GIVEN FILES HAVE THE SAME DATES', files)
    
    #read the frames from the given baselight/flame files
    csvFrames = []

    if args.output == 'DB' and args.verbose:
        print('Setting up DataBase...')
    dbStuff = dbSet()
    if args.output == 'DB' and args.verbose:
            print('Database Setup Complete.\nAdding to Database...')
    
    if args.verbose and args.output == 'CSV':
        print('Adding to CSV...')

    for file in files:
        filename = file[file.rfind('/') + 1:]
        
        #parse through the filename to extract the <Machine> <User on File> <Date submitted> - Note that <Machine isn't needed in CSV so it isn't extracted unless DB is the output
        user = filename[filename.find('_') + 1 : filename.rfind('_')]
        date = filename[filename.rfind('_') + 1 : len(filename) - 4]

        #append the data to DB if needed
        if args.output == 'DB':
            mach = filename[:filename.find('_')]
            addDataDB(dbStuff[2], [getuser(), mach, user, date, datetime.datetime.now().strftime("%Y%m%d")])

        #open file for reading the location and frames
        with open(file) as f:
            for line in f:
                
                loc = ''
                frames = ''
                framesList = []

                if 'Baselight' in file:
                    #find all slashes within location given
                    locSlash = find(line[:line.find(' ')], '/')
                    loc = line[locSlash[len(locSlash) - 4] + 1:line.find(' ')]

                    #grab the frames to be parsed
                    frames = line[line.find(' ') + 1:]

                else:
                    #Flame file - find all the spaces within the location given
                    locSpace = find(line, ' ')
                    loc = line[locSpace[0] + 1:locSpace[1]]

                    #grab the frames to be parsed
                    frames = line[locSpace[1] + 1:]
                
                allFrames = extractFrames(frames)

                if loc == '':
                    raise ValueError ('ERROR WITH FINDING LOCATIONS WITHIN FILE -', f)
                elif allFrames == []:
                    raise ValueError ('ERROR WITH FINDING FRAMES WITHIN FILE -', f)
                
                #for each element within the frame, append the data to DB
                for i in range(len(allFrames)):
                    for j in range(len(xytFolders)):
                        if loc in xytFolders[j]:
                            if args.output == 'DB':
                                addDataDB(dbStuff[3], [user, date, loc, allFrames[i]])
                            else:
                                csvFrames.append([loc, allFrames[i]])

    if args.output == 'CSV':
        
        #write to the output file
        with open('output.txt', 'w') as outputFile:
            for d in csvData:
                outputFile.write(d.rstrip('\n') + ' / ')

            outputFile.write('\n' * 3)

            for d in csvFrames:
                for i in range(len(xytFolders)):
                    if d[0] in xytFolders[i]:
                        outputFile.write(xytFolders[i] + ' / ' + d[1] + '\n')

        if args.verbose:
            print('Finished writing to CSV -- See \'output.txt\'')

    elif args.verbose and args.output == 'DB':
        print('Finished Adding data to DB')
        
except Exception as e:
    raise e

dbCalls(dbSet())