import sched, time, os, datetime

#define s as our scheduler
s = sched.scheduler(time.time, time.sleep)

#function that does the heavy lifting of checking file contents and seeing if a new file has been added
def foo(sc, list, eve):
    print('SCANNING')
    
    #enters event to the scheduler with given contents
    eve = sc.enter(1, 1, foo, (sc, list, eve))
    
    #grabs current contents of folder
    filestuff = os.listdir(os.path.abspath(os.getcwd() + '/week3'))

    #start looking for a new file added
    for f in filestuff:
        #if a new file is found
        if f not in list:

            #print info about file
            print('\n\nNEW FILE WAS FOUND: ' + f)
            if os.path.isfile(os.path.abspath(os.getcwd() + '/week3/' + f)):
                print(f,'is a file')
            elif os.path.isdir(os.path.abspath(os.getcwd() + '/week3/' + f)):
                print(f, 'is a directory')

            if os.path.splitext(os.path.abspath(os.getcwd() + '/week3/' + f))[1] != '':
                print('The extension of', f, 'is', os.path.splitext(os.path.abspath(os.getcwd() + '/week3/' + f))[1])

            print('Current time is:',datetime.datetime.now())

            #delete from queue
            sc.cancel(eve)
    
    #no new file so we update the queue
    if len(sc.queue) != 0:
        list = filestuff
        sc.cancel(eve)
        sc.enter(1, 1, foo, (sc, list, eve))

#run the program
foo(s, os.listdir(os.path.abspath(os.getcwd() + '/week3')), '')
s.run()