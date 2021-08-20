import os
import numpy as np
import pyswarms.backend as p
from pyswarms.backend.topology import Star
import json
import CostEvaluator
from pyswarms.utils.plotters import plot_cost_history
import matplotlib.pyplot as plt
import time
import datetime
import itertools
from tqdm import tqdm

param_path = "./test_parameters"

### Returns a list of hyperparmeters combinations
### enclosed in a dict so one can test different sets
def generateHyperparamsCombinations( psoH: dict):
    paramsList = list(psoH.keys())
    l= len(psoH[paramsList[0]])*len(psoH[paramsList[1]])*len(psoH[paramsList[2]])
    combinationsList=[None for i in range(0,l)]
    combIndex =0
    # for i in range(0,3):
    #     for focusedParamValue in psoH[paramsList[i]]:
    
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

    #boundsList = [(1000,10000),(0,100)]
    #bounds = np.array(boundsList)

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
    print("\nInitializing swarm..")
    for n in tqdm(range(particlesNum)):
        init_swarm[n] = swarm.position[n]
    
    # set first particle values equal to default parameters
    init_swarm[0] = parameters

    my_swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions,
                              options=options, init_pos=init_swarm)
    
    # position are particles' parameters
    # while cost is the time on lap
    # Initializing swarm scores
    my_swarm.pbest_pos = np.zeros(my_swarm.position.shape)
    my_swarm.best_pos = float("inf")
    my_swarm.pbest_cost = np.ndarray(shape=my_swarm.position.shape[0],buffer=np.ones((particlesNum)) * np.inf)
    my_swarm.best_cost = float("inf")


    for i in range(iteractionNum):
        print("Executing iteration: ", i+1,"/",iteractionNum)
        for particle in my_swarm.position:
            CostEvaluator.evaluateParticleCost(particle, paramsName)
            #exit(0)
            #TODO: continua ad implementare pso
            
    pass

if __name__ == "__main__":
    # psoHyperparams = {'c1':[0.6,1,1.5,1.75,2],
    #                   'c2':[0.6,1,1.5,1.75,2],
    #                   'w':[0.729, 0.67]}
    psoHyperparams = {'c1':[0.6,1,1.75,2],
                      'c2':[0.6,1.5],
                      'w':[0.67]}
    
    # static seed for replication
    seedsList = [1,2578,54,443]
    np.random.seed(seedsList[0])

    swarmParticles = 2
    iteractions = 3
    hCombinations = generateHyperparamsCombinations(psoHyperparams)
    for hyperparamters in hCombinations:
        print("----------------------------------------")
        print("Executing combination: ", hyperparamters)
        PSO_execution(hyperparamters,swarmParticles,iteractions)
    exit(0)