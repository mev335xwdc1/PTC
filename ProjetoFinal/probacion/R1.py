##O módulo "pandas" não pode ser utilizado (o tipo de dados dataframe é proibido) ATENÇÃO

#calcular la variación de la población por provincias desde el año 2011 a 2017

#Fichero poblacionProvinciasHM2010-17.csv contiene datos de la población por sexo y provincia desde el año 2010 a 2017.
# requests: Sends HTTP requests to get webpage content (used for static sites).
# beautifulsoup4: Parses and extracts HTML content (like tags, text, links).
# selenium: Automates browsers (needed for dynamic sites with JavaScript).
# lxml: A fast HTML/XML parser, useful for large or complex pages.
# schedule: Lets you run scraping tasks repeatedly at fixed intervals.
# pyautogui: Automates mouse and keyboard; useful when dealing with UI-based interactions.


#variacion_absoluta_ano = poblacion_ano - poblacion_ano_anterior
#variacion_relativa_ano = (variacion_absoluta_ano / poblacion_ano_anterior) * 100

import numpy as np
import csv
import sys
# Importar a função de formatação do ficheiro funciones.py
from funciones import formatar_numero

def main():
    print("A iniciar o processamento R1...")

    # 1. Caminhos
    file_csv = "entradas/poblacionProvinciasHM2010-17.csv"
    file_saida = "resultados/variacionProvincias.html"

    # 2. Dicionário para guardar séries temporais por província
    dados_prov = {}

    # 3. Ler CSV
    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')

            # Saltar cabeçalhos (normalmente 2 linhas são suficientes neste CSV)
            for _ in range(2): 
                next(leitor, None)

            for linha in leitor:
                # Ignorar linhas vazias ou notas de rodapé
                if not linha or len(linha) < 2 or "Notas" in linha[0]:
                    continue

                nome_completo = linha[0]

                # CORREÇÃO: No R1, o Total Nacional DEVE aparecer (veja-se imagem pág 2 do PDF)
                # Vamos atribuir o código "00" para que fique em primeiro lugar na ordenação
                if "Total Nacional" in nome_completo:
                    cod_prov = "00"
                    nome_prov = "Total Nacional"
                else:
                    # Extrair código e nome (ex: "02 Albacete")
                    partes = nome_completo.split(" ", 1)
                    cod_prov = partes[0].strip()
                    nome_prov = partes[1].strip() if len(partes) > 1 else cod_prov

                # --- Ler TOTAL 2017..2010 ---
                # No CSV, os totais estão nas colunas 1 a 9 (exclusivo) = 8 valores
                try:
                    valores = []
                    for x in linha[1:9]:
                        # Limpar dados (tirar pontos, espaços)
                        x = x.strip().replace(".", "")
                        if x == "": x = "0"
                        valores.append(float(x))
                    
                    # Se não tivermos 8 anos de dados, ignoramos a linha por segurança
                    if len(valores) == 8:
                        dados_prov[cod_prov] = {
                            "nome": nome_prov,
                            "totais": np.array(valores, dtype=float)
                        }
                except ValueError:
                    continue

    except FileNotFoundError:
        print(f"ERRO: ficheiro CSV não encontrado em {file_csv}")
        return

    # 4. Configuração dos Anos
    # A lista de dados lida do CSV está na ordem: [2017, 2016, 2015, ..., 2010]
    lista_anos_csv = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]

    # CORREÇÃO: O PDF pede ordem Decrescente (2017 -> 2011)
    loop_anos = range(2017, 2010, -1) 

    # 5. Gerar HTML
    html_header = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Variación de Población por Provincias</title>
    <style>
        table { border-collapse: collapse; width: 95%; margin: 20px auto; font-family: Arial, sans-serif; }
        th, td { border: 1px solid #ccc; padding: 6px; text-align: center; font-size: 12px; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .titulo { background-color: #e0e0e0; }
        h2 { text-align: center; color: #333; }
    </style>
</head>
<body>
    <h2>Variación de la Población por Provincias (2011-2017)</h2>

    <table>
        <thead>
            <tr>
                <th rowspan="2" class="titulo">Provincia</th>
"""
    # Gerar cabeçalhos dos Anos
    for ano in loop_anos:
        html_header += f'<th colspan="2" class="titulo">{ano}</th>'
    html_header += "</tr>\n<tr>"

    # Gerar sub-cabeçalhos (Abs/Rel)
    for ano in loop_anos:
        html_header += "<th>Abs</th><th>Rel (%)</th>"

    html_header += "</tr></thead><tbody>\n"

    html_body = ""

    # Ordenar por código (00 Total Nacional aparece primeiro, depois 01, 02...)
    for cod in sorted(dados_prov.keys()):
        nome = dados_prov[cod]["nome"]
        serie = dados_prov[cod]["totais"] # Array numpy com os dados [2017...2010]

        # Formatar o nome da primeira coluna
        display_nome = nome if cod == "00" else f"{cod} {nome}"

        html_body += f"<tr><td style='text-align:left; font-weight:bold;'>{display_nome}</td>"

        # Calcular variações para cada ano do loop
        for ano in loop_anos:
            # Encontrar índices correspondentes na lista de dados original
            idx_atual = lista_anos_csv.index(ano)
            idx_anterior = idx_atual + 1 # O ano anterior é o próximo na lista (ex: 2016 vem depois de 2017)

            if idx_anterior < len(serie):
                val_atual = serie[idx_atual]
                val_anterior = serie[idx_anterior]
                
                # Fórmula: Variação = Ano Atual - Ano Anterior
                abs_v = val_atual - val_anterior
                
                # Fórmula Relativa: (Absoluta / Anterior) * 100
                if val_anterior != 0:
                    rel_v = (abs_v / val_anterior) * 100
                else:
                    rel_v = 0.0
                
                html_body += f"<td>{formatar_numero(abs_v)}</td>"
                html_body += f"<td>{formatar_numero(rel_v)}</td>"
            else:
                html_body += "<td>-</td><td>-</td>"

        html_body += "</tr>\n"

    html_footer = """
        </tbody>
    </table>
</body>
</html>
"""

    # 6. Gravar Ficheiro
    try:
        with open(file_saida, "w", encoding="utf-8") as f:
            f.write(html_header + html_body + html_footer)
        print(f"SUCESSO! Ficheiro gerado em: {file_saida}")
    except Exception as e:
        print(f"ERRO: Não consegui gravar o ficheiro HTML: {e}")

if __name__ == "__main__":
    main()
