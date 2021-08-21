import subprocess
import re
import threading
import numpy as np
import os
import json
import time


tracksList = ["Forza"]#["Forza", "CG-Track-2", "E-Track-3", "Wheel-1"]
serverTrackPorts = {"Forza":"3001","CG-Track-2":"3002",
                    "E-Track-3":"3003","Wheel-1":"3004"}
returnValues = {"Forza":None,"CG-Track-2":None,
                "E-Track-3":None,"Wheel-1":None}
output=""
project_dir = str(os.getcwd())
carSim_dir = project_dir+"/CarSim/"

def loadTorcs(trackName,trackPort):
    global output

    # os.chdir("E:\\Programs\\torcs\\")
    # output = subprocess.run(["wtorcs.exe","-T","-r .\\Tracks\\Forza\\race0.xml", "-t 1000000000",
    #                          "-nofuel", "-nodamage","> ServerOutput.txt"],
    #                     stdout=subprocess.PIPE, encoding='utf-8').stdout

    command = ("torcs -r " + f"./Tracks/{trackName}"+ "/race0.xml "+
    "-nofuel -nodamage -t 1000000000 > torcsOutput.txt")
    print(command)
    os.system(command)

def loadClient(particle,trackName,port):
    global outClient
    os.chdir(project_dir)
    tmpArgs =f' --stage 1 --track {trackName} --steps 100000 --port {port} --host localhost' 
    os.system('python ' + carSim_dir+ 'client.py ' + tmpArgs )

def startSimulation(trackName,trackPort,particle,retVal):
    global returnValues
    print(trackName,' | ', trackPort)
    
    torcs_thread = threading.Thread(target=loadTorcs,args=[trackName,trackPort])
    torcs_thread.start()

    time.sleep(1)

    client_thread = threading.Thread(target=loadClient,args=[particle,trackName,trackPort])
    client_thread.start()
    
    torcs_thread.join()
    client_thread.join()

    # TODO: returnValues ottiene gli score della pista
    returnValues[retVal] = [trackName,1]
    return 1

    print(output)
    matches = re.findall("lap.*", output)
    print(matches)
    if len(matches) == 0 or len(matches) ==1:
        fitness = float('inf')
    else:
        fitness = float(matches[0].split(':')[1]) + float(matches[1].split(':')[1])
    return fitness

def evaluate(particle):
    global output,tracksList,returnValues
    subProcs = []
    # returnValues = {"Forza":None,"CG-Track-2":None,
    #                 "E-Track-3":None,"Wheel-1":None}

    #TODO: le piste possono avere un calcolo di score
    #      diverso in base alla loro complessita
    for trackName in tracksList:
        port =serverTrackPorts[trackName]
        #returnValues[trackName]]
        subProcs.append(threading.Thread(target=startSimulation,
                       args=[trackName,port,particle,trackName]))
        subProcs[-1].start()
        time.sleep(1)
        pass
    # waiting for all tracks to end
    for proc in subProcs:
        proc.join()
    # working on single track scores

    # print('results:')
    # for v in returnValues.values():
    #     print(v)
    

    #TODO: genera la funzione di valutazione
    return 1

### evaluate a particle cost by testing on different
### tracks and estimating a mean score of all
def evaluateParticleCost(particle, paramsName):
    # create a json containing params
    iterator = zip(paramsName, particle)
    jsonParams = dict(iterator)
    with open('./CarSim/tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    
    # evaluate particle on all tracks
    print("Starting evaluation...")
    tmp = evaluate(particle)
    # TODO: create a cost function based on
    #       the results of all tracks score
    return