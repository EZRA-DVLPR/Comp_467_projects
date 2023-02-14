#import array for arrays and secrets for true randomness
import array as arr
import secrets

#instantiate 'a' as our array
a = arr.array('i', [])

#loop 20 times generating random integers of size < 2^31
#and then inserts them into 'a'
for i in range(20):
    a.insert(len(a), secrets.randbelow(2**31))

#find max elt in 'a'
max_elt = -1

for i in range(len(a)):
    if a[i] > max_elt:
        max_elt = a[i]

#catch error if 'a' holds incorrect data
try:
    if max_elt == -1:
        raise
except:
    print("Problem generating 'a'")

#print statements
print(a)
print('Max element is: ' + str(max_elt))
print("The type of 'a' is: " + str(type(a)))