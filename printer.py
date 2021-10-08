######################## IMPORT #########################
import json
import numpy as np
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

def fromArrayToJson(path,array,paramsName):
    with open(path+"/bestParameters", 'w')as f:
            myDict = dict(zip(paramsName,array))
            json.dump(myDict, f)

def fromArrayToJson2(path,array,paramsName):
    with open(path+"/bestParameters2", 'w')as f:
            myDict = dict(zip(paramsName,array))
            json.dump(myDict, f)

def loadJsonParams(path):
    f = open(path)
    parameters = json.load(f)
    f.close()
    return parameters

if __name__ == "__main__":
    #pass
    path  = "./0Res/1.5_1.5_0.7298"
    array = np.loadtxt(path+'/bestpos.csv', delimiter=',')
    param_path = "./test_parameters"
    parameters = loadJsonParams(param_path)
    paramsName = [paramName for paramName in parameters.keys()]
    parameters = np.fromiter(parameters.values(), dtype=float)
    fromArrayToJson2(path,array,paramsName)