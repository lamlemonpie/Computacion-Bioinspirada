import numpy as np
import random
import math
import time
import datetime
import sys

def function(x,y):
    return -math.cos(x)*math.cos(y)*math.exp( -pow((x-math.pi),2)  -pow((y-math.pi),2) )

class Evolutivo:

    def __init__(self,function,populationSize,deviation,alpha,generations):
        self.function       = function
        self.populationSize = populationSize
        self.half           = self.populationSize//2
        self.deviation      = deviation
        self.alpha          = alpha
        self.generations    = generations
        self.min            = -10
        self.max            = 10


        self.population    = self.generatePopulation()
        self.deviations    = np.array([self.deviation]*self.populationSize)
        print("Población Inicial:\n", self.population )
        
        for i in range(self.generations):
            print("\nGENERACIÓN ", i+1)
            self.populationFit = self.fit(self.population)
            print("\nFitness:",self.populationFit)
            self.probability()
            print("\nMutaciones:\n")
            newPopulation,newDeviations = [],[]
            while(len(newPopulation) < self.populationSize ):
                bucle = True
                while (bucle):
                    parent          = self.roulette()
                    print("Ruleta:",parent)
                    child,deviation = self.mutate(parent)
                    bucle           = self.checkBoundaries(child)
                    if(bucle == True):
                        print("Mutación fuera de limites: ",child,"\nReintentando.")
                
                print("Mutado:", child)
                print("Desviacion:",deviation,"\n")
                newPopulation.append(child)
                newDeviations.append(deviation)

            newDeviations = np.array(newDeviations)
            newPopulation = np.array(newPopulation)
            newFit        = self.fit(newPopulation)
            #Elegimos los mejores (minimos) de la población nueva y de la nueva.
            oldBest = np.argsort(self.populationFit)[:self.half]
            oldBestPop = self.population[oldBest]
            oldBestDev = self.deviations[oldBest]

            newBest = np.argsort(newFit)[:self.half]
            newBestPop = newPopulation[newBest]
            newBestDev = newDeviations[newBest]

            self.population = np.concatenate( (oldBestPop,newBestPop) )
            self.deviations = np.concatenate( (oldBestDev,newBestDev) )

            print("Nueva Desviacion:\n",self.deviations)
            print("Nueva población:\n",self.population)

        self.fitness = self.fit(self.population)
        maximum = np.argsort(self.fitness)[-1]
        self.best = self.population[maximum]
        print("El minimo es: ", self.best, " con: ",self.fitness[maximum])
            

    def generatePopulation(self):
        return np.array([[np.random.uniform(self.min,self.max) for i in range(2)]for j in range(self.populationSize)])

    def fit(self,population):
        return np.array([self.function(vals[0],vals[1]) for vals in population])

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

    def mutate(self,parent):
        newDeviation = self.deviations[parent] *( 1 - self.alpha* np.random.normal(0,1) )
        print("Padre:",self.population[parent])
        child        = [ val + ( newDeviation*np.random.normal(0,1)) for val in self.population[parent]  ]
        return child,newDeviation

    #Si el gen está fuera de rango retorna True para volver a calcular nuevamente.
    def checkBoundaries(self,gen):
        for i in range(len(gen)):
            if( (gen[i] < self.min) or (gen[i] > self.max)):
                return True
        return False

    def normal(self,x,desvio):
        retorno = -0.5 * ( (x/desvio) * (x/desvio) )
        retorno = math.exp(retorno)
        retorno = retorno / ( desvio * math.sqrt( 2*math.pi ) )
        return retorno

    def valor_x(self,limInf,limSup,desvio,delta,aleatorio):
        area = 0
        auxSuma, aux = self.normal(limInf,desvio)
        i = limInf + delta
        while(i < limSup):
            auxSuma = self.normal(i,desvio)
            area    += (aux + auxSuma)

            if( (area * (delta/2)) > aleatorio ):
                return i
            aux = auxSuma
            i+= delta
            
        return -1*sys.maxsize


def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    gen      = Evolutivo(function,populationSize = 15,deviation = 0.3,alpha = 2,generations = 100)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

if __name__ == "__main__":
    main()