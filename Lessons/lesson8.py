import subprocess, shlex

command = "dir week3"
print(command)

proc = subprocess.Popen(shlex.split(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,)

files = []
for line in iter(proc.stdout.readline, b''):
    parts = line.decode('utf-8').strip()
    print(parts)

'''
#print(proc.stdout.readline())


for line in iter(proc.stdout.readline()):
    print(line)

print('\n\n\n')

print(proc.stdout)
print(type(proc.stdout))
print(proc.stdout.readable())
print(proc.stdout.read())
#, shell=True

command = 'ls -l some/folder'

process = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

for line in iter(process.stdout.readline, ''):


'''