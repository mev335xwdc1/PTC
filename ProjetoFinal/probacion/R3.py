import numpy as np
import matplotlib.pyplot as plt
import csv
from funciones import file_comunidades, file_csv, file_relacao, file_saida_R3, ler_comunidades, ler_relacao_prov_cca

def main():
    print("A iniciar o processamento R3 (Gráficos)...")

    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError:
        print("Erro: Verifica se os ficheiros HTML estão na pasta 'entradas'.")
        return

    #chave=CodCCAA, Valor=Array (24 poscoes)
    #indices 0-7: Total (2017-2010)
    #indices 8-15: Homens (2017-2010)
    #indices 16-23: Mulheres (2017-2010)
    dados_agregados = {cod: np.zeros(24, dtype=float) for cod in dic_ccaa}

    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')
            for _ in range(2): next(leitor, None) 
            
            for linha in leitor:
                if not linha or len(linha) < 2 or "Notas" in linha[0] or "Total Nacional" in linha[0]:
                    continue
                
                cod_prov = linha[0].split(" ")[0].strip()
                if cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                    try:
                        #ler valores das colunas 1 a 25
                        vals = [float(x.replace(".", "") if x.replace(".", "").strip() else 0) for x in linha[1:25]]
                        dados_agregados[cod_ccaa] += np.array(vals)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Erro: CSV não encontrado.")
        return

    # calcular medias e ordenar
    #queremos o top 10 baseado na média da população TOTAL (2010-2017)
    lista_ranking = []

    for cod, valores in dados_agregados.items():
        # O Total está nos primeiros 8 índices
        media_total = np.mean(valores[0:8])
        lista_ranking.append((cod, media_total))

    #ordenar por media e usar os 10 primeiros
    top_10 = sorted(lista_ranking, key=lambda x: x[1], reverse=True)[:10]

    nomes_ccaa = []
    hombres_2017 = []
    mujeres_2017 = []

    for item in top_10:
        cod = item[0]
        #recuperar o nome da CCAA
        nome = dic_ccaa[cod]
        nomes_ccaa.append(nome)
        
        vals = dados_agregados[cod]
        #himens 2017 primeira coluna 8
        hombres_2017.append(vals[8])
        #mulheres 2017 orimeira coluna 16
        mujeres_2017.append(vals[16])

    #grafico matplotlib
    x = np.arange(len(nomes_ccaa))
    width = 0.35  #largura barras

    fig, ax = plt.subplots(figsize=(10, 6)) #tamnho da figura
    
    #criar barras homens e mulheres
    rects1 = ax.bar(x - width/2, hombres_2017, width, label='Hombres', color='blue')
    rects2 = ax.bar(x + width/2, mujeres_2017, width, label='Mujeres', color='red')

    ax.set_ylabel('1e6') #escalha em milhoes
    ax.set_title('Población por sexo en el año 2017 (CCAA)')
    ax.set_xticks(x)
    ax.set_xticklabels(nomes_ccaa, rotation=90) #rotacao vertical
    ax.legend()

    #n cortar nomes em baixo
    plt.tight_layout()

    plt.savefig(file_saida_R3)
    print(f"Gráfico guardado em: {file_saida_R3}")
    # plt.show() # Descomentar se quiseres ver a janela a abrir

if __name__ == "__main__":
    main()
