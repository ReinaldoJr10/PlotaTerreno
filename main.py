import json, timeit, numpy as np, requests, asyncio, aiohttp, matplotlib.pyplot as plt, time
import ponto

def exportaModeloObj(Pontos:ponto.BauPontos):
    with open("modelo.obj", "w") as arq:
        aux=0
        for i in range(0,Pontos.getTamanhoI()):
            indI=Pontos.getTamanhoI()
            indJ=Pontos.getTamanhoJ(i)
            for j in range(0,indJ):
                if (i==(indI-1)) or (j==(indJ-1)):
                    break;
                else:
                    Pontos.geraTriangulos(arq,i,j,indI,indJ)

def PlotaSuperficie(x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()

def VetorizaLinhasFit(matriz,eixoX,eixoY):
    auxiliar = []
    for linha in matriz:
        p = np.polyfit(np.linspace(0, eixoX - 1, eixoX), linha, deg=4)
        auxiliar.append(p.tolist())
    return auxiliar


async def chamaApi(session, url, tempo=0):
    await asyncio.sleep(tempo/100)
    async with session.get(url) as resp:
        #print(tempo/2)
        #print("----")
        x = await resp.json()
        return x['results']


async def chamadasApi2(lat, long,eixoX,eixoY):
    async with aiohttp.ClientSession() as session:
        x = []
        y = []
        z = []
        chamadas = []
        urlBase = 'https://api.opentopodata.org/v1/aster30m?locations='
        acu = 0
        qtdBlocosChamadas = 0
        for i in range(0, eixoX):
            for j in range(0, eixoY):
                if acu == 100:
                    acu = 0
                    chamadas.append(asyncio.create_task(chamaApi(session, urlBase, qtdBlocosChamadas)))
                    qtdBlocosChamadas += 1
                    urlBase = 'https://api.opentopodata.org/v1/aster30m?locations='
                x.append(i)
                y.append(j)
                nBase = 90/3600
                urlBase = urlBase + f'|{lat + nBase * i},{long + nBase * j}'
                acu += 1
                if i + 1 == eixoX and j + 1 == eixoY:
                    chamadas.append(asyncio.ensure_future(chamaApi(session, urlBase, qtdBlocosChamadas)))
        dados = await asyncio.gather(*chamadas)
        for elementos in dados:
            for elemento in elementos:
                z.append(elemento['elevation'])
        print("q")
    return x, y, z

def MontaMatriz(lat, long,eixoX,eixoY):
    x, y, z = asyncio.run(chamadasApi2(lat, long,eixoX,eixoY))
    xNp = np.array(x).reshape((eixoX, eixoY))
    yNp = np.array(y).reshape((eixoX, eixoY))
    zNp = np.array(z).reshape((eixoX, eixoY))
    q1, q3 = np.percentile(zNp,[25, 75])
    iqr = q3 - q1
    zNormalizada = ((zNp-np.min(zNp))/(np.max(zNp)-np.min(zNp)))*100
    #print(zNormalizada)
    return xNp*10, yNp*10, zNormalizada

def SalvaInformacoes(dadosMatrizes, dadosFits):
    dados = {
        "matrizZ": dadosMatrizes[0][0].tolist(),
        "matrizZT": dadosMatrizes[0][1].tolist(),
        "matrizX": dadosMatrizes[0][2].tolist(),
        "matrizY": dadosMatrizes[0][3].tolist()
    }
    dados_json = json.dumps(dados)
    fits = {
        "fitZ": dadosFits[0][0],
        "fitZT": dadosFits[0][1]
    }
    # print(fits)
    fits_json = json.dumps(fits)

    with open("dados.json", "w") as arq:
        arq.write(dados_json)
    with open("fits.json", "w") as arq:
        arq.write(fits_json)
    print("Informacoes salvas!")
    return


def interpola2Vetores(vet1, vet2, valor):
    vetResNp = (vet1 * valor) + (vet2 * (1 - valor))
    return vetResNp


def interpolaVetorZ(vetZ, ind, valor, nIteracao, totalIteracao):
    if nIteracao == (totalIteracao-1):
        i=int(str(ind),2)
        return interpola2Vetores(vetZ[(i * 2)], vetZ[(i * 2) + 1], valor)
    else:
        return interpola2Vetores(interpolaVetorZ(vetZ,(ind*10)+0,valor,nIteracao+1,totalIteracao),interpolaVetorZ(vetZ,(ind*10)+1,valor,nIteracao+1,totalIteracao),valor)


# codigo principal
def main():
    # 1000 levam por volta de 3 segundos
    eixoX = eixoY = 20
    # numero de terrenos
    numE = 4
    # valor da interpolação
    valorInterp = 0.5

    start = timeit.default_timer()

    lat = 45.589270491935146
    long = -111.53715889768334
    vetTerrenos = []
    for x in range(0, 2 ** numE):
        vetTerrenos.append([lat + ((1 / 60) * x), long + ((1 / 60) * x)])
    dadosMatrizes = []
    dadosFits = []
    dadosZ=[]

    for terreno in vetTerrenos:
        xNp, yNp, zNp = MontaMatriz(terreno[0], terreno[1],eixoX,eixoY)
        dadosZ.append(zNp)
        zNpTransposta = np.transpose(zNp)
        dadosMatrizes.append([zNp, zNpTransposta, xNp, yNp])
        fit = VetorizaLinhasFit(zNp,eixoX,eixoY)
        fitTransposta = VetorizaLinhasFit(zNpTransposta,eixoX,eixoY)
        dadosFits.append([fit, fitTransposta])
        # print(dadosFits)

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    print("testando:")
    zFinal=interpolaVetorZ(dadosZ,0,valorInterp,0,numE)

    SalvaInformacoes(dadosMatrizes, dadosFits)
    #PlotaSuperficie(xNp, yNp, zNp)
    #PlotaSuperficie(xNp, yNp, zFinal)

    pontos=ponto.BauPontos(xNp,yNp,zFinal)
    exportaModeloObj(pontos)
    print("modelo obj criado")

main()

