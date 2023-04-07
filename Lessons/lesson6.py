import argparse

#used to read from files
def fileReader(filename, verbosity):
    try:
        lines = []
        with open(filename) as f:
            for line in f:
                lines.append(line)
                if (verbosity):
                    print(line)

        #print length of file
        print(len(lines))
    
    except Exception as e:
        print("Unexpected {e}, {type(e)=}")
        raise

#define parser
parser = argparse.ArgumentParser()

#file txt as args.filePath
#verbose option which is a boolean as args.verbose
parser.add_argument('--file', dest='filePath', help='path to a file')
parser.add_argument('--verbose', action='store_true', help='show verbose')

#parse the args
args = parser.parse_args()

try:
    #read from file and then print length of lines
    fileReader(args.filePath, args.verbose)
except Exception as e:
    raise e