# requests: Sends HTTP requests to get webpage content (used for static sites).
# beautifulsoup4: Parses and extracts HTML content (like tags, text, links).

import numpy as np
import csv
from funciones import formatar_numero, file_csv, file_saida_R1, anos

def main():
    print("A iniciar o processamento R1...")

    # dicionario para guardar séries temporais por província
    dados_prov = {}

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

                if "Total Nacional" in nome_completo:
                    cod_prov = "00"
                    nome_prov = "Total Nacional"
                else:
                    partes = nome_completo.split(" ", 1)
                    cod_prov = partes[0].strip()
                    nome_prov = partes[1].strip() if len(partes) > 1 else cod_prov

                try:
                    valores = []
                    for x in linha[1:9]:
                        x = x.strip().replace(".", "")
                        if x == "": x = "0"
                        valores.append(float(x))
                    
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

    loop_anos = range(2017, 2010, -1) 

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

    # Ordenar por código 
    for cod in sorted(dados_prov.keys()):
        nome = dados_prov[cod]["nome"]
        serie = dados_prov[cod]["totais"] 

        # Formatar o nome da primeira coluna
        display_nome = nome if cod == "00" else f"{cod} {nome}"

        html_body += f"<tr><td style='text-align:left; font-weight:bold;'>{display_nome}</td>"

        for ano in loop_anos:
            # Encontrar índices correspondentes na lista de dados original
            idx_atual = anos.index(ano)
            idx_anterior = idx_atual + 1 

            if idx_anterior < len(serie):
                val_atual = serie[idx_atual]
                val_anterior = serie[idx_anterior]
                
                #var = ano_atual - ano_anterior
                abs_v = val_atual - val_anterior
                
                #rel = (abs/ant) * 100
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

    # gravar Ficheiro
    try:
        with open(file_saida_R1, "w", encoding="utf-8") as f:
            f.write(html_header + html_body + html_footer)
        print(f"SUCESSO! Ficheiro gerado em: {file_saida_R1}")
    except Exception as e:
        print(f"ERRO: Não consegui gravar o ficheiro HTML: {e}")

if __name__ == "__main__":
    main()
