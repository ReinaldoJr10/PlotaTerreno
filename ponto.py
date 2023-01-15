import numpy as np
class ponto:
    x=0.0
    y=0.0
    z=0.0

    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

    def AtualizaCoordenadas(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def verticeString(self):
        return f'v {self.x} {self.y} {self.z} \n'

    def getXyz(self):
        return np.array([self.x,self.y,self.z])

class vetor:
    xyz=np.array([0.0,0.0,0.0])

    def __init__(self,p1:ponto,p2:ponto):
        self.xyz=p2.getXyz()-p1.getXyz()

    def getXYZ(self):
        return self.xyz

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

    def geraTriangulos(self, arq, i, j,sizeI,sizeJ):
        ind=j*2+(i*sizeJ)
        arq.write(self.getPonto(i,j).verticeString())
        arq.write(self.getPonto(i,j + 1).verticeString())
        arq.write(self.getPonto(i + 1,j + 1).verticeString())
        auxNormal1=self.calculaVetorNormal(self.getPonto(i,j), self.getPonto(i,j+1), self.getPonto(i+1,j+1))
        arq.write(f'vn {auxNormal1[0]} {auxNormal1[1]} {auxNormal1[2]}\n')
        arq.write(f'f -3//{ind+1} -2//{ind+1} -1//{ind+1}\n')
        #arq.write("f -3 -2 -1\n")
        arq.write(self.getPonto(i, j).verticeString())
        arq.write(self.getPonto(i + 1, j).verticeString())
        arq.write(self.getPonto(i + 1, j + 1).verticeString())
        auxNormal2 = self.calculaVetorNormal(self.getPonto(i, j), self.getPonto((i + 1), j), self.getPonto((i + 1), (j + 1)))
        arq.write(f'vn {auxNormal2[0]} {auxNormal2[1]} {auxNormal2[2]}\n')
        arq.write(f'f -3//{ind+2} -2//{ind+2} -1//{ind+2}\n')
        #arq.write("f -3 -2 -1\n")

    def calculaVetorNormal(self,pontoA:ponto,pontoB:ponto,pontoC:ponto):
        aux1=vetor(pontoA,pontoB)
        aux2=vetor(pontoA,pontoC)
        prodVet=np.cross(np.array(aux1.getXYZ()),np.array(aux2.getXYZ()))
        #print(prodVet)
        normal=(prodVet - np.min(prodVet)) / (np.max(prodVet) - np.min(prodVet))
        return normal

