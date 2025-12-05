import csv
import numpy as np
import os
# Importar funções do funciones.py
from funciones import ler_comunidades, ler_relacao_prov_cca, formatar_numero

def limpar_valor(x):
    """
    Converte string para float tratando separadores e notação científica.
    """
    x = x.strip()
    if x == "":
        return 0.0
    if 'E' in x or 'e' in x:
        try:
            return float(x)
        except:
            return 0.0
    # Remover ponto de milhar e trocar vírgula por ponto
    x = x.replace(".", "")
    x = x.replace(",", ".")
    try:
        return float(x)
    except:
        return 0.0

def main():
    print("A iniciar o processamento R4...")

    # Caminhos (ajustados para a tua estrutura de pastas)
    entradas = "entradas"
    resultados = "resultados"
    
    file_csv = os.path.join(entradas, "poblacionProvinciasHM2010-17.csv")
    file_comunidades = os.path.join(entradas, "comunidadesAutonomas.htm")
    file_relacao = os.path.join(entradas, "comunidadAutonoma-Provincia.htm")
    file_saida = os.path.join(resultados, "variacionComAutonomas.html")

    # 1. Ler mapas
    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError as e:
        print("ERRO: ficheiro HTML não encontrado:", e)
        return

    # 2. Inicializar dict de CCAA
    comunidades = {}
    for cod in dic_ccaa.keys():
        comunidades[cod] = {
            "nome": dic_ccaa[cod],
            "Hombres": np.zeros(8, dtype=float), # 8 anos (2017..2010)
            "Mujeres": np.zeros(8, dtype=float),
            "_has": False
        }

    # 3. Ler CSV e agregar por CCAA
    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')

            # Saltar cabeçalhos (2 a 4 linhas, depende do CSV, pomos 4 por segurança conforme o teu código)
            for _ in range(4):
                next(leitor, None)

            for linha in leitor:
                if not linha or len(linha) < 2 or "Notas" in linha[0]:
                    continue

                nome_completo = linha[0].strip()
                if "Total Nacional" in nome_completo:
                    continue

                partes = nome_completo.split(" ", 1)
                cod_prov = partes[0].strip()
                
                # Normalizar código (com zero à esquerda se necessário)
                cod_prov_z = cod_prov.zfill(2)

                # Colunas no CSV: 
                # Hombres: colunas 9 a 17 (exclusivo) -> 8 valores
                # Mujeres: colunas 17 a 25 (exclusivo) -> 8 valores
                h_raw = linha[9:17]
                m_raw = linha[17:25]

                h_vals = [limpar_valor(x) for x in h_raw]
                m_vals = [limpar_valor(x) for x in m_raw]

                if not (len(h_vals) == 8 and len(m_vals) == 8):
                    continue

                # Identificar CCAA
                if cod_prov_z in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov_z]
                elif cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                elif cod_prov.lstrip("0") in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov.lstrip("0")]
                else:
                    continue

                # Somar
                if cod_ccaa in comunidades:
                    comunidades[cod_ccaa]["Hombres"] += np.array(h_vals, dtype=float)
                    comunidades[cod_ccaa]["Mujeres"] += np.array(m_vals, dtype=float)
                    comunidades[cod_ccaa]["_has"] = True

    except FileNotFoundError:
        print("ERRO: ficheiro CSV não encontrado:", file_csv)
        return

    # 4. Calcular Variações
    # Anos dados: 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010
    # Variar: 2017-2016, ..., 2011-2010
    anos = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]
    anos_variacao = [2017, 2016, 2015, 2014, 2013, 2012, 2011]

    vari_abs = {}
    vari_rel = {}

    for cod, info in comunidades.items():
        if not info["_has"]: continue
        
        vari_abs[cod] = {"Hombres": [], "Mujeres": []}
        vari_rel[cod] = {"Hombres": [], "Mujeres": []}

        for sexo in ["Hombres", "Mujeres"]:
            arr = info[sexo]
            for Y in anos_variacao:
                idx = anos.index(Y)
                prev_idx = idx + 1
                
                if prev_idx < len(arr):
                    atual = float(arr[idx])
                    anterior = float(arr[prev_idx])
                    
                    abs_v = atual - anterior
                    rel_v = (abs_v / anterior * 100.0) if anterior != 0 else 0.0
                    
                    vari_abs[cod][sexo].append(abs_v)
                    vari_rel[cod][sexo].append(rel_v)
                else:
                    vari_abs[cod][sexo].append(0.0)
                    vari_rel[cod][sexo].append(0.0)

    # 5. Gerar HTML
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='es'>")
    html.append("<head>")
    html.append("<meta charset='utf-8'>")
    html.append("<title>Variacion Com. Autonomas</title>")
    html.append("""
    <style>
      body { font-family: Arial, sans-serif; color:#222; text-align: center;}
      h2 { margin-top:20px; }
      .container { width: 98%; margin: 10px auto; }
      table { border-collapse: collapse; width: 100%; font-size:11px; margin-bottom: 30px; }
      th, td { border: 1px solid #999; padding: 4px; text-align: center; vertical-align: middle; }
      th { background: #efefef; font-weight: bold; }
      td.left { text-align:left; padding-left:8px; font-weight: bold;}
      img { max-width: 90%; border: 1px solid #ccc; padding: 5px; box-shadow: 2px 2px 5px #ccc;}
    </style>
    """)
    html.append("</head><body>")
    html.append("<div class='container'>")
    html.append("<h2>Variación de población por Comunidades Autónomas (2011-2017)</h2>")

    # --- Tabela ---
    html.append("<table>")
    html.append("<thead>")
    
    # Linha 1: CCAA + Grandes Grupos
    html.append("<tr>")
    html.append("<th rowspan='3'>CCAA</th>")
    html.append("<th colspan='14'>Variación Absoluta</th>")
    html.append("<th colspan='14'>Variación Relativa (%)</th>")
    html.append("</tr>")

    # Linha 2: Sexo
    html.append("<tr>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("</tr>")

    # Linha 3: Anos
    html.append("<tr>")
    # Repetir os anos 4 vezes (Abs-Hom, Abs-Mul, Rel-Hom, Rel-Mul)
    for _ in range(4):
        for y in anos_variacao:
            html.append(f"<th>{y}</th>")
    html.append("</tr>")
    
    html.append("</thead>")
    html.append("<tbody>")

    # Ordenar por código
    codigos_ccaa = sorted([c for c in comunidades.keys() if comunidades[c]["_has"]])

    for cod in codigos_ccaa:
        nome = comunidades[cod]["nome"]
        
        # Recuperar listas de valores
        vh_abs = vari_abs[cod]["Hombres"]
        vm_abs = vari_abs[cod]["Mujeres"]
        vh_rel = vari_rel[cod]["Hombres"]
        vm_rel = vari_rel[cod]["Mujeres"]

        html.append(f"<tr><td class='left'>{cod} {nome}</td>")

        # Absoluta Hombres
        for v in vh_abs: html.append(f"<td>{formatar_numero(v)}</td>")
        # Absoluta Mujeres
        for v in vm_abs: html.append(f"<td>{formatar_numero(v)}</td>")
        # Relativa Hombres
        for v in vh_rel: html.append(f"<td>{formatar_numero(v)}</td>")
        # Relativa Mujeres
        for v in vm_rel: html.append(f"<td>{formatar_numero(v)}</td>")

        html.append("</tr>")

    html.append("</tbody></table>")

    # --- INSERÇÃO DO GRÁFICO R5 (Obrigatório) ---
    html.append("<hr>")
    html.append("<h3>Evolución de la Población Total (Top 10 CCAA)</h3>")
    # O caminho é ../imagenes/R5.png porque o HTML está na pasta 'resultados'
    html.append("<img src='../imagenes/R5.png' alt='Gráfico R5'>")
    html.append("<br><br>")

    html.append("</div></body></html>")

    # Gravar ficheiro
    try:
        with open(file_saida, "w", encoding="utf-8") as f:
            f.write("\n".join(html))
        print("SUCESSO! Ficheiro gerado:", file_saida)
    except Exception as e:
        print("ERRO ao gravar HTML:", e)

if __name__ == "__main__":
    main()
