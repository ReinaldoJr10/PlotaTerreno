import numpy as np
from numba import jit
class ponto:
    x=0.0
    y=0.0
    z=0.0

    def __init__(self,x,y,z):
        self.x=x
        self.y=z
        self.z=y

    def verticeString(self):
        return f'v {self.x} {self.y} {self.z} \n'

    def getXyz(self):
        return np.array([self.x,self.y,self.z])

class BauPontos:
    x=[]
    y=[]
    z=[]
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def getPonto(self,i,j):
        if(i<len(self.x) and j<len(self.x[i])):
            aux = ponto(self.x[i][j],self.y[i][j],self.z[i][j])
            return aux

    def getTamanhoI(self):
        return len(self.x)

    def getTamanhoJ(self,i):
        return len(self.x[i])


    def geraTriangulos(self, i,sizeJ,j):
        ind=(j*2)+(sizeJ)+1
        auxNormal1 = calculaVetorNormal(self.getPonto(i, j).getXyz(), self.getPonto(i, j + 1).getXyz(), self.getPonto(i + 1, j + 1).getXyz())
        auxNormal2 = calculaVetorNormal(self.getPonto(i, j).getXyz(), self.getPonto(i + 1, j).getXyz(), self.getPonto(i + 1, j + 1).getXyz())
        return "".join([self.getPonto(i,j).verticeString()+self.getPonto(i,j + 1).verticeString(),self.getPonto(i + 1,j + 1).verticeString(),f'vn {auxNormal1[0]} {auxNormal1[1]} {auxNormal1[2]}\nf -3//{ind} -2//{ind} -1//{ind}\n',self.getPonto(i,j).verticeString(),self.getPonto(i + 1,j).verticeString(),self.getPonto(i + 1,j + 1).verticeString(),f'vn {auxNormal2[0]} {auxNormal2[1]} {auxNormal2[2]}\nf -3//{ind+1} -2//{ind+1} -1//{ind+1}\n'])


def gTriangulo(args):
    p1,p2,p3,p4,ind=args
    auxNormal1 = calculaVetorNormal(p1.getXyz(), p2.getXyz(),p3.getXyz(),p4.getXyz())
    return "".join([p1.verticeString(), p2.verticeString(), p3.verticeString(),
                    f'vn {auxNormal1[0]} {auxNormal1[1]} {auxNormal1[2]}\nf -3//{ind} -2//{ind} -1//{ind}\n',
                    p1.verticeString(), p4.verticeString(), p3.verticeString(),
                    f'vn {auxNormal1[3]} {auxNormal1[4]} {auxNormal1[5]}\nf -3//{ind + 1} -2//{ind + 1} -1//{ind + 1}\n'])

@jit(nopython=True)
def calculaVetorNormal(pontoA,pontoB,pontoC,pontoD):
        prodVet=np.cross(pontoB-pontoA, pontoC-pontoA)
        prodVet2=np.cross(pontoD-pontoA, pontoC-pontoA)
        normal=prodVet/np.linalg.norm(prodVet)
        normal2 = prodVet2 / np.linalg.norm(prodVet2)
        normalF = np.array([normal[0],normal[1],normal[2],normal2[0],normal2[1],normal2[2]])
        return normalF