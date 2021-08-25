######################## IMPORT #########################
import os
import numpy as np
import pyswarms.backend as p
from pyswarms.backend.topology import Star
import json
import CostEvaluator
import time
import datetime
import itertools
from tqdm import tqdm
import signal
import sys
from contextlib import redirect_stdout
from printer import print as pt, jsonFileWriter, cleanJson
import printer
import mail

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0)) #hide traceback

#################### GLOBAL VARIABLE #####################
param_path = "./test_parameters"

######################## FUNCTION #########################
### Returns a list of hyperparmeters combinations
### enclosed in a dict so one can test different sets
def generateHyperparamsCombinations(psoH):
    paramsList = list(psoH.keys())
    l= len(psoH[paramsList[0]])*len(psoH[paramsList[1]])*len(psoH[paramsList[2]])
    combinationsList=[None for i in range(0,l)]
    combIndex =0
    
    for c1Param in psoH['c1']:
        for c2Param in psoH['c2']:
            for wParam in psoH['w']:
                combinationsList[combIndex]={'c1':c1Param,'c2':c2Param,'w':wParam}
                combIndex +=1
    return combinationsList

### Returns a dictionary containing json loaded from path
def loadJsonParams(path):
    f = open(path)
    parameters = json.load(f)
    f.close()
    return parameters

### Executes a PSO algoritm based on Global Best and 
### returns a particle/params set to be used as
### torcs controller 
def PSO_execution(hyperparams,swarmParticles=10,iteractions=3):
    # swarm settings
    particlesNum = swarmParticles
    dimensions = 49
    iteractionNum = iteractions
    options = hyperparams

    # import default_parameters as json
    parameters = loadJsonParams(param_path)
    paramsName = [paramName for paramName in parameters.keys()]
    parameters = np.fromiter(parameters.values(), dtype=float)
    # convert json to numpy array
    array_param = np.zeros((1, dimensions))
    array_param[0] = parameters
    # create swarm with center in default_parameters
    swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions,
                           options=options, center=array_param)
    
    # create swarm with parameters
    init_swarm = np.zeros((particlesNum, dimensions))
    pt("\nInitializing swarm..")
    for n in tqdm(range(particlesNum)):
        init_swarm[n] = swarm.position[n]
    
    # set first particle values equal to default parameters
    init_swarm[0] = parameters

    my_swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions,
                              options=options, init_pos=init_swarm)
    
    my_topology = Star()

    my_swarm.pbest_cost = np.ndarray(shape=my_swarm.position.shape[0],buffer=np.ones((particlesNum)) * np.inf)
    my_swarm.best_pos = np.zeros(shape=my_swarm.position.shape[1])

    for iteraction in range(iteractionNum):
        pt(f"Executing iteration: {iteraction+1} / {iteractionNum}")

        for index, particle in enumerate(my_swarm.position):
            pt(f'Executing particle n.{index+1} evaluation...')
            particleScore = CostEvaluator.evaluateParticleCost(particle, paramsName)
            pt(f"score: {particleScore}")

            #check if actual score is better then particle best position
            if particleScore < my_swarm.pbest_cost[index]:
                pt("updating particle best position and cost...")
                my_swarm.pbest_cost[index] = particleScore
                my_swarm.pbest_pos[index] = particle
            #check if actual score is better then swarm best position
            my_swarm.best_pos, my_swarm.best_cost = my_topology.compute_gbest(my_swarm)
            
        # swarm update
        nextPosition =  my_topology.compute_position(my_swarm)
        nextVelocity =  my_topology.compute_velocity(my_swarm)
        # print("next position: ",nextPosition)
        my_swarm.position = nextPosition
        my_swarm.velocity = nextVelocity

    paramDict = dict(zip(paramsName, my_swarm.best_pos))

    return my_swarm.best_pos, my_swarm.best_cost, paramDict


if __name__ == "__main__":
    start_time = time.time()
    printer.cleanFile()
    # psoHyperparams = {'c1':[0.6,1,1.5,1.75,2],
    #                   'c2':[0.6,1,1.5,1.75,2],
    #                   'w':[0.729, 0.67]}
    psoHyperparams = {'c1':[0.6,1,1.75,2],
                      'c2':[0.6,1.5],
                      'w':[0.67]}
    
    # static seed for replication
    seedsList = [1,2578,54,443,12,4565675,456456,3435]
    seedIndex =np.random.randint(0,len(seedsList))
    np.random.seed(seedsList[seedIndex])
    pt(f"active seed: {seedsList[seedIndex]}")
    posCost =[]
    swarmParticles = 30
    iteractions = 100

    # creating hyperparameters combinations
    hCombinations = generateHyperparamsCombinations(psoHyperparams)
    for hyperparameters in hCombinations:
        pt(f"Executing combination: {hyperparameters}")
        pos, cost, paramDict=PSO_execution(hyperparameters,swarmParticles,iteractions)
        posCost.append((pos,cost,hyperparameters,paramDict))
    # selecting best position with it's cost,params and hyperparameters selected
    (bestPost,bestCost,hyperparameters,paramDict)= min(posCost, key=  lambda t: t[1])
    
    pt(f"\nBest Position:\t{bestPost}")
    jsonFileWriter(paramDict)         #WRITE ON JSON
    pt(f"Best Cost:\t{bestCost}")
    pt(f"Hyperparamters:\t{hyperparameters}\n")
    execution_time = f"---------- {round((time.time() - start_time), 2)} seconds ----------" 
    pt("\n"+execution_time+"\n")
    mail.sendEmail()
    exit(0)