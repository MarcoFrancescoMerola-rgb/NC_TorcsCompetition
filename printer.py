######################## IMPORT #########################
import json

#################### GLOBAL VARIABLE #####################
FILENAME = ['out.txt','bestParameters']
pr = print

######################## FUNCTION ########################
def cleanFile():
    with open(FILENAME[0],'w') as f:
        f.write('')
        pass

def print(string):
    pr(string)
    with open(FILENAME[0],'a') as f:
        f.write("\n"+string)

def jsonFileWriter(param):
    with open(FILENAME[1], 'w')as f:
        json.dump(param, f)

def cleanJson():
    with open(FILENAME[1],'w') as f:
        pass
