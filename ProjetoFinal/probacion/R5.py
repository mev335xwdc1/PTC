import numpy as np
import matplotlib.pyplot as plt
import csv
from funciones import file_comunidades, file_relacao, file_csv, file_saida_R5, ler_comunidades, ler_relacao_prov_cca, anos

def main():
    print("A iniciar R5 (Gráfico de Linhas)...")

    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError:
        print("ERRO: Ficheiros HTML em falta.")
        return

    #ler csv
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

    #top 10 a partir da media 
    ranking = []
    for cod, valores in dados_agregados.items():
        media = np.mean(valores[0:8])
        ranking.append((cod, media))
    
    #prdenar top 10
    top_10 = sorted(ranking, key=lambda x: x[1], reverse=True)[:10]

    #grafico
    plt.figure(figsize=(10, 6))

    #linha para cada comunidade nno top 10
    for cod, _ in top_10:
        nome = dic_ccaa[cod]
        valores_total = dados_agregados[cod][0:8] #usar apenas TOTAL
        
        #inverter a ordem 2010->2017
        valores_cronologicos = valores_total[::-1]
        
        #plotar a linha com marcadores ("o-")
        plt.plot(anos, valores_cronologicos, marker='o', label=nome)

    #configuração visual
    plt.title("Población total en 2010-2017 (CCAA)")
    plt.ylabel("1e6") 
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout()

    #guardar
    plt.savefig(file_saida_R5)
    print(f"SUCESSO: Gráfico gerado em {file_saida_R5}")

if __name__ == "__main__":
    main()
