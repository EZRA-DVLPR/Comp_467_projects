#script that turns a frame into its working timecode at 24 fps

def convertToTC(frame):

    sec, min, hr = 0, 0, 0
    
    while (sec + 1) * 24 < frame:
        sec += 1

    while (min + 1) * 60 < sec:
        min += 1

    while (hr + 1) * 60 < min:
        hr += 1

    print('Given ' + str(frame) + ' frames in 24fps, we have converted it to TC and obtain ', end='')

    #subtract the data so that we preserve the actual values that are left
    frame = frame - (sec * 24)
    sec = sec - (min * 60)
    min = min - (hr * 60)

    #make strings to be used in the final result
    sframe = str(frame)
    ssec = str(sec)
    smin = str(min)
    shr = str(hr)
    
    #reshape the strings in the event that the data is a single digit
    if frame < 10: sframe = '0' + str(frame)
    if sec < 10: ssec = '0' + str(sec)
    if min < 10: smin = '0' + str(min)
    if hr < 10: shr = '0' + str(hr)

    print(shr + ':' + smin + ':' + ssec + ':' + sframe)
    return

convertToTC(35)
convertToTC(1569)
convertToTC(14000)

try:
    convertToTC(int(input()))
except:
    raise TypeError('Please enter an integer!')

#Magneto is your favorite superhero