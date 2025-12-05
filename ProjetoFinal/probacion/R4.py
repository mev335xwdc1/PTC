import csv
import numpy as np
from funciones import ler_comunidades, ler_relacao_prov_cca, formatar_numero, file_comunidades,file_csv, file_relacao, anos, anos_variacion, file_saida_R4

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
    x = x.replace(".", "")
    x = x.replace(",", ".")
    try:
        return float(x)
    except:
        return 0.0

def main():
    print("A iniciar o processamento R4...")

    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
    except FileNotFoundError as e:
        print("ERRO: ficheiro HTML não encontrado:", e)
        return

    #inicializar dict de CCAA
    comunidades = {}
    for cod in dic_ccaa.keys():
        comunidades[cod] = {
            "nome": dic_ccaa[cod],
            "Hombres": np.zeros(8, dtype=float), # 8 anos (2017..2010)
            "Mujeres": np.zeros(8, dtype=float),
            "_has": False
        }

    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')

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
                
                #normalizar codigo (com zero à esquerda se necessário)
                cod_prov_z = cod_prov.zfill(2)

                homem_vals = [limpar_valor(x) for x in linha[9:17]]
                mulher_vals = [limpar_valor(x) for x in linha[17:25]]

                if not (len(homem_vals) == 8 and len(mulher_vals) == 8):
                    continue

                #identificar CCAA
                if cod_prov_z in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov_z]
                elif cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                elif cod_prov.lstrip("0") in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov.lstrip("0")]
                else:
                    continue

                if cod_ccaa in comunidades:
                    comunidades[cod_ccaa]["Hombres"] += np.array(homem_vals, dtype=float)
                    comunidades[cod_ccaa]["Mujeres"] += np.array(mulher_vals, dtype=float)
                    comunidades[cod_ccaa]["_has"] = True

    except FileNotFoundError:
        print("ERRO: ficheiro CSV não encontrado:", file_csv)
        return

    vari_abs = {}
    vari_rel = {}

    for cod, info in comunidades.items():
        if not info["_has"]: continue
        
        vari_abs[cod] = {"Hombres": [], "Mujeres": []}
        vari_rel[cod] = {"Hombres": [], "Mujeres": []}

        for sexo in ["Hombres", "Mujeres"]:
            arr = info[sexo]
            for Y in anos_variacion:
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

    #tabela
    html.append("<table>")
    html.append("<thead>")
    
    #linha 1: CCAA + Grandes Grupos
    html.append("<tr>")
    html.append("<th rowspan='3'>CCAA</th>")
    html.append("<th colspan='14'>Variación Absoluta</th>")
    html.append("<th colspan='14'>Variación Relativa (%)</th>")
    html.append("</tr>")

    #linha 2: Sexo
    html.append("<tr>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("<th colspan='7'>Hombres</th>")
    html.append("<th colspan='7'>Mujeres</th>")
    html.append("</tr>")

    #linha 3: Anos
    html.append("<tr>")
    #repetir os anos 4 vezes (Abs-Hom, Abs-Mul, Rel-Hom, Rel-Mul)
    for _ in range(4):
        for y in anos_variacion:
            html.append(f"<th>{y}</th>")
    html.append("</tr>")
    
    html.append("</thead>")
    html.append("<tbody>")

    #ordenar por codigo
    codigos_ccaa = sorted([c for c in comunidades.keys() if comunidades[c]["_has"]])

    for cod in codigos_ccaa:
        nome = comunidades[cod]["nome"]
        
        #recuperar listas de valores
        vh_abs = vari_abs[cod]["Hombres"]
        vm_abs = vari_abs[cod]["Mujeres"]
        vh_rel = vari_rel[cod]["Hombres"]
        vm_rel = vari_rel[cod]["Mujeres"]

        html.append(f"<tr><td class='left'>{cod} {nome}</td>")

        for v in vh_abs: html.append(f"<td>{formatar_numero(v)}</td>")
        for v in vm_abs: html.append(f"<td>{formatar_numero(v)}</td>")
        for v in vh_rel: html.append(f"<td>{formatar_numero(v)}</td>")
        for v in vm_rel: html.append(f"<td>{formatar_numero(v)}</td>")

        html.append("</tr>")

    html.append("</tbody></table>")

    #adicionar grafico 5
    html.append("<hr>")
    html.append("<h3>Evolución de la Población Total (Top 10 CCAA)</h3>")
    #o caminho é ../imagenes/R5.png porque o HTML está na pasta 'resultados'
    html.append("<img src='../imagenes/R5.png' alt='Gráfico R5'>")
    html.append("<br><br>")

    html.append("</div></body></html>")

    #gravar ficheiro
    try:
        with open(file_saida_R4, "w", encoding="utf-8") as f:
            f.write("\n".join(html))
        print("SUCESSO! Ficheiro gerado:", file_saida_R4)
    except Exception as e:
        print("ERRO ao gravar HTML:", e)

if __name__ == "__main__":
    main()
