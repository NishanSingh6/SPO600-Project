"""
Autovectorized function building tool

Author: Nishan Singh.
Licensed under the terms of the GPL verion 2.
Developed for the project for SPO600 at Seneca College of Applied Arts and Technology.
Version: 2.0 - Stage 3 of the project (Final implementation)

"""

import os
import sys

#reading the arguements
if len(sys.argv) != 3:
    print("Invalid Arguements")
    sys.exit(1)


arg1 = sys.argv[1]
arg2 = sys.argv[2]

#reading function under second arguement file
try:
    file2 = open(arg2, "r")
    function_string = file2.read()
    file2.close()
except:
    print("Error! Unable to read " + arg2 + " file")
    sys.exit(1)

function_string = str(function_string)

#Reading prototype and name of the function
os.system("makeheaders " + arg2)
headerFile = arg2.replace(".c", ".h")

try:
    f = open(headerFile, "r")
    func_prototype = f.read()
    f.close()
    os.system("rm " + headerFile)
except:
    print("An error occurred while dealing with function prototype")
    sys.exit(1)

func_prototype = func_prototype.replace(func_prototype[func_prototype.find("/*") : func_prototype.find("*/") + 3], "")

func_name = func_prototype[:func_prototype.find("(")]

#Creating three versions of the function
f1 = function_string.replace(func_name, func_name+"_asimd", 1)

idx1 = f1.find("printf")
idx2 = f1.find(";", idx1)
f1 = f1.replace(f1[idx1:idx2], 'printf("Using Advance SIMD implementation\\n")')

f2 = function_string.replace(func_name, func_name + "_sve", 1)

idx1 = f2.find("printf")
idx2 = f2.find(";", idx1)
f2 = f2.replace(f2[idx1:idx2], 'printf("Using SVE implementation\\n")')

f3 = function_string.replace(func_name, func_name + "_sve2", 1)

idx1 = f3.find("printf")
idx2 = f3.find(";", idx1)
f3 = f3.replace(f3[idx1:idx2], 'printf("Using SVE2 implementation\\n")')

#Writing function1.c
func1 = open("function1.c", "w")
func1.write(f1)
func1.close()

#Writing function2.c
func2 = open("function2.c", "w")
func2.write(f2)
func2.close()

#Writing function3.c
func3 = open("function3.c", "w")
func3.write(f3)
func3.close()

#ifun.h - header file for ifunc
f1_prototype = func_prototype.replace(func_name, func_name+"_asimd")
f2_prototype = func_prototype.replace(func_name, func_name+"_sve")
f3_prototype = func_prototype.replace(func_name, func_name+"_sve2")

header_string = f1_prototype + '\n' + f2_prototype + '\n' + f3_prototype

#writing ifunc.h
header_file = open("ifunc.h", "w")
header_file.write(header_string)
header_file.close()

#ifun.c - tool for auto-vectorization
#reading the template file
try:
    template = open("template.txt", "r") 
    ifunc_string = template.read()
    template.close()
except:
    print("Unable to open template.txt [file missing or corrupted]")
    exit(1)

#filling out the template for ASIMD, SVE, SVE2

fnames = func_name.split(" ")
func_name = fnames[1]

ifunc_string = ifunc_string.replace("##", func_prototype.replace(";\n",""))
ifunc_string1 = func_prototype.replace(func_name, "*sve2")
ifunc_string1 = ifunc_string1[:len(ifunc_string1) - 1]
ifunc_string = ifunc_string.replace('#sve2', ifunc_string1)
ifunc_string2 = func_prototype.replace(func_name, "*sve")
ifunc_string2 = ifunc_string2[:len(ifunc_string2) - 1]
ifunc_string = ifunc_string.replace('#sve', ifunc_string2)
ifunc_string3 = func_prototype.replace(func_name, "*asimd")
ifunc_string3 = ifunc_string3[:len(ifunc_string3) - 1]
ifunc_string = ifunc_string.replace('#asimd',ifunc_string3)

# List of built in Datatypes - 
dTypes = ["unsigned", "char", "int", "float", "double", "long", "short", "*", "signed", "wchar_t", "const", "&"]
f1_prototype = f1_prototype[func_prototype.find(func_name):]
f2_prototype = f2_prototype[func_prototype.find(func_name):]
f3_prototype = f3_prototype[func_prototype.find(func_name):]

print("Does the function accepts parameters of user defined data type (struct or class)")
ch = input("<Y/N>: ")

if ch.lower() == "y":
    print("Enter the user defined data types seprated by ,")
    u_dTypes = input(">")
    u_dTypes = u_dTypes.split(",")

    dTypes = dTypes + u_dTypes 

for i in dTypes:
    f1_prototype = f1_prototype.replace(i, "")
    f2_prototype = f2_prototype.replace(i, "")
    f3_prototype = f3_prototype.replace(i, "")

ifunc_string = ifunc_string.replace("#fsve2", f3_prototype)
ifunc_string = ifunc_string.replace("#fsve", f2_prototype)
ifunc_string = ifunc_string.replace("#fasimd", f1_prototype)

#writing ifunc.c file
ifunc = open("ifunc.c", "w")
ifunc.write(ifunc_string)
ifunc.close()

#writing a bash script to build the output file and link the functions
bash_script = """#!/bin/sh \n
gcc -g -O3 -march=armv8-a -c function1.c -o  function1.o
gcc -g -O3 -march=armv8-a+sve -c function2.c -o  function2.o
gcc -g -O3 -march=armv8-a+sve2 -c function3.c -o  function3.o
gcc -g -O3 -march=armv8-a @ ifunc.c function?.o -o main"""
bash_script = bash_script.replace('@', arg1)


print("Building... ")
bash = open("build.sh","w")
bash.write(bash_script)
bash.close()

#executing the bash script
os.system("bash build.sh")
os.system("rm build.sh")

print("Successfully builded!!")
print("Do you want to keep function output files {function1.o, function2.o, function3.o}")
ch = input("<Y/N>: ")
if ch.lower() == "n":
    os.system("rm function?.o")

print("Do you want to keep function files {function1.c, function2.c, function3.c}")
ch = input("<Y/N>: ")
if ch.lower() == "n":
    os.system("rm function?.c")


