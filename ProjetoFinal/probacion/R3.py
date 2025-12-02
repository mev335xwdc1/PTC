import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
from funciones import ler_comunidades, ler_relacao_prov_cca

def main():
    print("A iniciar o processamento R3 (Gráficos)...")

    # 1. Definição de ficheiros
    file_comunidades = "entradas/comunidadesAutonomas.htm"
    file_relacao = "entradas/comunidadAutonoma-Provincia.htm"
    file_csv = "entradas/poblacionProvinciasHM2010-17.csv"
    file_imagem = "imagenes/R3.png"

    # 2. Carregar Dados (Mesma lógica do R2)
    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError:
        print("Erro: Verifica se os ficheiros HTML estão na pasta 'entradas'.")
        return

    # Estrutura para somar: Chave=CodCCAA, Valor=Array Numpy (24 posições)
    # Índices 0-7: Total (2017-2010)
    # Índices 8-15: Homens (2017-2010)
    # Índices 16-23: Mulheres (2017-2010)
    dados_agregados = {cod: np.zeros(24, dtype=float) for cod in dic_ccaa}

    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')
            for _ in range(2): next(leitor, None) # Saltar cabeçalhos
            
            for linha in leitor:
                if not linha or len(linha) < 2 or "Notas" in linha[0] or "Total Nacional" in linha[0]:
                    continue
                
                cod_prov = linha[0].split(" ")[0].strip()
                if cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                    try:
                        # Ler valores das colunas 1 a 25
                        vals = [float(x.replace(".", "") if x.replace(".", "").strip() else 0) for x in linha[1:25]]
                        dados_agregados[cod_ccaa] += np.array(vals)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Erro: CSV não encontrado.")
        return

    # 3. Calcular Médias e Ordenar
    # Queremos o TOP 10 baseado na média da população TOTAL (2010-2017)
    lista_ranking = []

    for cod, valores in dados_agregados.items():
        # O Total está nos primeiros 8 índices (0 a 7)
        media_total = np.mean(valores[0:8])
        lista_ranking.append((cod, media_total))

    # Ordenar por média (decrescente) e pegar nos primeiros 10
    top_10 = sorted(lista_ranking, key=lambda x: x[1], reverse=True)[:10]

    # 4. Preparar dados para o Gráfico
    nomes_ccaa = []
    hombres_2017 = []
    mujeres_2017 = []

    for item in top_10:
        cod = item[0]
        # Recuperar o nome da CCAA
        nome = dic_ccaa[cod]
        # O enunciado pede nomes curtos nos eixos, vamos simplificar alguns se necessário
        # Mas vamos usar o nome do dicionário
        nomes_ccaa.append(nome)
        
        vals = dados_agregados[cod]
        # Hombres 2017 é a primeira coluna do bloco de homens (índice 8)
        hombres_2017.append(vals[8])
        # Mujeres 2017 é a primeira coluna do bloco de mulheres (índice 16)
        mujeres_2017.append(vals[16])

    # 5. Gerar o Gráfico com Matplotlib
    x = np.arange(len(nomes_ccaa))
    width = 0.35  # Largura das barras

    fig, ax = plt.subplots(figsize=(10, 6)) # Tamanho da figura
    
    # Criar as barras (Homens deslocados à esquerda, Mulheres à direita)
    rects1 = ax.bar(x - width/2, hombres_2017, width, label='Hombres', color='blue')
    rects2 = ax.bar(x + width/2, mujeres_2017, width, label='Mujeres', color='red')

    # Etiquetas e Títulos
    ax.set_ylabel('1e6') # Indicação de escala (milhões)
    ax.set_title('Población por sexo en el año 2017 (CCAA)')
    ax.set_xticks(x)
    ax.set_xticklabels(nomes_ccaa, rotation=90) # Rotação vertical como na imagem
    ax.legend()

    # Ajustar layout para não cortar os nomes em baixo
    plt.tight_layout()

    # Guardar
    plt.savefig(file_imagem)
    print(f"Gráfico guardado em: {file_imagem}")
    # plt.show() # Descomentar se quiseres ver a janela a abrir

if __name__ == "__main__":
    main()