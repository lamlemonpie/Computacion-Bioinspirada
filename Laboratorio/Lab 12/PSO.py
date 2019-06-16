from prettytable import PrettyTable
import math
import time
import datetime
import numpy as np

def function(x,y):
    return x*math.sin(4*math.pi*x) - y*math.sin(4*math.pi*y + math.pi)+1


class PSO:
    def __init__(self,function,lowlim, highlim, fi1, fi2, populationSize, max, generations):
        self.function       = function
        self.lowlim         = lowlim
        self.highlim        = highlim
        self.fi1            = fi1
        self.fi2            = fi2
        self.populationSize = populationSize
        self.max            = True
        self.generations    = generations

        
        if(self.max): self.globalBestFit  = float('-inf')
        else:         self.globalBestFit  = float('inf')
        self.globalBest     = None

        self.localBestFit   = None
        self.localBest      = None

        #Inicio del algoritmo
        self.population = self.generatePopulation()
        self.velocities = self.generatePopulation()
        self.fitness()
        self.printTable("Particulas Iniciales",self.population,self.velocities,self.populationFit)
        for i in range(self.generations):
            print("\n"+"-"*20); print("Generación {} de {}".format(i+1,self.generations))
            self.getLocalBest()
            self.checkGlobalBest()
            self.calculateVelocities()
            self.updatePositions()
            self.fitness()
            self.printTable("Particulas Actualizadas",self.population,self.velocities,self.populationFit)

    def generatePopulation(self):
        return np.array([ [np.random.uniform(self.lowlim,self.highlim),np.random.uniform(self.lowlim,self.highlim)] for i in range(self.populationSize) ])
    
    def fitness(self):
        self.populationFit =  np.array( [ self.function(i[0],i[1]) for i in self.population ] )

    def getLocalBest(self):
        if( self.max ): localBest = self.populationFit.argmax()
        else:           localBest = self.populationFit.argmin()

        self.localBest    = self.population[localBest]
        self.localBestFit = self.populationFit[localBest]
        print("El mejor local es: ( {},{} ) -> ( {} )".format(self.localBest[0],self.localBest[1],self.localBestFit))

    def checkGlobalBest(self):
        if( self.max ): conditionBest = self.localBestFit > self.globalBestFit
        else:           conditionBest = self.localBestFit < self.globalBestFit

        if( conditionBest ):
            self.globalBest    = self.localBest
            self.globalBestFit = self.localBestFit
            print("El nuevo mejor global es: ( {}, {} ) -> ( {} )".format(self.globalBest[0],self.globalBest[1],self.globalBestFit))
        else:
            print("El mejor global se mantiene: ( {}, {} ) -> ( {} )".format(self.globalBest[0],self.globalBest[1],self.globalBestFit))
        

    def calculateVelocities(self):
        w = np.random.uniform(0,1) #Factor inercia nuevo por cada iteración
        for i in range( ( len( self.velocities ) ) ):
            for j in range( len( self.velocities[i] ) ):
                rand1 = np.random.uniform(0,1)
                rand2 = np.random.uniform(0,1)
                self.velocities[i][j] = ( w * self.velocities[i][j] ) + \
                                        ( self.fi1 * rand1 * ( self.localBest[j] - self.population[i][j] ) ) + \
                                        ( self.fi2 * rand2 * ( self.globalBest[j] - self.population[i][j] ) )

    def updatePositions(self):
        for i in range ( len( self.population ) ):
            for j in range ( len( self.population[i] ) ):
                tmp = self.population[i][j] + self.velocities[i][j] #Realizamos el calculo de actualización
                 #Si esta actualización sale del limite generamos aleatoriamente.
                if( ( tmp > self.highlim ) or ( tmp < self.lowlim ) ): 
                    tmp = np.random.uniform(self.lowlim,self.highlim)
                self.population[i][j] = tmp #Actualizamos particula.

    def printTable(self,titulo,pop,vel,fit):
        print("\n"+titulo)
        table = PrettyTable()
        table.field_names = ["#","x1","x2","v1","v2","Fitness"]
        
        for i in range(len(pop)):
            vals = [i+1, pop[i][0],pop[i][1],vel[i][0],vel[i][1],fit[i] ]
            table.add_row( vals )
        
        print (table.get_string(header=True, border=True))



def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    pso      = PSO(function, lowlim = -1, highlim = 2, fi1 = 2, fi2 = 2,\
                populationSize = 6, max=True, generations = 300)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

if __name__ == "__main__":
    main()