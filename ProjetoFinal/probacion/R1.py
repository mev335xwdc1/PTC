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

            # Saltar as primeiras 4 linhas não relevantes
            for _ in range(4):
                next(leitor, None)

            for linha in leitor:

                # Ignorar linhas vazias ou cabeçalhos
                if not linha or "Notas" in linha[0]:
                    continue

                nome_completo = linha[0]

                # Ignorar Total Nacional
                if "Total Nacional" in nome_completo:
                    continue

                # Extrair código + nome (ex: "02 Albacete")
                partes = nome_completo.split(" ", 1)
                cod_prov = partes[0].strip()
                nome_prov = partes[1].strip() if len(partes) > 1 else cod_prov

                # --- Ler TOTAL 2017..2010 ---
                # São as colunas 1 a 8 (sempre 8 valores)
                raw_total = linha[1:9]

                valores = []
                for x in raw_total:
                    x = x.strip()
                    # Remover separadores de milhar
                    x = x.replace(".", "")
                    # números científicos tipo 4.6572132E7 são válidos em float()
                    if x == "":
                        x = "0"
                    try:
                        valores.append(float(x))
                    except ValueError:
                        print(f"Aviso: valor inválido em {cod_prov} {nome_prov}: '{x}', convertido para 0")
                        valores.append(0.0)

                # Precisa exatamente de 8 valores
                if len(valores) != 8:
                    print(f"Aviso: linha ignorada por dados incompletos: {cod_prov} {nome_prov}")
                    continue

                dados_prov[cod_prov] = {
                    "nome": nome_prov,
                    "totais": np.array(valores, dtype=float)
                }

    except FileNotFoundError:
        print("ERRO: ficheiro CSV não encontrado.")
        return

    # 4. Gerar variações (2011..2017)
    # Diferenças entre anos consecutivos
    # série[0] = 2017, série[7] = 2010  → diferença invertida?
    #
    # O CSV está em ordem: 2017, 2016, ..., 2010
    #
    # Para calcular
    #   Abs(2011) = ano2011 - ano2010
    # mas
    #   serie = [2017, 2016, 2015, ..., 2010]
    #
    # Portanto índice:
    #   2011 → série[6]
    #   2010 → série[7]
    #
    # Geral:
    #   dif_abs[ano] = serie[i] - serie[i+1]
    #
    # Vamos criar listas alinhadas com 2011..2017.

    # Índices dos anos na série TOTAL: 2017..2010
    anos = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]

    # Vamos produzir um HTML igual ao estilo de R2
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

    # Cabeçalho (anos 2011..2017)
    for ano in range(2011, 2018):
        html_header += f'<th colspan="2" class="titulo">{ano}</th>'
    html_header += "</tr>\n<tr>"

    for ano in range(2011, 2018):
        html_header += "<th>Abs</th><th>Rel (%)</th>"

    html_header += "</tr></thead><tbody>\n"

    # 5. Corpo da tabela
    html_body = ""

    # Ordenar por código da província
    for cod in sorted(dados_prov.keys()):
        nome = dados_prov[cod]["nome"]
        serie = dados_prov[cod]["totais"]  # [2017..2010]

        # Segurança
        if len(serie) != 8:
            print(f"Aviso: Série inválida para {cod} {nome}")
            continue

        html_body += f"<tr><td style='text-align:left; font-weight:bold;'>{cod} {nome}</td>"

        # Calcular para anos 2011..2017
        for ano in range(2011, 2018):
            idx_ano = anos.index(ano)      # posição do ano Y
            idx_prev = idx_ano + 1         # posição do ano Y-1

            if idx_prev >= len(serie):
                abs_v = 0
                rel_v = 0
            else:
                atual = serie[idx_ano]
                anterior = serie[idx_prev]
                abs_v = atual - anterior
                rel_v = (abs_v / anterior * 100) if anterior != 0 else 0

            html_body += f"<td>{formatar_numero(abs_v)}</td>"
            html_body += f"<td>{formatar_numero(rel_v)}</td>"

        html_body += "</tr>\n"

    html_footer = """
        </tbody>
    </table>

</body>
</html>
"""

    # 6. Gravar
    try:
        with open(file_saida, "w", encoding="utf-8") as f:
            f.write(html_header + html_body + html_footer)
        print("SUCESSO! Ficheiro gerado em:", file_saida)
    except:
        print("ERRO: não consegui escrever o ficheiro HTML.")

if __name__ == "__main__":
    main()