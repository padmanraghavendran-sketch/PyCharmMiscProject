
#round = round off function, eg u can do round(x) or round(x,1) the later signifies round to how many decimal pts
#absolute = modulus
#max = max value from a list
#min = min value from a list
#math.sqrt = square root of a number
#ceil = round off to higher values
#floor = round off to lower values
#power = math.pow(radius,x)

#if and else loop learnt
#"==" operator used for comparing two values

#logical operators
#or = atleast one condition must be True
#and = both conditions must be True
#not = inverts the condition

#conditional expression
#num = 5
#print("Positive" if num > 0 else "Negative")

#String functions
#len = length of string
#name.find("") first occurence of any character
# name.rfind("") last occurance of any character
#returns negative 1 if character not found
#name.capitalize(), only first letter is capitalized
#name.upper(), converts everything to uppercase
#name.lower(), converts everything to lowercase
#name.isdigit(), returns true or false if only digit present
#name.isalpha(), returns true or false if a string contains only alphabetical characters(space ain't included)
#name.count(), counts occurences of a character or digit
#name.replace("old","new"), replaces


#string indexing
#str[start:end:step], -1 = last character

#format specifiers
#.(number)f = round to that many decimal places
#:(number) = allocate that many spaces
# :03 = allocate and zero pad that many spaces
# :<, :>, :^ left justify right justify centre align
# :+ = use a plan sign to indicate positive value
# := = place sign to leftmost position
# : = insert a space before psoitive numbers
# :, = comma separator
#eg:f"hello from the other side {price:insert format specifier}"


#while loop = execute some code while some condition remains true
# for loops = execute a block of code a fixed number of times.
#2nd number is exclusive in range function
#reversed range-opposite order

#continue - to skip over an iteration
#break - terminates the loop once iteration found

#time module
#sleeps for a given amount of time then u can print for eg
#import time, time.sleep(3), print

#nested loop, loop inside loop
#print() used to print new line


#Collection = single "variable" used to store multiple values
# list = []
# set = {} unordered and immutable
# tuple = () ordered and unchangeable

#list functions
#print(help(type of element) gives all the functions
#len- number of elements in the list
# "x" in y- return boolean value
# mutable data type
# list.append(item)- add item at the end of list
# list.remove(item)
# list.insert(index, item)- add item at any position
# list.sort()- list sorted in ascending order
# list.reverse() - lost sorted in descending order
# list.clear() - all elements are gone empty list
# list.index(item)- returns index of item- error if item not found
# list.count(item)- counts number of occurences of the item

#set = {} unordered and immutable, but add/remove ok. No duplicates
# fruits.add(item)
# fruits.remove(item)
# fruits.pop() - random incase of set
# fruits.clear()

#tuple = () ordered and unchangeable, tuples are faster than list
# tuple.index(item)
# tuple.count(item)
# iterable object

# 2d list- Nested list

# dictionary = a collection of {key:value} pairs ordered and changeable No duplicates
# dict.get("KEY") - returns the corresponding value pair, if not found returns none
# dict.update("key value pair"), also can update existing value of a key value pair
# dict.pop("KEY") removes key value pair
# dict.popitem() removes last key value pair
# dict.keys() returns list of keys
# dict.values() returns list of values
# dict.items() tuple of list
# dict["key"] returns value

#random-module
#random.randint - inclusive of start and send
#random.random() - random floating point number between 0 and 1
#random.choice(list or tuple) returns choice
#random.shuffle(list or tuple) for eg cards are shuffle

#function = A block of reusable code
#           place() after the function name to invoke it

#return - returns the value if no value - none

#default arguments - if no argument provided python uses the default argument
# non default argument should follow default argement


#keyword arguments = an argument preceded by an identifier
#helps with readability order of arguments doesn't matter
#hello("Hello",title = "MR",first = "SPONEGEBOB",last = "SQUAREPANTS")


# *args = allows you to pass multiple non-key arguments(stored in form of tuple)
# *kwargs = allows you to pass keyword arguments(stored in form of dictionary)

# Iterables = An object/collection that can return its elements one at a time, allowing it to be iterated over in a loop


# Membership operators = used to test whether a value or iteravle is found in a squence
# 1. in, 2. not in

#List comprehension = A concise way to create lists in python
# list = [expression for value in iterable]

## Match-case statement, An aternative to using many elif statements
# def day_of_week(day):
#     match day:
#         case 1:
#             return "SUNDAY"
#         case 2:
#             return "MONDAY"
#         case 3:
#             return "TUESDAY"
#         case 4:
#             return "WEDNESDAY"
#         case 5:
#             return "THURSDAY"
#         case 6:
#             return "FRIDAY"
#         case 7:
#             return "SATURDAY"
# print(day_of_week(1))

# Module = a file containing code you want to include in your program

# variable scope = where a variable is visible and acessiblle
# scope resolution = (LEGB) Local -> Enclosed -> Global -> Built-in
# Local - Variables under a function
# Enclosed - Function inside a Function, if local scope not found then enclosed one is the output
# Global - Variables declared outside the function
# Built-in = eg :from math import e
# def func1():
#     print(e)
# e = 3
# func1()





# if __name__ == __main__ : (this script can be imported or run standalone)
# Functions and classes in this module can be reused without main block existing
# eg: def main():
# IF __name__ == "__main"__:
#main()

#Github
#git add .
#git commit -m "..."
#itgit push