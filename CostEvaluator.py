import subprocess
import re
import threading
import numpy as np
import os
import json

output=""
project_dir = os.getcwd()+"\\CarSim\\"
# print(project_dir)
# exit(0)
torcs_dir = 'E:/Programs/torcs/'

def loadTorcs():
    global output
    os.chdir(torcs_dir)
    #-T
    output = subprocess.run('wtorcs.exe -nofuel -nodamage', stdout=subprocess.PIPE, encoding='utf-8').stdout

def loadClient(particle):
    tmpStr = " "
    for p in particle:
        tmpStr += str(p) + " "

    os.system('python ' + project_dir+ 'client.py ' + tmpStr)

def evaluate(particle):
    global output
    
    torcs_thread = threading.Thread(target=loadTorcs)
    torcs_thread.start()

    client_thread = threading.Thread(target=loadClient(particle))
    client_thread.start()
    
    torcs_thread.join()
    client_thread.join()
    
    matches = re.findall("lap.*", output)
    print(matches)
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
    with open('tmp_params','w') as json_file:
        json.dump(jsonParams,json_file)
    tmp = evaluate(particle)
    print(tmp)
    return