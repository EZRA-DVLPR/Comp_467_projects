import argparse, datetime, pymongo, openpyxl, ffmpeg
from getpass import getuser
from re import split
from requests import post
from frameioclient import FrameioClient

#extract the list of folders and xytech data from the xytech file
def extractXytech(xyPath, output, verbose):
    if verbose:
        print(xyPath, '\n')

    #read the folders from the given xytech file
    #read the data from the xytech file like workorder, etc. that is not a folder
    xytFolders = []
    xytechData = []
    if 'Xytech' not in xyPath:
        raise NameError ('WRONG FILE GIVEN AS XYTECH FILE - PLEASE ENTER A XYTECH FILE FOR THE XYTECH ARGUMENT', xyPath)
    else:
        with open(xyPath) as f:
            isNote = False
            for line in f:
                
                #grab the workorder, name, operator, job, and notes
                if ((output == 'CSV') or (output == 'XLS')) and (('Workorder' in line) or ('Producer:' in line) or ('Operator:' in line) or ('Job:' in line)):
                    xytechData.append(line)
                elif ((output == 'CSV') or (output == 'XLS')) and 'Notes:' in line:
                    xytechData.append(line)
                    isNote = True
                elif ((output == 'CSV') or (output == 'XLS')) and isNote:
                    xytechData.append(line)

                if '/' in line:
                    xytFolders.append(line[:len(line) - 1])

    if verbose and len(xytFolders) < 1:
        print('WARNING - NO DIRECTORIES FOUND IN XYTECH FILES')
        
    return xytFolders, xytechData

#check that the dates match in all the given strings (filenames)
def dateMatches(*filenames):
    
    #first find the date within the Xytech file to compare to the rest of the files
    date = filenames[0][len(filenames[0]) - 1][filenames[0][len(filenames[0]) - 1].rfind('_') + 1:len(filenames[0][len(filenames[0]) - 1]) - 4]

    #once date is found check and see if the date is the same across all the files relative to the Xytech file
    for file in filenames[0]:
        if date not in file:
            return False

    return True

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

#search db for frame range that is less than the given length in seconds
def findRanges(length, dbComponents):

    dbData = []

    for x in dbComponents[3].find({}):
        if ('-' in x['Frame/Ranges']) and(int(x['Frame/Ranges'][:x['Frame/Ranges'].find('-')]) < length) and (int(x['Frame/Ranges'][x['Frame/Ranges'].find('-') + 1 :]) < length):
            dbData.append([x['Location'], x['Frame/Ranges']])

    return dbData

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

#open file and extract the location as well as list of frames
def readFileData(file):
    with open(file) as f:
        allFrames = []
        for line in f:
            
            loc = ''
            frames = ''

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
            
            allFrames += extractFrames(frames)

            if loc == '':
                raise ValueError ('ERROR WITH FINDING LOCATIONS WITHIN FILE -', f)
            elif allFrames == []:
                raise ValueError ('ERROR WITH FINDING FRAMES WITHIN FILE -', f)
            
    return loc, allFrames

#output CSV as 'output.txt'
def outputToCSV(xytechData, fileData):
    with open('output.txt', 'w') as outputFile:
        for d in xytechData:
            outputFile.write(d.rstrip('\n') + ' / ')

        outputFile.write('\n' * 3)

        for d in fileData:
            outputFile.write(d[0]+ ' / ' + d[1] + '\n')

#establish excel sheet as [DATE]_[LOCAL MACHINE USER].xlsx
def setXLS(date, verbose):
    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]
    ws.title = date
    filenameXL = date + '_' + str(getuser()) + '.xlsx'
    wb.save(filename= filenameXL)

    if verbose:
        print('Excel sheet created --', filenameXL)

    return filenameXL

#extract image from video given TC
def createThumbnail(framesToAdd, video, videoData):

    thumbnailList = []

    #toAdd is in frames, so we convert it to seconds then extract the frame, and then append the name to thumbnail List
    for range in framesToAdd:
            
        toAdd = int(range[1][range[1].find('-')+1:]) // int(range[1][:range[1].find('-')])
        toAdd = toAdd + int(range[1][range[1].find('-')+1:])
        toAdd = toAdd / int(videoData['r_frame_rate'][:videoData['r_frame_rate'].find('/')])

        filename = 'frame_' + str(toAdd) + '.jpg'
        ffmpeg.input(video.name, ss=toAdd).filter('scale', width=96, height=76).output(filename, vframes=1, loglevel='quiet').overwrite_output().run()
        thumbnailList.append(filename)

    return thumbnailList

#add the data to excel sheet and save as 'output.xlsx'
def addXLS(filenameXL, xytechData, fileData, video, verbose):

    probe = ffmpeg.probe(video.name)
    videoData = probe['streams'][0]

    wb = openpyxl.load_workbook(filenameXL)
    ws = wb[filenameXL[:filenameXL.find('_')]]
    if verbose:
        print('Adding data to XLS...')

    for i in range(len(xytechData)):
        ws.cell(row = 1, column = i + 1, value = xytechData[i])
    
    for i in range(len(fileData)):
        ws.cell(row = i + 4, column = 1, value = fileData[i][0] + ' / ' + fileData[i][1])

    framesToAdd = findRanges(float(videoData['duration']) * int(videoData['r_frame_rate'][:videoData['r_frame_rate'].find('/')]), dbSet())

    for i in range(len(framesToAdd)):
        ws.cell(row = i + 4, column = 2, value = framesToAdd[i][0] + ' / ' + framesToAdd[i][1])

    if verbose:
        print('Making Thumbnails...')
    thumbnailList = createThumbnail(framesToAdd, video, videoData)
    if verbose:
        print('Thumbnails Created.\nAdding thumbnails to the XLS and Frame.io...')
    ws.column_dimensions['A'].width = 60
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 14
    # row 4 col 3: append the images to the cells
    for i in range(len(thumbnailList)):            
        frameIOUpload(thumbnailList[i])
        ws.row_dimensions[i + 4].height = 60
        img = openpyxl.drawing.image.Image(thumbnailList[i])
        img.anchor = 'C' + str(i + 4)
        ws.add_image(img)

    # once all images are added, save the worksheet
    wb.save(filenameXL)

    if verbose:
        print('Finished adding to Frame.io')
        print('Successfully saved to XLS')

#uploads the given file to frame.io
def frameIOUpload(thumbnail):
    #needed for the API
    headers = {'Authorization' : 'Bearer fio-u-H7CelP5LH4qQUUn564zulCwhmvcOZZmo0ArwsFww6nAwDvRSZrDPDETZKWs9Tc0y'}
    url = 'https://api.frame.io/v2/assets/394bcbed-5132-4ae2-befe-5f1d8b64ad60/children?type=file'
    asset_id = '394bcbed-5132-4ae2-befe-5f1d8b64ad60'
    token = 'fio-u-H7CelP5LH4qQUUn564zulCwhmvcOZZmo0ArwsFww6nAwDvRSZrDPDETZKWs9Tc0y'

    #create a client to access via token
    client = FrameioClient(token)

    #open the given thumbnail and upload with a subsequent closure of the thumbnail
    file = open(thumbnail, 'rb')
    client.assets.upload(asset_id, thumbnail)
    response = post(url, headers=headers)
    file.close()

#print all files in root folder of 'Project 3' from frame.io
def printThumbnails():
    #needed for the API
    asset_id = '394bcbed-5132-4ae2-befe-5f1d8b64ad60'
    token = 'fio-u-H7CelP5LH4qQUUn564zulCwhmvcOZZmo0ArwsFww6nAwDvRSZrDPDETZKWs9Tc0y'

    #create a client to access via token
    client = FrameioClient(token)

    #retrive list of files within root folder
    response_list = client.assets.get_children(asset_id)
    for item in response_list:
        print(item['name'])

#main program
def main():
    parser = argparse.ArgumentParser()

    #arguments:
    #   files - all the baselight/flames files to be read
    #   xytech - the xytech file to be read
    #   process - video file to be processed
    #   output - choose CSV or DB or XLS to output info
    #   verbose

    parser.add_argument('--files', action='append', help='path to Baselight or Flames txt files for processing', nargs='+', required=True, type=argparse.FileType('r'))
    parser.add_argument('--xytech', dest='xytechPath', help='path to Xytech txt file for processing', required=True, type=argparse.FileType('r'))
    parser.add_argument('--process', dest='video', help='path to video file for processing', type=argparse.FileType('r'))
    parser.add_argument('--output', choices=['CSV', 'DB', 'XLS'], dest='output', help='choose output to: \'CSV\' or \'DB\' or \'XLS\'', required=True)
    parser.add_argument('--verbose', action='store_true', help='show verbose')

    args = parser.parse_args()

    #files is the list of Baselight and Flame files to read data from
    #see if filenames are valid and raise if they're not Baselight or Flame files
    files = []
    if args.verbose:
        print('Reading files:')
    for file in args.files[0]:
        if args.verbose:
            print(file.name, end=' ')
        
        if ('Baselight' not in file.name) and ('Flame' not in file.name):
            raise NameError ('WRONG FILE GIVEN AS BASELIGHT/FLAME FILE(S) - PLEASE ENTER A PROPER FILE FOR DATA INPUT', file)
        else:
            files.append(file.name)
    
    #extract the information from the xytech file given
    xytFolders, xytechData = extractXytech(args.xytechPath.name, args.output, args.verbose)

    #check the dates of the given files to see if they all match
    files.append(args.xytechPath.name[args.xytechPath.name.rfind('/') + 1:])
    if dateMatches(files):
        files.pop()
    else:
        raise NameError ('DIFFERENT DATES FOR FILES GIVEN - ENSURE THAT THE GIVEN FILES HAVE THE SAME DATES', files)

    #handle db connectivity/setup
    if args.output == 'DB':
        dbComponents = dbSet()

        if args.verbose:
            print('Setting up DataBase...')

    if args.verbose:
        if args.output == 'CSV':
            print('Adding to CSV...')
        elif args.output == 'XLS':
            print('Adding to XLS...')
        elif args.output == 'DB':
            print('Database Setup Complete.\nAdding to Database...')

    #read the frames from the given baselight/flame files
    fileData = []

    for file in files:
        
        #parse through the filename to extract the <Machine> <User on File> <Date submitted> - Note that <Machine> is only extracted if DB is the output
        filename = file[file.rfind('/') + 1:]
        user = filename[filename.find('_') + 1 : filename.rfind('_')]
        date = filename[filename.rfind('_') + 1 : len(filename) - 4]

        #append the data to DB
        if args.output == 'DB':
            mach = filename[:filename.find('_')]
            addDataDB(dbComponents[2], [getuser(), mach, user, date, datetime.datetime.now().strftime("%Y%m%d")])

        #extract location and list of allFrames from given Baselight/Flame file
        loc, allFrames = readFileData(file)
                
        #for each element within the frame, append the data to DB
        for i in range(len(allFrames)):
            for j in range(len(xytFolders)):
                if loc in xytFolders[j]:
                    if args.output == 'DB':
                        addDataDB(dbComponents[3], [user, date, loc, allFrames[i]])
                    else:
                        fileData.append([xytFolders[j], allFrames[i]])

    if args.output == 'CSV':

        outputToCSV(xytechData, fileData)

        if args.verbose:
            print('Finished writing to CSV -- See \'output.txt\'')
    
    elif args.output == 'XLS':

        if args.video == None:
            raise ValueError('No video file specified')
        else:
            XLFilename = setXLS(date, args.verbose)
            addXLS(XLFilename, xytechData, fileData, args.video, args.verbose)

        if args.verbose:
            print('List of all Thumbnails in \'Project 3\' Root folder on Frame.io:')
            printThumbnails()

    elif args.output == 'DB':
        if args.verbose:
            print('Finished Adding data to DB')

#runner of the program
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise e