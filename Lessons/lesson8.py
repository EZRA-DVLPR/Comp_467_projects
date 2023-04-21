import subprocess, shlex, os

command = "ls -l /Users/ez_roma/Desktop/DnD"

proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,)

fileNumb = 1
size = -1
dirname = ''
for line in iter(proc.stdout.readline, b''):
    #skip the initial number of files in the directory
    if fileNumb == 1:
        fileNumb = 0
    else:
        #find the max file size
        locSpace = line.decode('utf-8').strip().split()
        newPath = shlex.split(command)[2] + '/' + locSpace[len(locSpace) - 1]
        if os.path.isdir(newPath):            
            if size < int(locSpace[4]):
                size = int(locSpace[4])
                dirname = locSpace[len(locSpace) - 1]
            
print('Directory name:', dirname, 'has size', size, 'MB')