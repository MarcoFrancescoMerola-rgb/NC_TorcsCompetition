import subprocess
import re
import threading
import numpy as np
import os
import json
import time

output=""
outClient =""
project_dir = str(os.getcwd())
carSim_dir = project_dir+"/CarSim/"
#torcs_dir = "E:\\Programs\\torcs\\"


def loadTorcs():
    global output
    #os.chdir(torcs_dir)
    #print('threadTorcs dir: ', os.getcwd())

    #-T -nofuel -nodamage
    # output = subprocess.call(["wtorcs.exe", "-nofuel", "-nodamage"], cwd=torcs_dir,
    #                          stdout=subprocess.PIPE, encoding='utf-8').stdout

    #["wtorcs.exe","-T", "-r .\\customrace0ovalB.xml", "-nofuel", "-nodamage"]
    # output = subprocess.run(["wtorcs.exe","-T","-r .\\customrace0Forza.xml", "-t 1000000000", "-nofuel", "-nodamage","> ServerOutput.txt"],
    #                         cwd = torcs_dir, stdout=subprocess.PIPE, encoding='utf-8').stdout

    print('sto per avviare torcs')
    command = ("torcs -r " + f"/Tracks/Forza"+ "/race0.xml "+
    "-nofuel -nodamage -t 1000000000 > torcsOutput.txt")
    os.system(command)

def loadClient(particle):
    global outClient
    os.chdir(project_dir)
    #print('threadClient dir: ', os.getcwd())
    tmpArgs = " "
    # for p in particle:
    #     tmpArgs += str(p) + " "
    # --stage 0 --track ovalB --steps 1000 --port 3001 --host localhost
    tmpArgs +='--stage 1 --track ovalB --steps 100000 --port 3001 --host localhost' 
    os.system('python ' + carSim_dir+ 'client.py ' + tmpArgs )

def evaluate(particle):
    global output

    torcs_thread = threading.Thread(target=loadTorcs)
    torcs_thread.start()
    time.sleep(1)
    client_thread = threading.Thread(target=loadClient(particle))
    client_thread.start()
    
    torcs_thread.join()
    client_thread.join()
    matches = re.findall("lap.*", output)
    [print(m,end='\r') for m in matches]
    if len(matches) == 0 or len(matches) ==1:
        fitness = float('inf')
    else:
        fitness = float(matches[0].split(':')[1]) + float(matches[1].split(':')[1])
    return fitness


def evaluateCostSwarm(swarm):
    fitness = np.zeros((swarm.shape[0],))
    count = 0
    with open('tmp_params','r') as json_file:
        json_param = json.load(json_file)
    for particle in swarm:
        i_particle = 0
        for key in json_param.keys():
            json_param[key] = particle[i_particle]
            i_particle += 1
        with open('tmp_params', 'w') as outfile:
            json.dump(json_param, outfile)
        temp = evaluate()
        print("Particle "+ str(count) + " -> " + str(temp))
        fitness.put(count,temp)
        count += 1
    print("Total fitness array: " + str(fitness))

    return fitness

def evaluateCostParticle(particle, paramsName):
    iterator = zip(paramsName, particle)
    jsonParams = dict(iterator)
    with open('./CarSim/tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    tmp = evaluate(particle)
    print(tmp)
    return