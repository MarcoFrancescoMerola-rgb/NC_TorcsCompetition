import matplotlib.pyplot as plt
import numpy as np
#1.4_1.2_0.7298
#1_1.5_0.7298
iterationsDir = "./0Res/1.4_1.2_0.7298/iteraction.csv"  #"./results/solo/forza/215/iteraction.csv"
costDir = "./0Res/1.4_1.2_0.7298/costOverIteractions.csv"    #"./results/solo/forza/215/costOverIteractions.csv"
plotDir = "./0Res/"

def createPlot(xValues, yValues, plotDir):
    plt.plot(xValues, yValues, color='red', linestyle='solid', linewidth= 1)
    #plt.xticks(xValues)
    plt.xticks(np.arange(min(xValues), max(xValues), 5))
    ax = plt.gca()
    plt.xlabel('# iterations')
    plt.ylabel('cost')
    plt.title('Cost Over Iterations')
    #plt.setp(ax.get_xticklabels(), rotation=80, horizontalalignment='right')
    plt.savefig(plotDir+"plot.png")
    plt.close()

if __name__ == "__main__":
    
    xValues = [i for i in range(0,int(np.loadtxt(iterationsDir)))]
    yValues = np.loadtxt(costDir).tolist()
    createPlot(xValues, yValues, plotDir)