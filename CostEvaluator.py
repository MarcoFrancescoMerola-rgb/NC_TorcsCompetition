import subprocess
import re
import threading
import numpy as np
import os
import json
import time
from CarSim import client
from concurrent.futures import *

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
    port = int(trackPort[3])-1
    
    # os.chdir("E:\\Programs\\torcs\\")
    # print('using port: ', port)
    # output = subprocess.run(["wtorcs.exe","-T",f"-r .\\Tracks\\{trackName}\\race{port}.xml", "-t 1000000000",
    #                          "-nofuel", "-nodamage","> ServerOutput.txt"],
    #                     stdout=subprocess.PIPE, encoding='utf-8').stdout

    command = ("torcs -r " +os.getcwd()+ f"/Tracks/{trackName}"+ f"/race{port}.xml "+
    "-nofuel -nodamage -t 1000000000" +f"> torcsOutput{trackPort}.txt")
    #print(command)
    os.system(command)

def loadClient(particle,trackName,port):
    stage = 1 # 0=Warm-up, 1=Qualifying 2=Race, 3=unknown <Default=3> 
    steps = 100000
    os.chdir(project_dir)
    result = client.run(trackName,stage,steps,port)
    return result

def startSimulation(trackName,trackPort,particle,retVal):
    global returnValues
    
    torcs_thread = threading.Thread(target=loadTorcs,args=[trackName,trackPort])
    torcs_thread.start()

    time.sleep(1)

    clientResult= None
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(loadClient, particle,trackName,trackPort)
        as_completed(future)
        clientResult= future.result()
    
    torcs_thread.join()

    # TODO: clientResult ottiene gli score della pista
    return clientResult

    # print(output)
    # matches = re.findall("lap.*", output)
    # print(matches)
    # if len(matches) == 0 or len(matches) ==1:
    #     fitness = float('inf')
    # else:
    #     fitness = float(matches[0].split(':')[1]) + float(matches[1].split(':')[1])
    # return fitness

def evaluate(particle):
    global output,tracksList,returnValues

    #TODO: le piste possono avere un calcolo di score
    #      diverso in base alla loro complessita
    simulationsResult = []
    with ThreadPoolExecutor(max_workers=len(tracksList)) as executor:
        futuresList = []
        for trackName in tracksList:
            port =serverTrackPorts[trackName]
            # print('Creo thread: ',trackName, " | ",port)
            # print("------------------------------------")
            future = executor.submit(startSimulation, trackName,port,particle,trackName)
            time.sleep(0.2)
            futuresList.append(future)
        # waiting for all tracks to end
        for f in as_completed(futuresList):
            simulationsResult.append(f.result())



    # working on single track scores

    print('\n--------------------------------------------------\n\t\t   RESULTS\n')
    for v in simulationsResult:
        print(v)
    


    #TODO: genera la funzione di valutazione
    return simulationsResult

### evaluate a particle cost by testing on different
### tracks and estimating a mean score of all
def evaluateParticleCost(particle, paramsName):
    # create a json containing params
    iterator = zip(paramsName, particle)
    jsonParams = dict(iterator)
    with open('./CarSim/tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    
    # evaluate particle on all tracks
    print("Starting evaluation...\n")
    print('--------------------------------------------------\n\t\tRUNNING TRACK\n')
    tmp = evaluate(particle)
    # TODO: create a cost function based on
    #       the results of all tracks score
    return

def scoreAssignment(numLaps, circuitTime, carDamage, racePosition):

    score = float(numLaps * 1000) - (2.0 * circuitTime) - carDamage - (float(racePosition) - 1.0)
    
    return score
