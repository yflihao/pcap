import os
import sys
import getopt
import fileinput

inputfile = ''
outputfile = ''

def usage():
    print("usage:\n\
    -h <help>   -- show help message\n\
    -i <input>  -- input file name\n")

def parseParam(argv):
   global inputfile,outputfile
   try:
      opts, args = getopt.getopt(sys.argv[1:],"hi:")
   except getopt.GetoptError:
      usage()
      sys.exit()
   for opt, arg in opts:
      if opt == '-h':
         usage()
         sys.exit()
      elif opt == '-i':
         inputfile = arg
         outputfile = arg+".tmp"

   if inputfile == '':
      usage()
      sys.exit()
   else:
      print('input ：', inputfile)
      print('output：', outputfile) 

def convert():
    i_h = open(inputfile, 'r')
    o_h = open(outputfile, 'w', newline='\n')
    while 1:
        lines = i_h.readlines(1000)
        if not lines:
            break
        for line in lines:
            if line.find('NET /I') != -1 and line.find('Dump') != -1:
                result = line[0:15] + 'SXR 09 : ' + line[line.find('Dump'):]
                print(result, end='')
                o_h.write(result)
    i_h.close()
    o_h.close()

def runcommand(cmd):
    print('*****************************************')
    print(cmd)
    print('*****************************************')
    result = os.popen(cmd)
    print(result.read())


if __name__ == "__main__":
   parseParam(sys.argv[1:])
   convert()
   print('\r\nrun command...\n')
   runcommand("del sim* pcap /q")
   runcommand("pcapParser.exe -tracef " + outputfile)
   runcommand("copy pcap\\sim* .\\")