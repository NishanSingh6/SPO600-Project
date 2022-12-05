"""
Autovectorized function building tool

Author: Nishan Singh.
Licensed under the terms of the GPL verion 2.
Developed for the project for SPO600 at Seneca College of Applied Arts and Technology.
Version: 1.0 - Stage 2 of the project (initial implementation)

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
f = open(arg2, "r")
x = f.read()
f.close()
x = str(x)

#Creating three versions of the function
f1 = x.replace("void adjust_channels", "void adjust_channels_asimd", 1)

idx1 = f1.find("printf")
idx2 = f1.find(";", idx1)
f1 = f1.replace(f1[idx1:idx2], 'printf("Using Advance SIMD implementation\\n")')

f2 = x.replace("void adjust_channels", "void adjust_channels_sve", 1)

idx1 = f2.find("printf")
idx2 = f2.find(";", idx1)
f2 = f2.replace(f2[idx1:idx2], 'printf("Using SVE implementation\\n")')

f3 = x.replace("void adjust_channels", "void adjust_channels_sve2", 1)

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
f1 = f1[f1.find("void adjust_channels") : f1.find("{", f1.find("void adjust_channels"))] + ";"
f2 = f2[f2.find("void adjust_channels") : f2.find("{", f2.find("void adjust_channels"))] + ";"
f3 = f3[f3.find("void adjust_channels") : f3.find("{", f3.find("void adjust_channels"))] + ";\n"
header_string = f1 + '\n\n' + f2 + '\n\n' + f3

header_file = open("ifunc.h", "w")
header_file.write(header_string)
header_file.close()


#ifun.c - tool for auto-vectorization
#reading the template file

template = open("template.txt", "r") 
t = template.read()
template.close()

func_prototype = x[x.find("void adjust_channels") : x.find("{", x.find("void adjust_channels"))]

#filling out the template for ASIMD, SVE, SVE2
t = t.replace("##", func_prototype)

t = t.replace('#sve2', func_prototype.replace("adjust_channels", "*sve2"));
t = t.replace('#sve', func_prototype.replace("adjust_channels", "*sve"));
t = t.replace('#asimd', func_prototype.replace("adjust_channels", "*asimd"));

dTypes = ["unsigned", "char", "int", "float", "double", "long", "short", "*"]
func_prototype = func_prototype[func_prototype.find("adjust_channels"):]

for i in dTypes:
    func_prototype = func_prototype.replace(i, "")

t = t.replace("#fsve2", func_prototype.replace("adjust_channels", "adjust_channels_sve2") + ';')
t = t.replace("#fsve", func_prototype.replace("adjust_channels", "adjust_channels_sve") + ';')
t = t.replace("#fasimd", func_prototype.replace("adjust_channels", "adjust_channels_asimd") + ';')

#writing ifunc.c file
ifunc = open("ifunc.c", "w")
ifunc.write(t)
ifunc.close()

#writing a bash script to build the output file and link the functions
bash_script = """#!/bin/sh \n
gcc -g -O3 -march=armv8-a -c function1.c -o  function1.o
gcc -g -O3 -march=armv8-a+sve -c function2.c -o  function2.o
gcc -g -O3 -march=armv8-a+sve2 -c function3.c -o  function3.o
gcc -g -O3 -march=armv8-a @ ifunc.c function?.o -o main"""
bash_script = bash_script.replace('@', arg1)
bash = open("build.sh","w")
bash.write(bash_script)
bash.close()

#executing the bash script
os.system("bash build.sh")





