from prettytable import PrettyTable
import math
import time
import datetime
import numpy as np

DEBUG = True

def log(s):
    if DEBUG:
        print (s)

def function1(x):
    return -math.cos(x[0])*math.cos(x[1])*math.exp( -pow(x[0]-math.pi,2) -pow(x[1]-math.pi,2) )

class AINET:
    def __init__(self, function,lowlim, highlim, populationSize, problemSize, numClones, numRandom, betha, min, generations):
        self.function          = function
        self.lowlim            = lowlim
        self.highlim           = highlim
        self.populationSize    = populationSize
        self.problemSize       = problemSize
        self.numClones         = numClones
        self.numRandom         = numRandom
        self.betha             = betha
        self.min               = min
        self.generations       = generations

        self.affinityThreshold = ( self.highlim - self.lowlim ) * 0.05
        self.maxIt             = 10

        self.best     = None
        self.infs     = ["-inf","inf"]
        self.bestCost = float( self.infs[self.min] )

        log("AffinityThreshold : ({} - {}) = {}".format(self.highlim,self.lowlim,self.affinityThreshold))
        self.population = self.generatePopulation(self.populationSize)
    
        for i in range(self.generations):
            log("\n"+"+"*70); log("GENERACIÓN {} DE {}:".format(i+1,self.generations))
            self.populationCost     = self.cost(self.population)
            self.populationCostNorm = self.normalize(self.populationCost)
            self.printTable("Población",self.population,self.populationCost,self.populationCostNorm)
            self.updateBest()
            self.populationCostAverage = np.average(self.populationCost)
            log("\nEl costo promedio es: {}".format(self.populationCostAverage))

            self.clonesCostAverage = float( self.infs[self.min] ) #valor infinito
            numIt = 0 #Cantidad de iteraciones para terminar el ciclo while si es que se estanca
            while( self.isWorseThan( self.clonesCostAverage, self.populationCostAverage ) and (numIt < self.maxIt) ):
                #Clones
                log("\nCreación de clones: Iteración {}".format(numIt))
                self.makeClones()
                numIt+=1
            
            self.printTable("Mejores Clones",self.clones,self.clonesCost)
            log("\nEl costo promedio es: {}".format( np.average(self.clonesCost) ))
            
            #Suprimimos de acuerdo al self.affinityThreshold
            clonesIndeces = self.suppressLowAffinityCells(self.clonesCost)
            self.clones   = self.clones[clonesIndeces]
            #Añadimos aleatorios
            random              = self.generatePopulation(self.numRandom)
            randomCost          = self.cost(random)
            self.clones         = np.concatenate( (self.clones,random) )
            self.clonesCost     = np.concatenate( (self.clonesCost,randomCost) )
            self.population     = self.clones
            self.populationCost = self.clonesCost
            self.clones         = None
            self.clonesCost     = None

        log("La mejor solución es {} ({})".format(self.best,self.bestCost))

    def generatePopulation(self,size):
        return  np.array( [ [ np.random.uniform(self.lowlim,self.highlim)  for j in range (self.problemSize) ] \
                                         for i in range (size) ] )

    def cost(self,population):
        return np.array( [ self.function(i) for i in population ] )

    def normalize(self,cost):
        max = cost.max()
        min = cost.min()
        diff = max - min
        return np.array( [ self.normFuct(min,max,diff,i) for i in cost  ] ) #normFunct1 o normFunct2


    def updateBest(self):
        localBest = self.localBest(self.populationCost)
        better    = self.isBetterThan( self.populationCost[localBest], self.bestCost )
        if (better):
            log("El mejor {} ({}) se actualiza a {} ({})".format(\
                    self.best,self.bestCost,self.population[localBest],self.populationCost[localBest] ))
            self.best     = self.population[localBest]
            self.bestCost = self.populationCost[localBest]
        else:
            log("El mejor {} ({}) se mantiene".format(self.best,self.bestCost))

    def makeClones(self):
        self.clones = []
        self.clonesCost = []
        for i in range( len(self.population) ):
            subClones = [] #Clones de cada elemento (subclones).
            for j in range (self.numClones):
                alpha = 1/self.betha * math.exp( -self.populationCostNorm[i] ) 
                clone = self.population[i] + ( alpha * np.random.normal(0,1) ) #Función de mutación
                subClones.append(clone)

            subClones     = np.array(subClones)
            subClonesCost = self.cost(subClones)
            localBest     = self.localBest(subClonesCost) #Calculamos el mejor subclon.
            self.printTable("Clones de {}".format(self.population[i]),subClones,subClonesCost)
            
            self.clones.append( subClones[localBest] ) #Añadimos el mejor subclon
            self.clonesCost.append( subClonesCost[localBest] )

        self.clones            = np.array(self.clones)
        self.clonesCost        = np.array(self.clonesCost)
        self.clonesCostAverage = np.average(self.clonesCost)
        log("\nEl costo promedio es: {}".format( self.clonesCostAverage ) )        

    def suppressLowAffinityCells(self,cost):
        #Calculamos afinidad.
        min = cost.min()
        max = cost.max()
        diff = max - min
        afinity = np.array( [  self.affinity(diff,i) for i in cost  ] )
        #No eliminados
        indeces = []
        for i in range (len (cost)):
            if( afinity[i] > self.affinityThreshold ):
                indeces.append(i)

        return indeces

    #------------------------------FUNCIONES DE SOPORTE----------------------------------------#
    #------------------------------------------------------------------------------------------#

    def affinity(self,diff,cost):
            return 1 - cost/(diff)
    
    def normFuct(self,min,max,diff,cost):
        return (cost - min)/diff

    def localBest(self,population):
        if self.min:
            return population.argmin()
        else:
            return population.argmax()

    def isWorseThan(self,val1, val2):
        if self.min:
            if val1 >= val2:
                return True
        else:
            if val1 <= val2:
                return True
        return False

    def isBetterThan(self,val1,val2):
        if self.min:
            if val1 < val2:
                return True
        else:
            if val1 > val2:
                return True
        return False


    #Dependiendo de la cantidad de soluciones,
    #haremos cabeceras de la tabla.
    def makeFields(self):
        fields = []
        for i in range(0,self.problemSize):
            field = "x"+str(i+1)
            fields.append(field)
        return fields

    def printTable(self,title,pop,cost,norm=[]):
        log("\n"+title)
        pops = lambda x: list(x) if (len(x)>1)  else list([x])
        table = PrettyTable()
        
        if( len(norm) > 0):
            table.field_names = ["#"] + self.makeFields() + ["Costo","Costo Norm"]
            for i in range(len(pop)):
                vals = [i+1]+pops(pop[i]) + [cost[i],norm[i]]
                table.add_row( vals )
        else:
            table.field_names = ["#"] + self.makeFields() + ["Costo"]
            for i in range(len(pop)):
                vals = [i+1]+pops(pop[i]) + [cost[i]]
                table.add_row( vals )

        log(table.get_string(header=True, border=True))


if __name__ == '__main__':
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    inmune   = AINET(function1,lowlim = -10, highlim = 10, populationSize = 5, problemSize = 2,\
                     numClones = 5, numRandom = 2, betha = 100, min = True, generations = 100)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)