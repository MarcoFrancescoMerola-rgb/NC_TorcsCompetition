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
import shutil
from pathlib import Path


#################### GLOBAL VARIABLE #####################
trackMode  = ["Competitive"]       # ["Solo","Competitive"]
soloLapsMode   = ["10Laps"] # ["2Laps","10Laps"]
tracksList = ["Forza", "CG-Track-2", "E-Track-3", "Wheel-1"] #["Forza", "CG-Track-2", "E-Track-3", "Wheel-1"]
# serverTrackPorts = {"Forza":3001,"CG-Track-2":3002,
#                     "E-Track-3":3003,"Wheel-1":3004}
serverTrackPorts = {"First4":{"Forza":3001,"CG-Track-2":3002,
                              "E-Track-3":3003,"Wheel-1":3004},
                    "Second4":{"Forza":3005,"CG-Track-2":3006,
                              "E-Track-3":3007,"Wheel-1":3008}}

returnValues = {"Forza":None,"CG-Track-2":None,
                "E-Track-3":None,"Wheel-1":None}
output=""
project_dir = str(os.getcwd())
carSim_dir = project_dir+"/CarSim/"
torcsProcList={}
pids_dir=""
######################## FUNCTIONS #########################

def killAllTorcsProcs():
    try:
        command =("pkill torcs")
        os.system(command)
    except Exception as ex:
        print(str(ex))
        print("error on torcs all kill")

def lookForTorcsEnding(secondsToWait,threadID):
    time.sleep(secondsToWait)
    try:
        command =("pkill "+f"{threadID}")
        os.system(command)
    except Exception as ex:
        print(str(ex))
        print("aaaaaaa")


# load a torcs instance with specific track parameters
def loadTorcs(trackName,trackPort,trackMode,hyperparams):
    global output
    port = str(trackPort-1)[3]
    
    # os.chdir("E:\\Programs\\torcs\\")
    # print('using port: ', port)
    # output = subprocess.run(["wtorcs.exe","-T",f"-r .\\Tracks\\{trackName}\\race{port}.xml", "-t 1000000000",
    #                          "-nofuel", "-nodamage","> ServerOutput.txt"],
    #                     stdout=subprocess.PIPE, encoding='utf-8').stdout

    # command = ("../torcs-1.3.7/BUILD/bin/torcs -r " +os.getcwd()+ f"/Tracks/{trackName}"+f"/{trackMode}"+ f"/race{port}.xml "+
    # "-nofuel -t 1000000000" +f"> torcsOutput{trackPort}.txt")
    # os.system(command)
    argument=""
    #os.chdir("/home/grupponc1/gruppo1/torcs-1.3.7/BUILD/bin/")
    #pt(os.getcwd())
    proc = None
    if trackMode == 'Solo':
        proc = subprocess.Popen(["/home/grupponc1/gruppo1/torcs-1.3.7/BUILD/bin/torcs", "-r " +os.getcwd()+
                f"/Tracks/{trackName}"+f"/{trackMode}"+f"/{soloLapsMode[0]}"+ f"/race{port}.xml "+
                "-nofuel -t 1000000000" +f"> torcsOutput{trackPort}.txt"], shell=False,stdout=subprocess.DEVNULL)
    else:
        proc = subprocess.Popen(["/home/grupponc1/gruppo1/torcs-1.3.7/BUILD/bin/torcs", "-r " +os.getcwd()+
                f"/Tracks/{trackName}"+f"/{trackMode}"+ f"/race{port}.xml "+
                "-nofuel -t 1000000000" +f"> torcsOutput{trackPort}.txt"], shell=False,stdout=subprocess.DEVNULL)
    torcsProcList[str(proc.pid)]= proc
    with open(f"{pids_dir}"+f"{trackName}_{trackPort}",'w+') as f:
        f.write(f"{proc.pid}")
    #pt(f"{proc.pid}")
    return proc.pid


# load a client instance with specific track parameters
# returns results after race ending
def loadClient(particle,trackName,port,mode,jsonParams):
    stage = 0 # 0=Warm-up, 1=Qualifying 2=Race, 3=unknown <Default=3> 
    steps = 300000
    os.chdir(project_dir)
    result = client.run(trackName,stage,steps,port,mode,jsonParams)
    return result

# starts a simulation given a track settings
# it can run the same track more than once based
# on 'trackMode' global variable
def startSimulation(trackName,trackPort,particle,jsonParams,hyperparams,stats_dir):
    global returnValues, trackMode

    clientResult= []
    #stats_dir="0Res/"+f"{hyperparams['c1']}_{hyperparams['c2']}_{hyperparams['w']}/"
    out_dir = stats_dir+'out.txt'
    
    for index, mode in enumerate(trackMode):
        #pt(f"Starting track {trackName} in {mode}")
        torcs_thread = threading.Thread(target=loadTorcs,args=[trackName,trackPort,mode,hyperparams])
        torcs_thread.start()
        time.sleep(0.3)
        #loading client instance
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(loadClient, particle,trackName,trackPort,mode,jsonParams)
            as_completed(future)
            clientResult.append(future.result())

        myTorcsProcPID=None
        torcs_thread.join()
        with open(f"{pids_dir}"+f"{trackName}_{trackPort}",'r') as f:
            myTorcsProcPID = int(f.read())
        try:
            for torcsProc in torcsProcList.values():
                if torcsProc.pid ==myTorcsProcPID:
                    torcsProc.kill()
                    #lookForTorcsEnding(1,myTorcsProcPID)
                    time.sleep(0.5)
                    #pt(stats_dir+'out.txt',f'process killed: {myTorcsProcPID}')
                    del torcsProcList[str(myTorcsProcPID)]
                    #pt("processo eliminato dalla lista")
                    break
        except Exception as ex:
            pt("outError.txt",ex)
    pt(out_dir,
    f"track: {clientResult[0]['trackName']}, "
    f"positiveOvertaking: {clientResult[0]['positiveOvertaking']}, "+
    f"negativeOvertaking: {clientResult[0]['negativeOvertaking']}, "+
    #f"circuitTime: {clientResult[0]['circuitTime']}, "+
    #f"totalTimeOffTrack: {clientResult[0]['totalTimeOffTrack']}, "+
    f"damage: {clientResult[0]['damage']}, "+
    f"racePos: {clientResult[0]['racePos']}, "+
    #f"meanSpeed: {clientResult[0]['meanSpeed']}, "+
    #f"lapsNum: {clientResult[0]['lapsNum']}, "+
    f"lapsNum: {clientResult[0]['lapsNum']}, ")
    #f"lapsTime: {clientResult[0]['lapsTime']}")
    score = TracksScoreCalculator(clientResult,trackMode)
    return score

# starts given particle simulation on all tracks specified
# by 'tracksList' global variable
def evaluate(particle,jsonParams,hyperparams,torcsPortsToUse,stats_dir):
    global output,tracksList,returnValues
    
    simulationsResult = []
    with ThreadPoolExecutor(max_workers=len(tracksList)) as executor:
        futuresList = []
        for trackName in tracksList:
            port =serverTrackPorts[torcsPortsToUse][trackName]
            future = executor.submit(startSimulation, trackName,port,particle,jsonParams,hyperparams,stats_dir)
            time.sleep(0.2)
            futuresList.append(future)
        # waiting for all tracks to end
        for f in as_completed(futuresList):
            simulationsResult.append(f.result())
    # working on single track scores
    # pt('\n--------------------------------------------------\n\t\t   RESULTS\n')
    killAllTorcsProcs()
    shutil.rmtree(pids_dir)
    return particleScoreEvaluation(simulationsResult)

# evaluate a particle cost by testing on different
# tracks and estimating a mean score of all
def evaluateParticleCost(particle, paramsName,hyperparams,torcsPortsToUse,stats_dir):
    # create a json containing params
    global pids_dir
    #pids_dir = "0Res/"+f"{hyperparams['c1']}_{hyperparams['c2']}_{hyperparams['w']}/pids/"
    pids_dir = stats_dir+"/pids/"
    Path(pids_dir).mkdir(parents=True, exist_ok=True)
    iterator = zip(paramsName, particle)
    jsonParams = dict(iterator)
    with open('./CarSim/tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    tmp = evaluate(particle,jsonParams,hyperparams,torcsPortsToUse,stats_dir)
    return tmp

# returns a single track score based on its
# stats
def singleTrackScore(raceStats,raceMode):
    global soloLapsMode
    finalScore= None

    lapsNotCompletedPenality=0
    try:
        if raceMode =='Solo':
            if soloLapsMode[0] == "10Laps":
                if raceStats['lapsNum'] <10:
                    lapsNotCompletedPenality = 1000* (10-raceStats['lapsNum'])
            else:
                if raceStats['lapsNum'] <2:
                    lapsNotCompletedPenality = 1000* (2-raceStats['lapsNum'])
    except Exception as ex:
        pt("outError.txt",f"errore singleTrackScore: \n{ex}")
        lapsNotCompletedPenality=0

    timeScore     = raceStats['circuitTime']
    damageScore   = int( (raceStats['damage']/20) * 1) #ogni 20 dmg 1 secondi di penalty
    positionScore = int(raceStats['racePos'])*100 -100
    positiveOvertakingScore = raceStats['positiveOvertaking']
    negativeOvertakingScore = raceStats['negativeOvertaking']
    #solo score
    #finalScore    = raceStats['circuitTime'] + 2.5*int(raceStats['totalTimeOffTrack']) + damageScore
    #solo score per migliorare andamento su 10 giri per pista
    #finalScore     = raceStats['circuitTime'] + 2.0*int(raceStats['totalTimeOffTrack']) + damageScore + lapsNotCompletedPenality
    #competitive score
    #finalScore    = 2*positionScore + raceStats['circuitTime'] + 1.5*int(raceStats['totalTimeOffTrack']) + damageScore
    #finalScore    = 20*positionScore + raceStats['circuitTime'] + 2.0*int(raceStats['totalTimeOffTrack']) + damageScore
    finalScore    = positionScore - 20*positiveOvertakingScore + 10*negativeOvertakingScore
    #finalScore    =  5*int(raceStats['totalTimeOffTrack']) + int((damageScore+5)*0.5) + 3*positionScore

    return finalScore

# returns a score as sum of races score
def TracksScoreCalculator(racesStat,raceMode):
    finalScore= 0
    for index,raceStat in enumerate(racesStat):
        raceScore=singleTrackScore(raceStat,raceMode[index])
        finalScore+=raceScore

    return finalScore

# returns a score as mean of races score
def particleScoreEvaluation(scores):
    finalScore = 0
    finalScore = round(statistics.mean(scores),4)
    return finalScore