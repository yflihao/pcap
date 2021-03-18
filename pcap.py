

import os
import sys
import getopt
import fileinput
from enum import Enum
import re

toolpath = sys.path[0]

platform = '8910'
inputfile = ''
outputfile = ''


class FSM(Enum):
    CONVERT_NONE = 0
    CONVERT_NETI = 1
    CONVERT_NETI_FAIL = 3
    CONVERT_NETDUMP = 4
    CONVERT_NETDUMP_FAIL = 8
    CONVERT_NETDUMP_FINISH = 10

def usage():
    print("usage:\n\
    --plat = <platform> -- choose platform\n\
             (only support 8910 or 8811 platform)\n\
    -i       <input>    -- input file name\n\
    -h       <help>     -- show help message\n")

def parseParam(argv):
   global platform,inputfile,outputfile
   try:
      opts, args = getopt.getopt(sys.argv[1:],"hi:",["plat="])
   except getopt.GetoptError:
      usage()
      sys.exit()
   for opt, arg in opts:
      if opt == '-h':
         usage()
         sys.exit()
      elif opt == '-i':
         inputfile = arg
         outputfile = toolpath + "\\" + arg + ".tmp"
      elif opt == '--plat':
         platform = arg

   if inputfile == '':
      usage()
      sys.exit()
   else:
      print('\nplat ：', platform)
      print('input ：', inputfile)
      print('output：', outputfile, '\n') 

def isHexStr(content):
    ret = re.match("^[A-Fa-f0-9]+$", content) 
    if ret:
      return True
    else:
      return False

def getNetDumpNetDumpSize(content):
    ret = re.match("^[(](0)(X|x)[A-Fa-f0-9]{8}(/)(\d{1,4})[)]", content) 
    if ret:
      return int(content[content.find('/')+1:content.find(')')])
    else:
      return 0

def getNetDumpNetDumpData(content):
    ret = re.match("^[(](0)(X|x)[A-Fa-f0-9]{8}(/)(\d{1,4})[)]", content) 
    if ret:
      return content[content.find(')')+1:]
    else:
      return '  '

def getNetDumpNetDumpTag(content):
    ret = re.match("^[(](0)(X|x)[A-Fa-f0-9]{8}(/)(\d{1,4})[)]", content) 
    if ret:
      return content[content.find('(0x'):content.find(')')+1]
    else:
      return '  '

def NetDumpDataSerialize(DumpData):
    i = 1
    list1 = list(DumpData)
    while (2*i < len(DumpData)):
      list1.insert((3*i-1), ' ')
      i += 1
    return ''.join(list1)

def convert():
    i_h = open(inputfile, 'r', encoding='UTF-8')
    o_h = open(outputfile, 'w', newline='\n')
    while 1:
      try:
        lines = i_h.readlines(1)
      except:
        print('\033[1;31m*********  Unexpected error:  **********')
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print('****************************************\033[0m')
      else:
        if not lines:
          break
        for line in lines:
          if line.find('NET /I') != -1 and line.find('Dump') != -1:
            result = line[0:15] + 'SXR 09 : ' + line[line.find('Dump'):]
            print(result, end='')
            o_h.write(result)
    i_h.close()
    o_h.close()

def convert8811():
    NetDumpSize = 0
    NetDumpData = ' '
    NetDumpTag = ' '
    ConvertStatus = FSM.CONVERT_NONE.value
    i_h = open(inputfile, 'r', encoding='UTF-8')
    o_h = open(outputfile, 'w', newline='\n')
    while 1:
      try:
        lines = i_h.readlines(1)
      except:
        print('\033[1;31m***************  Unexpected error:  ****************')
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print('****************************************************\033[0m')
      else:
        if not lines:
          break
        for line in lines:
          splitSpace = re.compile(' ')
          line = splitSpace.sub('', line)
          splitTabList = line.split('	')
          TraceTime = splitTabList[1]
          TraceContent = splitTabList[3]

          if ConvertStatus == FSM.CONVERT_NONE.value:
            if TraceContent.find('[NET/I]Dump:') != -1:
              #print(splitTabList)
              NetDumpSize = getNetDumpNetDumpSize(TraceContent)
              NetDumpData = getNetDumpNetDumpData(TraceContent)
              NetDumpTag = getNetDumpNetDumpTag(TraceContent)
              if  NetDumpSize < len(NetDumpData)/2:
                ConvertStatus = FSM.CONVERT_NETI.value
              elif NetDumpSize > len(NetDumpData)/2:
                ConvertStatus = FSM.CONVERT_NETDUMP.value
              else:
                ConvertStatus = FSM.CONVERT_NETDUMP_FINISH.value

          elif ConvertStatus >= FSM.CONVERT_NETI.value and ConvertStatus < FSM.CONVERT_NETI_FAIL.value:
            #print(splitTabList)
            NetDumpSize = getNetDumpNetDumpSize(TraceContent)
            NetDumpData = getNetDumpNetDumpData(TraceContent)
            NetDumpTag = getNetDumpNetDumpTag(TraceContent)
            if  NetDumpSize < len(NetDumpData)/2:
              ConvertStatus += 1
            elif NetDumpSize > len(NetDumpData)/2:
              ConvertStatus = FSM.CONVERT_NETDUMP.value
            else:
              ConvertStatus = FSM.CONVERT_NETDUMP_FINISH.value

          elif ConvertStatus == FSM.CONVERT_NETI_FAIL.value:
            ConvertStatus = FSM.CONVERT_NONE.value
            print('\033[1;31m***************  Unexpected error:  ****************')
            print('[NET /I] Dump NetDumpData is not found')
            print('****************************************************\033[0m')

          elif ConvertStatus >= FSM.CONVERT_NETDUMP.value and ConvertStatus < FSM.CONVERT_NETDUMP_FAIL.value:
            #print(splitTabList)
            if not isHexStr(TraceContent):
              ConvertStatus +=  1
              continue
            NetDumpData = NetDumpData + TraceContent
            if  NetDumpSize < len(NetDumpData)/2:
              ConvertStatus = FSM.CONVERT_NONE.value
              print('\033[1;31m***************  [NET /I] Dump NetDumpData is not match size:  ****************')
              print('Size: ' + str(NetDumpSize) + ' Dump: '+ NetDumpData)
              print('****************************************************************************\033[0m')
            elif NetDumpSize > len(NetDumpData)/2:
              ConvertStatus = FSM.CONVERT_NETDUMP.value
            else:
              ConvertStatus = FSM.CONVERT_NETDUMP_FINISH.value

          elif ConvertStatus == FSM.CONVERT_NETDUMP_FAIL.value:
            ConvertStatus = FSM.CONVERT_NONE.value
            print('\033[1;33m***************  [NET /I] NetDumpData is not enough:  ****************')
            result = '[' + TraceTime + ']' + ' SXR 09 : Dump : ' + NetDumpTag + '' + NetDumpDataSerialize(NetDumpData)
            print(result)
            print('**********************************************************************\033[0m')
            o_h.write(result + '\n')

          elif ConvertStatus == FSM.CONVERT_NETDUMP_FINISH.value:
            ConvertStatus = FSM.CONVERT_NONE.value
            result = '[' + TraceTime + ']' + ' SXR 09 : Dump : ' + NetDumpTag + ' ' + NetDumpDataSerialize(NetDumpData)
            print(result)
            o_h.write(result + '\n')

          else:
            ConvertStatus = FSM.CONVERT_NONE.value
            print('\033[1;31m***************  Unexpected error:  ****************')
            print('Unkown ConvertStatus: ' + str(ConvertStatus))
            print('****************************************************\033[0m')
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
   if platform == '8910':
     convert()
   elif platform == '8811':
     convert8811()
   else:
     usage()
   print('\r\nrun command...\n')
   runcommand("del "+toolpath+"\\pcap\\*.pcap")
   runcommand("pcapParser.exe -tracef " + outputfile)
   runcommand("del "+outputfile)
   runcommand("copy "+toolpath+"\\pcap\\sim* .\\")