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

#this function load the json file relative to default parameters
def loadJsonParams(path):
    f = open(path)
    parameters = json.load(f) #parameters is a dict
    f.close()

    return parameters

def PSO_execution():
    particlesNum = 10
    dimensions = 49
    iterations = 2

    options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}
    np.random.seed(1)

    boundsList = [(1000,10000),(0,100)]
    bounds = np.array(boundsList)

    #import default_parameters as np.ndarray
    parameters = loadJsonParams(param_path)
    paramsName = [paramName for paramName in parameters.keys()]
    parameters = np.fromiter(parameters.values(), dtype=float)
    array_param = np.zeros((1, dimensions))
    array_param[0] = parameters
    #create swarm with center in default_parameters
    swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions, options=options, center=array_param)
    
    #create swarm with parameters 
    init_swarm = np.zeros((particlesNum, dimensions))
    print("\nInitialize swarm..")
    for n in tqdm(range(particlesNum)):
        init_swarm[n] = swarm.position[n]
    init_swarm[0] = parameters
    my_swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions, options=options, init_pos=init_swarm)
    
    #position are particles' parameters, while cost is the time on lap
    print("\nPSO..")
    my_swarm.pbest_pos = np.zeros(my_swarm.position.shape)
    my_swarm.best_pos = float("inf")
    my_swarm.pbest_cost = np.ndarray(shape=my_swarm.position.shape[0],buffer=np.ones((particlesNum)) * np.inf)
    my_swarm.best_cost = float("inf")
    for i in tqdm(range(iterations)):
        for particle in my_swarm.position:
            CostEvaluator.evaluateCostParticle(particle, paramsName)
            exit(0)
            
            #TODO: calcola costo della position

            # Part 1: If current position is less than the personal best,
            if f(current_position[particle]) < f(personal_best[particle]):
                # Update personal best
                personal_best[particle] = current_position[particle]
            # Part 2: If personal best is less than global best,
            if f(personal_best[particle]) < f(global_best):
                # Update global best
                global_best = personal_best[particle]
            # Part 3: Update velocity and position matrices
            update_velocity()
            update_position()
    pass

if __name__ == "__main__":
    psoHyperparams = {'c1':[0.6,1,1.5,1.75,2],
                      'c2':[0.6,1,1.5,1.75,2],
                      'w':[0.729]}
    seedsList = [1,2578,54,443]
    PSO_execution()