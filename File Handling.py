### text-file
# file_object = open("Filename.txt","mode"), r for read, w for write, a for append
# read- FileNotFound error if file doesn't exist
# append - starts cursor at end of the text file
# write - clears the whole file each time u run it and pointer at beginning
# with open("Filename.txt","mode") as file_object : doesn't require to close the file
# always remember to close to file so memory isn't lost. file_object.close()

# write() method - used to write lines of text
# read() method - Reads entire file into one string
# writelines() method - writes entire list of strings

### Binary - file
# import pickle module for serialization and deserialization
# file_object = open("Filename.dat","mode"), rb for read, wb for write, ab for append, rb+ for read and write, wb+ for write and read
# make sure not to run code of binary file many as file gets easily corrupted

#pickle.dump(object,file) - any python object can be used to write
#pickle.load() - iterable object - always remember to use try and EOFError:
# file.seek(number of bytes,offset) - moves pointer to that position
# 0 for beginning, 1 for current position and 2 for end, can give negative no of bytes
# file.tell() - reveals the position of the pointer


### CSV file (comma separated values)
#import csv module
# file_object = open("Foreg.csv","mode"), r for read, w for write, a for append

#create reader and writer objects
# cw = csv.writer(file_object)
# cr = csv.reader(file_object)
# cr is an iterable object so u can use for loops
# writerow function takes a single row and writes it as a record(list)
# takes nested list as an input and writes multiple lines
# next cr- skips one iteration for eg header row, all items r stored in form of string


# API- Key, code requests data from service, it validates and sends data back