from prettytable import PrettyTable
import math
import time
import datetime
import numpy as np

DEBUG = True

def log(s):
    if DEBUG:
        print (s)

def function1(x,y):
    return -math.cos(x)*math.cos(y)*math.exp( -pow(x-math.pi,2) -pow(y-math.pi,2) )

def function2(x,y):
    return x+y

def function3(x,y):
    return x**2 + y**2

class CLONALG:
    def __init__(self,function,lowlim,highlim,populationSize,selectionSize,randomCellsNum,cloneRate,mutationFactor,generations):
        self.function       = function
        self.populationSize = populationSize
        self.selectionSize  = selectionSize
        self.randomCellsNum = randomCellsNum
        self.cloneRate      = cloneRate
        self.mutationFactor = mutationFactor
        self.generations    = generations

        self.best           = None
        self.bestEval       = None
        self.bestFit        = float("inf")

        self.stringSize     = 16
        self.lowlim         = lowlim
        self.highlim        = highlim

        self.cloneAmmount   = int(self.cloneRate*self.populationSize)

        self.population     = self.generatePopulation()
        
        for i in range(self.generations):
            log("\n"+"+"*70); log("GENERACIÓN {} DE {}:".format(i+1,self.generations))

            self.populationEval = self.evalPopulation(self.population)
            self.populationFit  = self.fitness(self.populationEval)
            self.populationAff  = self.affinity(self.populationFit)
            self.printTable("Población",self.population,self.populationEval,self.populationFit,self.populationAff)
            #Seleccionamos self.selectionSize elementos para clonar. (Peor fit = mayor costo)
            self.selectPopulation()
            self.printSelected("Se seleccionan {} elementos:".format(self.selectionSize))
            #Calculamos las tasas de mutación
            self.makeMutationRate()

            log("Clones para cada elemento seleccionado: ( {} x {} ) = {}".format(self.populationSize,self.cloneRate,self.cloneAmmount))
            
            self.makeClones()
            self.clonesEval = self.evalPopulation(self.clones)
            self.clonesFit  = self.fitness(self.clonesEval)
            self.printTable("Clones",self.clones,self.clonesEval,self.clonesFit)
            self.keepBestCosts(self.clones,self.clonesEval,self.clonesFit)
            self.printTable("Mejores entre población y clones",self.population,self.populationEval,self.populationFit)

            #Generamos valores aleatorios. 
            #Junto con la población, conservamos los de mejor costo.
            self.generateRandom()
            self.printTable("Aleatorios {}".format(self.randomCellsNum),self.randomPop,self.randomPopEval,self.randomPopFit)
            self.keepBestCosts(self.randomPop,self.randomPopEval,self.randomPopFit)
            self.printTable("Mejores entre población y aleatorios",self.population,self.populationEval,self.populationFit)

            #Actualizamos la mejor solución posible.
            self.updateBest()

        print("La mejor solución es {}({}) con costo {}".format(self.best,self.bestEval,self.bestFit))
        
    
    def generateString(self,size):
        string = ""
        for i in range(size):
            string+=str(np.random.randint(0,2))
        return string

    def generatePopulation(self):
        return np.array([ self.generateString(self.stringSize)  for i in range(self.populationSize)])

    #Generar flotantes apartir de un rango y un valor.
    def bitToFloat(self,x,min,max):
    	return min+(max - min)/(2.0**8 - 1.0)*x
    
    #Evaluamos el string binario y nos devuelve los dos valores flotantes.
    def evalString(self,string):
        one,two = string[:(self.stringSize//2)], string[(self.stringSize//2):]
        one,two = int(one,2),int(two,2)
        return [self.bitToFloat(one,self.lowlim,self.highlim),self.bitToFloat(two,self.lowlim,self.highlim)]

    def evalPopulation(self,population):
        return np.array([ self.evalString(i) for i in population  ])

    def fitness(self,population):
        return np.array([ self.function(i[0],i[1]) for i in population ])

    def affinity(self,fit):
        max = fit.max()
        min = fit.min()
        aff = []
        for i in range (self.populationSize):
            a = 1.0 - (fit[i])/(max-min)
            if(a>1):    a=1.0
            if(a <= 0): a=0.0
            aff.append(a)
        return np.array(aff)

    def selectPopulation(self):
        #ordered          = self.populationFit.argsort()            #Selecciono de acuerdo al fitness.
        #self.selectedPop = np.array(ordered[-self.selectionSize:]) #Los más altos.
        self.selectedPop = np.array([i for i in range(self.selectionSize)]) #Los primeros self.selectionSize (indices)

    def makeMutationRate(self):
        mutationRates = []
        for i in self.populationAff:
            mutationRates.append( math.exp(self.mutationFactor * i)  )
        self.mutationRates = np.array(mutationRates)

    def makeClone(self,pos):
        clone = ""
        for i in self.population[pos]:
            rand = np.random.uniform(0,1)
            if(rand < self.mutationRates[pos]):
                if(i == '0'): clone+= '1'
                else:         clone+= '0'
            else:
                clone+=i
        return clone

    def makeClones(self):
        clones = []
        for i in self.selectedPop:                  #A los seleccionados,
            for j in range(self.cloneAmmount):      #Se los clona self.cloneAmmount veces.
                clones.append( self.makeClone(i) )
        self.clones = np.array(clones)

    def keepBestCosts(self,pop,eval,fit):
        self.population     = np.concatenate( (self.population,pop) )
        self.populationEval = np.concatenate( (self.populationEval,eval) )
        self.populationFit  = np.concatenate( (self.populationFit,fit) )

        bestCostIndex       = self.populationFit.argsort()[:self.populationSize]
        self.population     = self.population[bestCostIndex]
        self.populationEval = self.populationEval[bestCostIndex]
        self.populationFit  = self.populationFit[bestCostIndex]


    def generateRandom(self):
        self.randomPop     = np.array([ self.generateString(self.stringSize)  for i in range(self.randomCellsNum)])
        self.randomPopEval = self.evalPopulation(self.randomPop)
        self.randomPopFit  = self.fitness(self.randomPopEval)
    
    def updateBest(self):
        localBest = self.populationFit.argmin()
        if( self.populationFit[localBest] < self.bestFit ):
            log("Se actualiza el mejor {}( {} ) a {}( {} )".format(self.population[localBest],self.populationFit[localBest],self.best,self.bestFit))
            self.best     = self.population[localBest]
            self.bestEval = self.populationEval[localBest]
            self.bestFit  = self.populationFit[localBest]
        else:
            log("Se mantiene el mejor {}( {} )".format(self.best,self.bestFit))

    def printTable(self,title,pop,eval,fit,afinity = []):
        log("\n"+title)
        table = PrettyTable()
        if( len(afinity) <= 0 ):
            table.field_names = ["#","Bits","x1","x2","Cost"]
            for i in range(len(pop)):
                vals = [i+1,pop[i],round(eval[i][0],4),round(eval[i][1],4),fit[i]  ]
                table.add_row( vals )
        else:
            table.field_names = ["#","Bits","x1","x2","Cost","Affinity"]
            for i in range(len(pop)):
                vals = [i+1,pop[i],round(eval[i][0],4),round(eval[i][1],4),fit[i],afinity[i]  ]
                table.add_row( vals )

        log(table.get_string(header=True, border=True))

    def printSelected(self,title):
        log("\n"+title)
        table = PrettyTable()
        table.field_names = ["#","Bits","x1","x2","Cost"]
        for i in self.selectedPop:
            vals = [i+1,self.population[i],round(self.populationEval[i][0],4),round(self.populationEval[i][1],4),self.populationFit[i]  ]
            table.add_row( vals )
        log(table.get_string(header=True, border=True))

def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    clones   = CLONALG(function1,lowlim = -10,highlim = 10, populationSize = 10, selectionSize = 5,randomCellsNum = 2, cloneRate = 0.25, mutationFactor = -2.5, generations = 100)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

if __name__ == '__main__':
    main()
    