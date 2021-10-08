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
from printer import print as pt, jsonFileWriter, cleanJson, fromArrayToJson
import printer
import mail
import costOverIteractionsPlotter
import serializer
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
def PSO_execution(hyperparams,swarmParticles=10,iteractions=3,boundsRangePercentage=30):
    # swarm settings
    particlesNum = swarmParticles
    dimensions = 49
    iteractionNum = iteractions
    options = hyperparams
    stats = []
    stats_dir="0Res/"+f"{hyperparams['c1']}_{hyperparams['c2']}_{hyperparams['w']}/"

    # import parameters as json
    parameters = loadJsonParams(param_path)
    paramsName = [paramName for paramName in parameters.keys()]
    parameters = np.fromiter(parameters.values(), dtype=float)
    # convert json to numpy array
    array_param = np.zeros((1, dimensions))
    array_param[0] = parameters

    #bounds
    bounds = np.zeros((dimensions,2))
    lb = np.zeros(dimensions)
    ub = np.zeros(dimensions)

    variationPercentage = np.random.uniform(boundsRangePercentage[0],boundsRangePercentage[1])
    with open('test_parameters','r') as f:
        jsonBounds = json.load(f)
        print('Variation percentage: ',variationPercentage)
        for index,value in enumerate(jsonBounds.values()):
            lb[index] = value - ((float(value)/100) * variationPercentage)
            ub[index] = value + ((float(value)/100) * variationPercentage)
            #bounds[index] = (lb,ub)
    bounds = (lb,ub)

    # initialize swarm
    my_swarm= None
    init_swarm = np.zeros((particlesNum, dimensions))
    #action =  input('vuoi caricare le particelle salvate? [1]:si [0]:no\n')
    action = '0'
    if action == '0':
        print('creo nuove particelle')
        os.mkdir(stats_dir)
        for particle in range(particlesNum):
            for i in range(dimensions):
                tmplower = (100-variationPercentage)/100
                tmpupper = (100+variationPercentage)/100
                #init_swarm[particle][i] = parameters[i] * np.random.uniform(tmplower,tmpupper)
                init_swarm[particle][i] = np.random.uniform(lb[i],ub[i])
        my_swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions,
                        options=options,bounds=bounds,init_pos=init_swarm) #center=array_param
        #include default param
        my_swarm.position[0] = parameters
    if action == '1':
        print('carico le particelle salvate')
        init_swarm = np.loadtxt(stats_dir+'position.csv', delimiter=',')
        my_swarm = p.create_swarm(n_particles=particlesNum, dimensions=dimensions,
                        options=options,init_pos=init_swarm) #center=array_param

    #good for global best
    my_topology = Star()

    my_swarm.pbest_cost = np.ndarray(shape=my_swarm.position.shape[0],buffer=np.ones((particlesNum)) * np.inf)
    my_swarm.best_pos = np.zeros(shape=my_swarm.position.shape[1])
    my_swarm.current_cost = np.ndarray(shape=my_swarm.position.shape[0],buffer=np.ones((particlesNum)) * np.inf)
    statIterVal =0
    costOverIteractions = []
    if action == '1':
        my_swarm.velocity =     np.loadtxt(stats_dir+'velocity.csv', delimiter=',')
        my_swarm.pbest_cost=    np.loadtxt(stats_dir+'pbestcost.csv', delimiter=',')
        my_swarm.pbest_pos=     np.loadtxt(stats_dir+'pbestpos.csv', delimiter=',')
        my_swarm.best_cost=     np.loadtxt(stats_dir+'bestcost.csv', delimiter=',')
        my_swarm.best_pos=      np.loadtxt(stats_dir+'bestpos.csv', delimiter=',')
        my_swarm.current_cost = np.loadtxt(stats_dir+'current_cost.csv', delimiter=',')
        stats                 = np.loadtxt(stats_dir+'cost_stats.csv', delimiter=',').tolist()
        statIterVal           = int(np.loadtxt(stats_dir+'iteraction.csv', delimiter=','))
        costOverIteractions   = np.loadtxt(stats_dir+'costOverIteractions.csv', delimiter=',').tolist()

    for iteraction in range(statIterVal,iteractionNum):

        for index, particle in enumerate(my_swarm.position):
            pt(f"Executing combination: {hyperparams}")
            pt(f"Executing iteration: {iteraction+1} / {iteractionNum}")
            pt(f'Executing particle n.{index+1} / {particlesNum} evaluation...')
            particleScore = CostEvaluator.evaluateParticleCost(particle, paramsName)
            pt(f"score: {particleScore}")
            pt('--------------------------------------------------')
            # check if actual score is better then particle best position
            # if particleScore < my_swarm.pbest_cost[index]:
            #     pt(f"updating particle best position and cost... ({particleScore} < {my_swarm.pbest_cost[index]})")
            #     my_swarm.pbest_cost[index] = particleScore
            #     my_swarm.pbest_pos[index] = particle
            my_swarm.current_cost[index] = particleScore
        
        # updating pbest
        my_swarm.pbest_pos, my_swarm.pbest_cost = p.compute_pbest(my_swarm)
        # updating global score and position
        if np.min(my_swarm.pbest_cost) < my_swarm.best_cost:
            my_swarm.best_pos, my_swarm.best_cost = my_topology.compute_gbest(my_swarm)
            pt(f"bestCost: {my_swarm.best_cost}")
            pt(f"{my_swarm.best_pos}")
        # my_swarm.best_pos, my_swarm.best_cost = my_topology.compute_gbest(my_swarm)

        # TEST --------------------------
        # if i%2==0:
        #     print('my_swarm.best_cost: {:.4f}'.format(i+1, my_swarm.best_cost))

        costOverIteractions.append(my_swarm.best_cost)
        stats.append(my_swarm.best_cost)
        # swarm update
        my_swarm.velocity =  my_topology.compute_velocity(my_swarm,bounds=bounds)
        my_swarm.position =  my_topology.compute_position(my_swarm,bounds=bounds)
        pt('saving current swarm status...')        
        if(iteraction < iteractionNum):
            np.savetxt(stats_dir+'position.csv', my_swarm.position, delimiter=',')
            serializer.serialize(stats_dir+'position',my_swarm.position)

        np.savetxt(stats_dir+'velocity.csv', my_swarm.velocity, delimiter=',')
        np.savetxt(stats_dir+'pbestcost.csv', my_swarm.pbest_cost, delimiter=',')
        np.savetxt(stats_dir+'pbestpos.csv', my_swarm.pbest_pos, delimiter=',')
        np.savetxt(stats_dir+'bestcost.csv', [my_swarm.best_cost], delimiter=',')
        
        np.savetxt(stats_dir+'bestpos.csv', my_swarm.best_pos, delimiter=',')
        serializer.serialize(stats_dir+'bestpos',my_swarm.best_pos)
        # iterator = zip(paramsName, my_swarm.best_pos)
        # jsonParams = dict(iterator)
        # with open(stats_dir+'bestpos.json','w') as json_file:
        #     json.dump(jsonParams,json_file)

        np.savetxt(stats_dir+'current_cost.csv',my_swarm.current_cost, delimiter=',')
        np.savetxt(stats_dir+'cost_stats.csv', stats, delimiter=',')
        np.savetxt(stats_dir+'iteraction.csv', [iteraction+1], delimiter=',')
        np.savetxt(stats_dir+'costOverIteractions.csv', costOverIteractions, delimiter=',')
        fromArrayToJson(stats_dir,my_swarm.best_pos,paramsName)
    costOverIteractionsPlotter.createPlot([i for i in range(0,int(iteractionNum))],costOverIteractions,stats_dir)
    paramDict = dict(zip(paramsName, my_swarm.best_pos))
    lastParticles= my_swarm.position

    # TEST 2 -----------------------
    # print('The best cost found by our swarm is: {:.4f}'.format(my_swarm.best_cost))
    
    pt('--------------------------------------------------')
    particleScore = CostEvaluator.evaluateParticleCost(my_swarm.best_pos, paramsName)
    pt(f"global score: {particleScore}")
    pt('--------------------------------------------------')

    return my_swarm.best_pos, my_swarm.best_cost, paramDict, stats, lastParticles


if __name__ == "__main__":
    start_time = time.time()
    printer.cleanFile()
    # psoHyperparams = {'c1':[0.6,1,1.5,1.75,2],
    #                   'c2':[0.6,1,1.5,1.75,2],
    #                   'w':[0.729, 0.67]}

    # psoHyperparams = {'c1':[1.49618],
    #                   'c2':[1.49618],
    #                   'w':[0.7298]}


    # 1.2_1.5_0.7298
    # [0.6,1,1.2,1.49618]
    # [0.6,1.2,1.5,1.75]
    psoHyperparams = {'c1':[0.6,1,1.2],       # componente individuale
                      'c2':[0.6,1,1.2],       # componente sociale
                      'w':[0.7298]}     # componente inerziale

    # static seed for replication
    seedsList = [1258,54443,12455,675,456456,3435]
    seedIndex = 1294 #np.random.randint(0,len(seedsList))
    np.random.seed(seedIndex)
    #np.random.seed(456456)#seedsList[seedIndex])
    pt(f"active seed: {seedIndex}") #seedsList[seedIndex]}")
    posCost =[]
    swarmParticles = 20
    iteractions = 50
    boundsRangePercentage = (15,30)

    lastParticles =[]
    # creating hyperparameters combinations
    hCombinations = generateHyperparamsCombinations(psoHyperparams)
    for hyperparameters in hCombinations:
        # pt(f"Executing combination: {hyperparameters}")
        if hyperparameters == {'c1':0.6,'c2':1.2,'w':0.7298}:
            continue
        try:
            pos, cost, paramDict,stats, lastParticles=PSO_execution(hyperparameters,swarmParticles,iteractions,boundsRangePercentage)
            posCost.append((pos,cost,hyperparameters,paramDict,stats,lastParticles))
        except Exception as ex:
            pt(f"errore: {ex}")
    # selecting best position with it's cost,params and hyperparameters selected
    (bestPost,bestCost,hyperparameters,paramDict,stats,lastParticles)= min(posCost, key=  lambda t: t[1])
    
    pt(f"\nBest Position:\t{bestPost}")
    jsonFileWriter(paramDict)         #WRITE ON JSON
    pt(f"Best Cost:\t{bestCost}")
    pt(f"Hyperparamters:\t{hyperparameters}\n")
    execution_time = f"---------- {round((time.time() - start_time), 2)} seconds ----------" 
    pt("\n"+execution_time+"\n")
    with open('best_post','w')as f:
        f.write(str(bestPost))
    # with open('best_cost','w')as f:
    #     f.write(str(bestPost))
    with open('best_hyp','w')as f:
        f.write(str(hyperparameters))
    mail.sendEmail()
    exit(0)