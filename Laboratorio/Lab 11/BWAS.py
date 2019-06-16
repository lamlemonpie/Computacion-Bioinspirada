from prettytable import PrettyTable
import numpy as np
import secrets

import time
import datetime


class BWAS:
    def __init__(self,caminos,populationSize,alpha,betha,p,Q,pheroInit,initial,probMut,generations):
        #Variables del algoritmo
        self.caminos        = caminos
        self.populationSize = populationSize
        self.genotypeSize   = len(caminos[0])
        self.initial        = initial
        self.generations    = generations
        self.sameGlobal     = int(self.generations*(0.2)) #Porcenjate de iteraciones consecutivas para la busqueda estancada.
        #Constantes del algoritmo
        self.alpha     = alpha
        self.betha     = betha
        self.p         = p
        self.Q         = Q
        self.pheroInit = pheroInit
        self.probMut   = probMut

        self.bestFit   = float('inf') #Inicializamos el mejor con infinito.
        self.busqEstanq = 0 #Variable acumuladora de la búsqueda estancada.

        self.printTable("CAMINOS",self.caminos)
        self.dictionary    = self.generateDictionary()
        self.invDictionary = self.generateInverseDictionary()
        self.visibility    = self.generateVisibility(); self.printTable("VISIBILIDAD",self.visibility)
        self.pheromone     = self.generatePheromone();  self.printTable("FEROMONA INICIAL",self.pheromone)
        
        
        
        for i in range(self.generations):
            print("\nGENERACIÓN ",i+1,":")
            self.population    = np.array([ self.generatePath() for i in range(self.populationSize) ])
            self.populationFit = self.fitness(self.population)
            self.printTable("Población Generada",self.population,self.populationFit)
            self.checkBest()
            self.updatePheromone()
            self.printTable("FEROMONA",self.pheromone)
            mutated = self.mutatePheromone()
            self.printTable("FEROMONA MUTADA",self.pheromone)
            print("Se ha mutado {} feromonas".format(mutated))
               
            if(self.busqEstanq == self.sameGlobal): #Si es True, se concluye que el mejor global no cambió.
                print("Mejor global no ha cambiando por {} generaciones".format(self.sameGlobal))
                print("Se reiniciará la feromona")
                self.pheromone = self.generatePheromone() #Reiniciamos la feromona
                self.printTable("FEROMONA",self.pheromone)
                self.busqEstanq = 0
        
        self.printTable("Población final",self.population,self.populationFit)
        print("\nEl mejor global es: {} ({})".format(self.best,self.bestFit))


    def generateDictionary(self):
        return dict([(chr(65+i),i)  for i in range(self.genotypeSize)])

    def generateInverseDictionary(self):
        return dict([(i,chr(65+i))  for i in range(self.genotypeSize)])

    def fitness(self,population):
        fit = []
        for i in population:
            fi = 0
            for j in range(0,self.genotypeSize-1):
                fi+= self.caminos[self.dictionary[i[j]]][self.dictionary[i[j+1]]]
            fit.append(fi)
        return np.array(fit)

    def generatePheromone(self):
        return np.array([ [ 0 if i==j else self.pheroInit for j in range (len(self.caminos[0]))  ] for i in range( len(self.caminos[0]) ) ])

    # Nij = 1/Dij
    def generateVisibility(self):
        return np.array([[ 1/j if j!=0 else 0  for j in i] for i in self.caminos])

    def printTable(self,titulo,valores,fit = []):
        print("\n"+titulo)
        table = PrettyTable()
        if(len(fit) <= 0):
            for row in valores:
                table.add_row(row.round(decimals=6))
            print (table.get_string(header=False, border=True))
        else:
            table.field_names = ["Caminos","Fitness"]
            for i in range(len(valores)-1 ):
                table.add_row([valores[i],fit[i]])
            print (table.get_string(header=True, border=True))
    
    def printArcos(self,titulo,arcos):
        print("\n"+titulo)
        table = PrettyTable()
        table.add_row(arcos)
        print (table.get_string(header=False, border=True))

    def generatePath(self):
        path = self.initial
        notVisited = list(self.dictionary.keys())
        notVisited.remove(path)
        while(  len(notVisited) > 0  ):
            prob = []
            for j in notVisited:
                phero = self.pheromone[ self.dictionary[path[-1]]  ][ self.dictionary[j] ] ** self.alpha
                visiv = self.visibility[ self.dictionary[path[-1]] ][ self.dictionary[j] ] ** self.betha
                p = phero * visiv
                prob.append(p)

            prob  = np.array(prob)
            prob  = prob/sum(prob)
            prob  = np.cumsum(prob)
            index = self.choose(prob)
            new   = notVisited[index]
            path+= new
            notVisited.remove(new)

        return path

    def choose(self,prob):
        rand = np.random.uniform(0,1)
        for i in range(len(prob)):
            if (prob[i] > rand):
                return i

    def checkBest(self):
        localBest = self.populationFit.argmin()
        if( self.populationFit[localBest] < self.bestFit ):
            self.best    = self.population[localBest]
            self.bestFit = self.fitness([self.best])[0] 
            print("El nuevo mejor global es: {} ({})".format(self.best,self.bestFit))
            self.busqEstanq = 0 #Reiniciamos la busqueda estancada
        else:
            self.busqEstanq += 1 #Se mantiene y actualizamos la busqueda estancada.
            print("El mejor global se mantiene: {} ({})".format(self.best,self.bestFit))

    def getPaths(self,value):
        return [ value[i] + value[i+1] for i in range( len(value) - 1 ) ]

    def updatePheromone(self):
        self.pheromone = self.pheromone * ( 1 - self.p ) #evaporación de todas las feromonas
        localWorstIndx = self.populationFit.argmax()     #Obtenemos el peor local
        localWorst     = self.population[localWorstIndx]  
        print("El peor local es: {} ({})".format(localWorst,self.populationFit[localWorstIndx]))
        bestPaths      = self.getPaths(self.best)
        self.printArcos("Arcos del mejor global",bestPaths)
        worstPaths     = self.getPaths(localWorst)
        self.printArcos("Arcos del peor local",worstPaths)
        #Mejoramos la feromona de la mejor solución
        for k in bestPaths:
            ind1 = self.dictionary[k[0]]
            ind2 = self.dictionary[k[1]]
            self.pheromone[ind1][ind2] += self.Q/self.bestFit
            self.pheromone[ind2][ind1] += self.Q/self.bestFit
        
        #Eliminamos los arcos repetidos del bestPaths en el worstPaths
        worstPaths = [n for n in worstPaths if n not in bestPaths]
        self.printArcos("Arcos del peor local sin los arcos del mejor global",worstPaths)

        #Evaporación adicional para la feromona de la peor local.
        for k in worstPaths:
            ind1 = self.dictionary[k[0]]
            ind2 = self.dictionary[k[1]]
            self.pheromone[ind1][ind2] *= ( 1 - self.p )
            self.pheromone[ind2][ind1] *= ( 1 - self.p )

    def getUmbral(self,value):
        paths = self.getPaths(value)
        accum = 0
        for path in paths:
            ind1  = self.dictionary[path[0]]
            ind2  = self.dictionary[path[1]]
            accum += self.pheromone[ind1][ind2]
        
        return accum/(len(value))

    def mutatePheromone(self):
        mutated = 0
        umbral = self.getUmbral(self.best)
        for i in range( len( self.caminos[0] ) ):
            for j in range( i+1 , len( self.caminos[0] ) ):
                    rand = np.random.uniform(0,1)
                    if(rand < (self.probMut/100)):
                        phero = self.pheromone[i][j] + np.random.normal(0,umbral)
                        while(phero < 0):
                            phero = self.pheromone[i][j] + np.random.normal(0,umbral)
                        
                        self.pheromone[i][j] = phero
                        self.pheromone[j][i] = phero
                        mutated             += 1 
        return mutated

def main():
    # JICGHDBEAF , mejor.
    caminos = np.array([
                [0,12,3,23,1,5,23,56,12,11],
                [12,0,9,18,3,41,45,5,41,27],
                [3,9,0,89,56,21,12,48,14,29],
                [23,18,89,0,87,46,75,17,50,42],
                [1,3,56,87,0,55,22,86,14,33],
                [5,41,21,46,55,0,21,76,54,81],
                [23,45,12,75,22,21,0,11,57,48],
                [56,5,48,17,86,76,11,0,63,24],
                [12,41,14,50,14,54,57,63,0,9],
                [11,27,29,42,33,81,48,24,9,0]
                ])


    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    comienzo = time.time()
    bw       = BWAS(caminos = caminos, populationSize = 10,alpha=2,betha=1,p = 0.05,\
                    Q = 1,pheroInit = 0.1,initial="A",probMut = 20,generations = 100)
    final    = time.time()

    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)



if __name__ == '__main__':
    main()