import subprocess
import re
import threading
import numpy as np
import os
import json
import time


tracksList = ["Forza", "CG-Track-2", "E-Track-3", "Wheel-1"]
serverTrackPorts = {"Forza":"3011","CG-Track-2":"3012",
                    "E-Track-3":"3013","Wheel-1":"3014"}
returnValues = {"Forza":None,"CG-Track-2":None,
                "E-Track-3":None,"Wheel-1":None}
output=""
outClient =""
project_dir = str(os.getcwd())
carSim_dir = project_dir+"/CarSim/"

def loadTorcs():
    global output

    command = ("torcs -r " + f"/Tracks/Forza"+ "/race0.xml "+
    "-nofuel -nodamage -t 1000000000 > torcsOutput.txt")
    os.system(command)

def loadClient(particle):
    global outClient
    os.chdir(project_dir)
    tmpArgs =' --stage 1 --track ovalB --steps 100000 --port 3001 --host localhost' 
    os.system('python ' + carSim_dir+ 'client.py ' + tmpArgs )

def startSimulation(trackName,TrackPort,particle,retVal):
    global returnValues
    #print(trackName,' | ', TrackPort)
    returnValues[retVal] = [trackName,1]

    # TODO: returnValues ottiene gli score della pista
    return 1
    torcs_thread = threading.Thread(target=loadTorcs)
    torcs_thread.start()

    time.sleep(1)

    client_thread = threading.Thread(target=loadClient(particle))
    client_thread.start()
    
    torcs_thread.join()
    client_thread.join()

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