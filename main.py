import json, timeit, numpy as np, requests, asyncio, aiohttp, matplotlib.pyplot as plt, time
from sklearn.linear_model import LinearRegression as lm

# 1000 levam por volta de 3 segundos
eixoX = eixoY =15

def PlotaSuperficie(x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x, y, z)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()

def VetorizaLinhasFit(matriz):
    auxiliar = []
    for linha in matriz:
        p = np.polyfit(np.linspace(0, eixoX - 1, eixoX), linha, deg=4)
        auxiliar.append(p.tolist())
    return auxiliar

async def chamaApi(session, url, tempo=0):
    await asyncio.sleep(tempo)
    async with session.get(url) as resp:
        print(tempo)
        print("----")
        x = await resp.json()
        return x['results']

async def chamadasApi2(lat, long):
    async with aiohttp.ClientSession() as session:
        vetor = []
        x = []
        y = []
        chamadas = []
        urlBase = 'https://api.opentopodata.org/v1/aster30m?locations='
        acu = 0
        qtdBlocosChamadas = 0
        for i in range(0, eixoX):
            for j in range(0, eixoY):
                if acu == 100:
                    acu = 0
                    chamadas.append(asyncio.ensure_future(chamaApi(session, urlBase, qtdBlocosChamadas)))
                    qtdBlocosChamadas += 1
                    urlBase = 'https://api.opentopodata.org/v1/aster30m?locations='
                x.append(i)
                y.append(j)
                if acu == 0 or (i == 0 and j == 0):
                    urlBase = urlBase + f'{lat + 0.001802 * i},{long + 0.001802 * j}'
                else:
                    urlBase = urlBase + f'|{lat + 0.001802 * i},{long + 0.001802 * j}'
                acu += 1
                if i + 1 == eixoX and j + 1 == eixoY:
                    chamadas.append(asyncio.ensure_future(chamaApi(session, urlBase, qtdBlocosChamadas )))
        dados = await asyncio.gather(*chamadas)
        for elementos in dados:
            print(len(elementos))
            for elemento in elementos:
                vetor.append(elemento['elevation'])
    return vetor, x, y

def MontaMatriz(lat, long):
    matriz, x, y = asyncio.run(chamadasApi2(lat, long))
    xNp = np.array(x).reshape((eixoX, eixoY))
    yNp = np.array(y).reshape((eixoX, eixoY))
    matrizNp = np.array(matriz).reshape((eixoX, eixoY))
    matrizNormalizada = matrizNp - matrizNp.mean()
    return matrizNormalizada, xNp, yNp

def SalvaInformacoes(dadosMatrizes,dadosFits):
    dados = {
        "matrizZ": dadosMatrizes[0][0].tolist(),
        "matrizZT": dadosMatrizes[0][1].tolist(),
        "matrizX": dadosMatrizes[0][2].tolist(),
        "matrizY": dadosMatrizes[0][3].tolist()
    }
    dados_json=json.dumps(dados)
    fits={
        "fitZ" : dadosFits[0][0],
        "fitZT": dadosFits[0][1]
    }
    print(fits)
    fits_json=json.dumps(fits)

    with open("dados.json", "w") as arq:
        arq.write(dados_json)
    with open("fits.json", "w") as arq:
        arq.write(fits_json)
    print("Informacoes salvas!")
    return

# codigo principal
start = timeit.default_timer()
terrenosLoc = [[45.589270491935146, -111.53715889768334]]
dadosMatrizes = []
dadosFits = []
for terreno in terrenosLoc:
    matrizNp, XNp, YNp = MontaMatriz(terreno[0], terreno[1])
    matrizNpTransposta = np.transpose(matrizNp)
    dadosMatrizes.append([matrizNp , matrizNpTransposta , XNp , YNp ])
    fit = VetorizaLinhasFit(matrizNp)
    fitTransposta = VetorizaLinhasFit(matrizNpTransposta)
    dadosFits.append([fit, fitTransposta])
    print(dadosFits)

stop = timeit.default_timer()
print('Time: ', stop - start)

SalvaInformacoes(dadosMatrizes,dadosFits)
z = matrizNp
#PlotaSuperficie(XNp, YNp, z)