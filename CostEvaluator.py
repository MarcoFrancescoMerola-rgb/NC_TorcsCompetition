######################## IMPORT #########################
import subprocess
import re
import threading
import numpy as np
import os
import json
import time
from CarSim import client
from concurrent.futures import *
import statistics
from printer import print as pt

#################### GLOBAL VARIABLE #####################
trackMode = ["Solo"]#["Solo","Competitive"]
tracksList = ["Forza", "CG-Track-2", "E-Track-3", "Wheel-1"]
serverTrackPorts = {"Forza":3001,"CG-Track-2":3002,
                    "E-Track-3":3003,"Wheel-1":3004}
returnValues = {"Forza":None,"CG-Track-2":None,
                "E-Track-3":None,"Wheel-1":None}
output=""
project_dir = str(os.getcwd())
carSim_dir = project_dir+"/CarSim/"

######################## FUNCTION #########################
# load a torcs instance with specific track parameters
def loadTorcs(trackName,trackPort,trackMode):
    global output
    port = str(trackPort-1)[3]
    
    # os.chdir("E:\\Programs\\torcs\\")
    # print('using port: ', port)
    # output = subprocess.run(["wtorcs.exe","-T",f"-r .\\Tracks\\{trackName}\\race{port}.xml", "-t 1000000000",
    #                          "-nofuel", "-nodamage","> ServerOutput.txt"],
    #                     stdout=subprocess.PIPE, encoding='utf-8').stdout

    command = ("torcs -r " +os.getcwd()+ f"/Tracks/{trackName}"+f"/{trackMode}"+ f"/race{port}.xml "+
    "-nofuel -t 1000000000" +f"> torcsOutput{trackPort}.txt")
    #print(command)
    os.system(command)

# load a client instance with specific track parameters
# returns results after race ending
def loadClient(particle,trackName,port):
    stage = 1 # 0=Warm-up, 1=Qualifying 2=Race, 3=unknown <Default=3> 
    steps = 100000
    os.chdir(project_dir)
    result = client.run(trackName,stage,steps,port)
    return result

# starts a simulation given a track settings
# it can run the same track more than once based
# on 'trackMode' global variable
def startSimulation(trackName,trackPort,particle):
    global returnValues, trackMode

    clientResult= []
    
    for index, mode in enumerate(trackMode):
        pt(f"Starting track {trackName} in {mode}")
        torcs_thread = threading.Thread(target=loadTorcs,args=[trackName,trackPort,mode])
        torcs_thread.start()

        time.sleep(0.3)
        #loading client instance
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(loadClient, particle,trackName,trackPort)
            as_completed(future)
            clientResult.append(future.result())
        
        torcs_thread.join()
    score = perMoreThanOneTrackScore(clientResult,trackMode)

    return score

# starts given particle simulation on all tracks specified
# by 'tracksList' global variable
def evaluate(particle):
    global output,tracksList,returnValues
    
    simulationsResult = []
    with ThreadPoolExecutor(max_workers=len(tracksList)) as executor:
        futuresList = []
        for trackName in tracksList:
            port =serverTrackPorts[trackName]
            future = executor.submit(startSimulation, trackName,port,particle)
            time.sleep(0.2)
            futuresList.append(future)
        # waiting for all tracks to end
        for f in as_completed(futuresList):
            simulationsResult.append(f.result())
    # working on single track scores
    pt('\n--------------------------------------------------\n\t\t   RESULTS\n')

    return particleScoreEvaluation(simulationsResult)

# evaluate a particle cost by testing on different
# tracks and estimating a mean score of all
def evaluateParticleCost(particle, paramsName):
    # create a json containing params
    iterator = zip(paramsName, particle)
    jsonParams = dict(iterator)
    with open('./CarSim/tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    pt("--------------------------------------------------")
    pt('--------------------------------------------------\n\t\tRUNNING TRACK\n')
    tmp = evaluate(particle)

    return tmp

# returns a single track score based on its
# stats
def singleTrackScore(raceStats,raceMode):
    finalScore= 0
    minTime = 0
    maxTime = 360 if raceMode == "Solo" else 3600
    # for raceStats in stats:
    #     pass
    # return finalScore
    positionScore = (raceStats["racePos"]) * 1000 -999
    timeScore     = ((raceStats['circuitTime'] - minTime) /(maxTime - minTime))
    damageScore   = raceStats['damage']
    finalScore    = (positionScore * timeScore) + damageScore

    return finalScore

# returns a score as sum of races score
def perMoreThanOneTrackScore(racesStat,raceMode):
    finalScore= 0
    for index,raceStat in enumerate(racesStat):
        raceScore=singleTrackScore(raceStat,raceMode[index])
        finalScore+=raceScore

    return finalScore

# returns a score as mean of races score
def particleScoreEvaluation(scores):
    finalScore= 0
    finalScore = round(statistics.mean(scores),4)

    return finalScore