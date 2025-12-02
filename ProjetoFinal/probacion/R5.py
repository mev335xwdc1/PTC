import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
# Reutilizar as funções de leitura
from funciones import ler_comunidades, ler_relacao_prov_cca

def main():
    print("A iniciar R5 (Gráfico de Linhas)...")

    # 1. Caminhos
    file_comunidades = "entradas/comunidadesAutonomas.htm"
    file_relacao = "entradas/comunidadAutonoma-Provincia.htm"
    file_csv = "entradas/poblacionProvinciasHM2010-17.csv"
    file_imagem = "imagenes/R5.png"

    # 2. Carregar Dicionários
    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError:
        print("ERRO: Ficheiros HTML em falta.")
        return

    # 3. Ler CSV e Agrupar (Igual ao R2/R3)
    # Estrutura: 0-7 (Total), 8-15 (Homens), 16-23 (Mulheres)
    dados_agregados = {cod: np.zeros(24, dtype=float) for cod in dic_ccaa}

    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')
            for _ in range(2): next(leitor, None)
            
            for linha in leitor:
                if not linha or len(linha) < 2 or "Total Nacional" in linha[0] or "Notas" in linha[0]:
                    continue
                
                cod_prov = linha[0].split(" ")[0].strip()
                if cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                    try:
                        vals = []
                        for x in linha[1:25]:
                            limpo = x.replace(".", "")
                            if not limpo: limpo = 0
                            vals.append(float(limpo))
                        dados_agregados[cod_ccaa] += np.array(vals)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("ERRO: CSV não encontrado.")
        return

    # 4. Determinar Top 10 (Pela média do Total)
    ranking = []
    for cod, valores in dados_agregados.items():
        # Média dos índices 0 a 7 (Total 2017-2010)
        media = np.mean(valores[0:8])
        ranking.append((cod, media))
    
    # Ordenar decrescente e apanhar os 10 primeiros
    top_10 = sorted(ranking, key=lambda x: x[1], reverse=True)[:10]

    # 5. Preparar Gráfico
    # Os anos no CSV estão: 2017, 2016, ..., 2010
    anos_str = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]
    
    plt.figure(figsize=(10, 6))

    # Desenhar uma linha para cada comunidade do Top 10
    for cod, _ in top_10:
        nome = dic_ccaa[cod]
        valores_total = dados_agregados[cod][0:8] # Pegar apenas no bloco Total
        
        # O truque: Inverter a ordem para ficar 2010 -> 2017
        valores_cronologicos = valores_total[::-1]
        
        # Plotar a linha com marcadores ("o-")
        plt.plot(anos_str, valores_cronologicos, marker='o', label=nome)

    # 6. Configuração Visual
    plt.title("Población total en 2010-2017 (CCAA)")
    plt.ylabel("1e6") # Indicação de escala (milhões)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Legenda fora do gráfico (para não tapar as linhas, como no PDF)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout() # Ajusta tudo para caber na imagem

    # 7. Guardar
    plt.savefig(file_imagem)
    print(f"SUCESSO: Gráfico gerado em {file_imagem}")

if __name__ == "__main__":
    main()
