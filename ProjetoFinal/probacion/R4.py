import csv
import numpy as np
import os
from funciones import ler_comunidades, ler_relacao_prov_cca, formatar_numero

def limpar_valor(x):
    """
    Converte de forma robusta uma string do CSV INE para float.
    Trata notação científica (E), separadores de milhar '.' e vírgula decimal ','.
    Strings vazias -> 0.0
    """
    x = x.strip()
    if x == "":
        return 0.0
    # notação científica: não remover o ponto
    if 'E' in x or 'e' in x:
        try:
            return float(x)
        except:
            return 0.0
    # senão, remover separador de milhares e normalizar vírgula decimal
    x = x.replace(".", "")
    x = x.replace(",", ".")
    try:
        return float(x)
    except:
        return 0.0

def main():
    print("A iniciar o processamento R4...")

    entradas = "entradas"
    resultados = "resultados"
    os.makedirs(resultados, exist_ok=True)

    file_csv = os.path.join(entradas, "poblacionProvinciasHM2010-17.csv")
    file_comunidades = os.path.join(entradas, "comunidadesAutonomas.htm")
    file_relacao = os.path.join(entradas, "comunidadAutonoma-Provincia.htm")
    file_saida = os.path.join(resultados, "variacionComAutonomas.html")

    # Ler mapas
    try:
        dic_ccaa = ler_comunidades(file_comunidades)      # {codigo: nome}
        dic_mapa = ler_relacao_prov_cca(file_relacao)     # {cod_prov: cod_ccaa}
    except FileNotFoundError as e:
        print("ERRO: ficheiro HTML não encontrado:", e)
        return

    # Inicializar dict de CCAA com arrays para Hombres e Mujeres (8 anos: 2017..2010)
    comunidades = {}
    for cod in dic_ccaa.keys():
        comunidades[cod] = {
            "nome": dic_ccaa[cod],
            "Hombres": np.zeros(8, dtype=float),
            "Mujeres": np.zeros(8, dtype=float),
            "_has": False
        }

    # Ler CSV e agregar por CCAA (mesma lógica do R1)
    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')

            # Saltar as 4 linhas de cabeçalho (como no R1)
            for _ in range(4):
                next(leitor, None)

            for linha in leitor:
                if not linha:
                    continue
                if "Notas" in linha[0]:
                    continue

                nome_completo = linha[0].strip()
                if "Total Nacional" in nome_completo:
                    continue

                partes = nome_completo.split(" ", 1)
                cod_prov = partes[0].strip()
                nome_prov = partes[1].strip() if len(partes) > 1 else cod_prov

                # Normalizar código (tentar 2 dígitos)
                cod_prov_z = cod_prov.zfill(2)

                # Colunas: Hombres cols 9..16, Mujeres cols 17..24 (índices 9:17 e 17:25)
                h_raw = linha[9:17]
                m_raw = linha[17:25]

                h_vals = [limpar_valor(x) for x in h_raw]
                m_vals = [limpar_valor(x) for x in m_raw]

                if not (len(h_vals) == 8 and len(m_vals) == 8):
                    print(f"Aviso: linha ignorada (incompleta) -> {cod_prov} {nome_prov}")
                    continue

                # localizar código da CCAA (tentar com e sem zero à esquerda)
                if cod_prov_z in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov_z]
                elif cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                else:
                    alt = cod_prov.lstrip("0")
                    if alt in dic_mapa:
                        cod_ccaa = dic_mapa[alt]
                    else:
                        print(f"Aviso: província {cod_prov} não tem mapeamento para CCAA. Ignorada.")
                        continue

                # garantir existência no dict
                if cod_ccaa not in comunidades:
                    comunidades[cod_ccaa] = {
                        "nome": cod_ccaa,
                        "Hombres": np.zeros(8, dtype=float),
                        "Mujeres": np.zeros(8, dtype=float),
                        "_has": False
                    }

                comunidades[cod_ccaa]["Hombres"] += np.array(h_vals, dtype=float)
                comunidades[cod_ccaa]["Mujeres"] += np.array(m_vals, dtype=float)
                comunidades[cod_ccaa]["_has"] = True

    except FileNotFoundError:
        print("ERRO: ficheiro CSV não encontrado:", file_csv)
        return

    # Anos na ordem do CSV: [2017,2016,2015,2014,2013,2012,2011,2010]
    anos = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]
    anos_variacao = [2017, 2016, 2015, 2014, 2013, 2012, 2011]  # ordem 2017->2011 (esquerda->direita)

    # Calcular variações para cada CCAA e sexo
    vari_abs = {}  # vari_abs[cod][sexo] = list 7 vals (2017..2011)
    vari_rel = {}

    for cod, info in comunidades.items():
        if not info["_has"]:
            continue
        vari_abs[cod] = {"Hombres": [], "Mujeres": []}
        vari_rel[cod] = {"Hombres": [], "Mujeres": []}

        for sexo in ["Hombres", "Mujeres"]:
            arr = info[sexo]  # array length 8: [2017..2010]
            for Y in anos_variacao:
                idx = anos.index(Y)        # posição do ano Y no array
                prev_idx = idx + 1         # posição do ano anterior
                if prev_idx >= len(arr):
                    abs_v = 0.0
                    rel_v = 0.0
                else:
                    atual = float(arr[idx])
                    anterior = float(arr[prev_idx])
                    abs_v = atual - anterior
                    rel_v = (abs_v / anterior * 100.0) if anterior != 0 else 0.0
                vari_abs[cod][sexo].append(abs_v)
                vari_rel[cod][sexo].append(rel_v)

    # Construir HTML com a tabela única, com blocos conforme enunciado
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='es'>")
    html.append("<head>")
    html.append("<meta charset='utf-8'>")
    html.append("<title>variacionComAutonomas</title>")
    html.append("""
    <style>
      body { font-family: Arial, sans-serif; color:#222; }
      h2 { text-align:center; margin-top:20px; }
      .container { width: 98%; margin: 10px auto; }
      table { border-collapse: collapse; width: 100%; font-size:12px; }
      th, td { border: 1px solid #999; padding: 6px; text-align: center; vertical-align: middle; }
      th { background: #efefef; }
      td.left { text-align:left; padding-left:8px; }
      .block-title { background:#ddd; font-weight:bold; }
    </style>
    """)
    html.append("</head><body>")
    html.append("<div class='container'>")
    html.append("<h2>Variación de población por Comunidades Autónomas (2011-2017)</h2>")

    # Header: top row with big groups
    html.append("<table>")
    # First header row
    html.append("<thead>")
    html.append("<tr>")
    html.append("<th rowspan='3'>CCAA</th>")
    html.append(f"<th colspan='{7*1 + 0}'></th>")  # placeholder to align (we will build next rows properly)
    # We'll build the grouped headers below manually to ensure correct colspan:
    html.append("</tr>")

    # Build proper grouped header: one row with two big groups (Abs 14 cols, Rel 14 cols)
    # We'll close thead and create second/third header rows
    html.append("</thead>")

    # Now explicit header rows:
    # Row A: group headers
    html.append("<tr>")
    html.append("<th colspan='14'>Variación Absoluta</th>")
    html.append("<th colspan='14'>Variación Relativa (%)</th>")
    html.append("</tr>")

    # Row B: subgroups Hombres / Mujeres each 7 columns, repeated
    html.append("<tr>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("</tr>")

    # Row C: years 2017..2011 repeated 4 times
    html.append("<tr>")
    # First cell is header for rows (CCAA); we already have that as first column; insert nothing here
    # Actually we need to place the initial TH for CCAA in the first column; we already added earlier as rowspan but for clarity add now?
    # The above created no initial TH in rows B/C so ensure table layout consistent: the first TH for CCAA was created in the first thead row with rowspan=3.
    for _ in range(4):  # four blocks
        for y in anos_variacao:
            html.append(f"<th>{y}</th>")
    html.append("</tr>")

    # Start body
    html.append("<tbody>")

    # Order CCAA by code ascending (preserva ordem oficial)
    codigos_ccaa = sorted([c for c in comunidades.keys() if comunidades[c]["_has"]])

    for cod in codigos_ccaa:
        nome = comunidades[cod]["nome"]
        abs_h = vari_abs.get(cod, {}).get("Hombres")
        abs_m = vari_abs.get(cod, {}).get("Mujeres")
        rel_h = vari_rel.get(cod, {}).get("Hombres")
        rel_m = vari_rel.get(cod, {}).get("Mujeres")

        # garantir que existem séries completas
        if not (abs_h and abs_m and rel_h and rel_m):
            continue

        html.append(f"<tr><td class='left'><strong>{cod} {nome}</strong></td>")

        # Abs Hombres (2017..2011)
        for v in abs_h:
            html.append(f"<td>{formatar_numero(v)}</td>")

        # Abs Mujeres
        for v in abs_m:
            html.append(f"<td>{formatar_numero(v)}</td>")

        # Rel Hombres (percentagens)
        for v in rel_h:
            html.append(f"<td>{formatar_numero(v)}</td>")

        # Rel Mujeres
        for v in rel_m:
            html.append(f"<td>{formatar_numero(v)}</td>")

        html.append("</tr>")

    html.append("</tbody></table>")  # end table

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
