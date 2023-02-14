#lines will contain the files contents
#newlines will contain the updated files contents
lines = []
newlines = []

#error check with reading of file
try:
    with open('ingest_this.txt', 'r') as file:
        for line in file:
            #nline will be what we add to lines and newlines
            nline = line.strip()
            
            #append the stripped line to lines
            lines.append(nline)

            #change vowels to '9' and append to newlines
            nline = nline.replace('a', '9').replace('A','9')
            nline = nline.replace('e', '9').replace('E','9')
            nline = nline.replace('i', '9').replace('I','9')
            nline = nline.replace('o', '9').replace('O','9')
            nline = nline.replace('u', '9').replace('U','9')
            newlines.append(nline)

        #print output
        print(lines)
        print()
        print(newlines)

except:
    print('Error reading TXT file')