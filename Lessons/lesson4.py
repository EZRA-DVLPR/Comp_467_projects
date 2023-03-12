#first read file
lines = []
badlines = []

#iterate through and store contents of file
try:
    with open('lesson4_folderexample.txt', 'r') as file:
        for line in file:
            #nline will be what we add to lines and newlines
            nline = line.strip()
            lines.append(line)
except:
    print('IMPROPER FILENAME')

#flag any lines that contain the space character
#display line number and incorrect string
#subsequently correct them
#display corrected string
for i in range(len(lines)):
    if ' ' in lines[i]:
        print('LINE', i + 1, 'NEEDS FIXING.')
        print('AS IS:', lines[i])
        print('FIXED VERSION:', lines[i].replace(' ', ''))
        badlines.append(i)
        lines[i] = lines[i].replace(' ', '')

#display that rest of lines are fine except for list of fixed ones
if len(lines) != 0:
    if len(badlines) > 1:
        print('Lines: ', end="")
        for i in range(len(badlines)):
            print(str(i) + ' ', end="")
        print('Needed Fixing')
        print('The other lines are okay')
    else:
        print('No errors with lines!')