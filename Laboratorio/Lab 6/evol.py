import numpy as np
import random
import math
import time
import datetime

def funct(x,y):
    return -math.cos(x)*math.cos(y)*math.exp( -pow((x-math.pi),2)  -pow((y-math.pi),2) )


class CompEvol:
    def __init__(self,funct,populationSize,deviation,lbda,generations):
        self.funct          = funct
        self.populationSize = populationSize
        self.generations    = generations
        self.deviation      = deviation
        self.delthaSigma    = 1/(math.sqrt(2*math.sqrt(self.populationSize)))
        self.lbda           = lbda
        self.xLow           = -10
        self.xHigh          = 10
        self.yLow           = -10
        self.yHigh          = 10

        self.population = self.generatePopulation()
        self.deviations = np.array([self.deviation]*self.populationSize)
        print("Población Inicial:\n", self.population )

        for i in range(self.generations):
            
            self.populationFit = self.fit(self.population)
            print("\nFitness:",self.populationFit)
            self.probability()

            newPopulation = []
            for i in range(lbda):
                print("\nLambda:",i+1)
                r1,r2   = self.roulette(),self.roulette()
                parent1 = self.population[r1]
                parent2 = self.population[r2]
                child1  = self.crossover(parent1,parent2)
                newdev  = self.newDeviation(self.deviations[r1],self.deviations[r2])
                child1,mutdev  = self.mutation(child1,newdev)
                newPopulation.append(child1)
                self.deviations = np.concatenate((self.deviations,mutdev))
            
            newPopulation        = np.array(newPopulation)
            newFitness           = self.fit(newPopulation)
            self.population      = np.concatenate((self.population,newPopulation))
            self.populationFit   = np.concatenate((self.populationFit,newFitness))
            self.deviations      = np.concatenate((self.deviations,newdev))
            sortIndeces          = np.argsort(self.populationFit)
            oldIndeces           = sortIndeces[-self.lbda:]
            print("\nSe eliminan:",self.population[oldIndeces])
            newIndeces           = sortIndeces[:-self.lbda]
            self.population      = self.population[newIndeces]
            self.deviations      = self.deviations[newIndeces]
            print("\nDeviations:",self.deviations)
            print("\nNueva población:", self.population)
            print("\nFitness:",self.fit(self.population))


        self.best = self.population[ np.argsort(self.fit(self.population))[0]  ]
        self.bestFit = self.fit(np.array([self.best]))
        print("El mejor:", self.best, " con fit:", self.bestFit)


    def generatePopulation(self):
        return np.array([[np.random.uniform(-10,10) for i in range(2)] for j in range(self.populationSize)])
    
    def fit(self,population):
        return np.array([ self.funct(i,j) for i,j in population])

    def probability(self):
        #Minimizamos complementando los valores al valor máximo
        prob = self.populationFit.max() - self.populationFit +1    
        prob = prob/sum(prob)
        print("Probabilidad:",prob)
        self.populationProb = np.cumsum(prob)
        print("Probabilidad acum:",self.populationProb)

    def roulette(self):
        rand = np.random.uniform(0,1)
        for i in range(0,self.populationSize):
            if (self.populationProb[i] > rand):
                return i

    def crossover(self,parent1,parent2):
        print("\nCruzamiento:")
        print("Padre 1: ", parent1, " -- ","Padre 2:",parent2)
        child1 = np.array([(1/2)*(i+j) for i,j in (parent1,parent2) ])
        print("Hijo 1: ", child1)
        return child1

    def newDeviation(self,deviation1,deviation2):
        return np.array( [math.sqrt(deviation1+deviation2)] )

    def mutation(self,child,deviation):
        deviation = deviation*np.exp(np.random.normal(0,self.delthaSigma))
        N = np.random.normal(0,deviation)[0]
        child1 = np.array([ i+N for i in child ])
        print("Hijo 1 Mutado:",child1)
        return child1,deviation

def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    #u + 1
    generaciones = 100
    comienzo = time.time()
    gen1      = CompEvol(funct,populationSize = 10,deviation = 0.3,lbda = 1,generations = generaciones)
    #u + lambda
    gen2     = CompEvol(funct,populationSize = 10,deviation = 0.3,lbda = 5,generations = generaciones)
    #u,lambda - lambda >= u
    gen3     = CompEvol(funct,populationSize = 10,deviation = 0.3,lbda = 20,generations = generaciones)
    final    = time.time()

    print("\n\nRESULTADOS:")
    print("u+1:\n Val:",gen1.best," fit:",gen1.bestFit)
    print("u+lambda:\n Val:",gen2.best," fit:",gen2.bestFit)
    print("u,lambda:\n Val:",gen3.best," fit:",gen3.bestFit)

    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)


if __name__ == "__main__":
    main()