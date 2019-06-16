from prettytable import PrettyTable
import numpy as np
import time
import datetime


class AntColonySystem:
    def __init__(self,caminos,populationSize,alpha,betha,p,Q,q0,fi,pheroInit,initial,generations):
        self.caminos        = caminos
        self.populationSize = populationSize
        self.genotypeSize   = len(caminos[0])
        self.initial        = initial
        self.generations    = generations

        self.alpha     = alpha
        self.betha     = betha
        self.p         = p
        self.Q         = Q
        self.q0        = q0
        self.fi        = fi
        self.pheroInit = pheroInit

        self.bestFit   = float('inf') #Inicializamos el mejor con infinito.

        self.dictionary = self.generateDictionary()
        self.invDictionary = self.generateInverseDictionary()
        self.pheromone  = np.array(self.generatePheromone())
        self.printTable("FEROMONA",self.pheromone)
        self.visibility = self.generateVisibility()
        self.printTable("VISIBILIDAD",self.visibility)

        for i in range (self.generations):
            print("\nGENERACIÓN ",i+1,":\n")
            self.population = np.array([ self.generatePath() for i in range(self.populationSize) ])
            print("Población:\n",self.population)
            self.populationFit = self.fitness(self.population)
            print("Fitness:\n",self.populationFit)
            #Actualizamos la mejor solucion.
            self.checkBest()
            #Actualizamos la feromona del mejor.
            self.updateBestPheromone()
            self.printTable("FEROMONA",self.pheromone)
            print("Mejor solución:",self.best,"con:",self.bestFit)

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
        return [ [ 0 if i==j else self.pheroInit for j in range (len(self.caminos[0]))  ] for i in range( len(self.caminos[0]) ) ]

    # Nij = 1/Dij
    def generateVisibility(self):
        return np.array([[ 1/j if j!=0 else 0  for j in i] for i in self.caminos])

    def printTable(self,titulo,valores):
        print(titulo)
        table = PrettyTable()
        for row in valores:
            table.add_row(row.round(decimals=6))
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

            prob = np.array(prob)
            prob = prob/sum(prob)
            prob = np.cumsum(prob)
            #Usando el q0:
            q = np.random.uniform(0,1)
            if q<=self.q0:
                index = prob.argmax() #Intensificación
                print("Elegimos la mejor probabilidad: ",end="")
            else:
                index = self.choose(prob)#Diversificación
                print("Elegimos por ruleta: ",end="")
            new = notVisited[index]
            print(new)
            path+= new
            notVisited.remove(new)

            #Actualizamos la feromona
            self.updatePheromone(path[-2],path[-1])
        print("\nSe generó: ",path,"\n")
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
            print("El nuevo mejor es: ", self.best, " con: ",self.bestFit)
        

    #Actualización online de la feromona.
    def updatePheromone(self,p1,p2):
        ind1 = self.dictionary[p1]
        ind2 = self.dictionary[p2]
        self.pheromone[ind1][ind2] = (1 - self.fi)*self.pheromone[ind1][ind2] + self.fi*(self.pheroInit)


    #Actualización offline de la feromona.
    def updateBestPheromone(self):
        paths = [ self.best[j]+self.best[j+1] for j in range( len(self.best) ) if j!= (len(self.best)-1 ) ]
        for k in paths:
            ind1 = self.dictionary[k[0]]
            ind2 = self.dictionary[k[1]]
            #self.pheromone[ind1][ind2] = self.p * self.pheromone[ind1][ind2] + (1-self.p)*self.Q/self.bestFit
            self.pheromone[ind1][ind2] =  self.pheromone[ind1][ind2] + self.Q/self.bestFit
            #self.pheromone[ind2][ind1] = self.p * self.pheromone[ind2][ind1] + (1-self.p)*self.Q/self.bestFit
            self.pheromone[ind2][ind1] =  self.pheromone[ind2][ind1] + self.Q/self.bestFit

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


    print("Los caminos:\n",caminos)

    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    comienzo = time.time()
    acs      = AntColonySystem(caminos = caminos, populationSize = 10,alpha=1,betha=1,p = 0.99,Q = 1,q0 = 0.7,fi = 0.05,pheroInit = 0.1,initial="A",generations = 100)
    final    = time.time()

    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)


if __name__ == '__main__':
    main()