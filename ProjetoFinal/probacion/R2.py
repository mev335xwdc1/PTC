import numpy as np
import csv
from funciones import file_comunidades, file_relacao, file_csv, file_saida_R2, ler_comunidades, ler_relacao_prov_cca, formatar_numero

def main():
    print("A iniciar o processamento R2...")

    #carregar os Dicionários 
    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
        print(f"Dicionários carregados. {len(dic_ccaa)} Comunidades encontradas.")
    except FileNotFoundError as e:
        print(f"ERRO CRÍTICO: Não foi possível encontrar um ficheiro: {e}")
        print("Verifica se a pasta 'entradas' existe e se os ficheiros têm a extensão correta (.htm).")
        return

    # 24 colunas de dados (8 anos total + 8 anos homens + 8 anos mulheres)
    dados_agregados = {}
    
    #inicializar arrays a zeros para cada CCAA
    for cod_ccaa in dic_ccaa:
        dados_agregados[cod_ccaa] = np.zeros(24, dtype=float)

    #ler CSV e Somar
    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')
            # Saltar linhas de cabeçalho irrelevantes (2 linhas)
            for _ in range(2): 
                next(leitor, None)
            
            for linha in leitor:
                #verificar se a linha tem dados suficientes, não é rodapé nem cabeçalho extra
                if not linha or len(linha) < 2 or "Notas" in linha[0]:
                    continue
                
                nome_completo = linha[0]
                #ignorar o Total Nacional neste exercício
                if "Total Nacional" in nome_completo:
                    continue
                
                #cod provincia (tipo 00)
                partes = nome_completo.split(" ")
                cod_prov = partes[0].strip()
                
                #somar as prov q encontramos a comunidade correta
                if cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                    
                    valores = []
                    try:
                        for x in linha[1:25]:
                            #tirar o . dos milhares e vazio por 0 antes de converter
                            val_limpo = x.replace(".", "")
                            if val_limpo.strip() == "": 
                                val_limpo = 0
                            valores.append(float(val_limpo))
                        
                        #passar para array e somar ao acumulador CCAA correspondente 
                        if cod_ccaa in dados_agregados:
                            dados_agregados[cod_ccaa] += np.array(valores, dtype=float)
                    except ValueError:
                        continue #ignora linhas com erros de conversão

    except FileNotFoundError:
        print(f"ERRO: Não encontrei o ficheiro CSV em {file_csv}")
        return

    html_header = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Población por Comunidades Autónomas</title>
    <style>
        table { border-collapse: collapse; width: 95%; margin: 20px auto; font-family: Arial, sans-serif; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; font-size: 12px; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .titulo { background-color: #e0e0e0; }
        h2 { text-align: center; color: #333; }
        .grafico-container { text-align: center; margin-top: 40px; margin-bottom: 40px; }
        img { max-width: 90%; height: auto; border: 1px solid #ddd; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h2>Población por Comunidades Autónomas (2010-2017)</h2>
    <table>
        <thead>
            <tr>
                <th rowspan="2" class="titulo">CCAA</th>
                <th colspan="8" class="titulo">Total</th>
                <th colspan="8" class="titulo">Hombre</th>
                <th colspan="8" class="titulo">Mujer</th>
            </tr>
            <tr>
                <th>2017</th><th>2016</th><th>2015</th><th>2014</th><th>2013</th><th>2012</th><th>2011</th><th>2010</th>
                <th>2017</th><th>2016</th><th>2015</th><th>2014</th><th>2013</th><th>2012</th><th>2011</th><th>2010</th>
                <th>2017</th><th>2016</th><th>2015</th><th>2014</th><th>2013</th><th>2012</th><th>2011</th><th>2010</th>
            </tr>
        </thead>
        <tbody>
"""
    
    html_body = ""
    # Ordenar pelas chaves (códigos) para manter a ordem oficial (01, 02, 03...)
    chaves_ordenadas = sorted(dic_ccaa.keys())

    for cod in chaves_ordenadas:
        nome = dic_ccaa[cod]
        dados = dados_agregados[cod]
        
        html_body += f"<tr>\n<td style='text-align:left; font-weight:bold;'>{cod} {nome}</td>"
        for val in dados:
            html_body += f"<td>{formatar_numero(val)}</td>"
        html_body += "\n</tr>"

    #rodapé com a imagem do R3 incorporada
    html_footer = """
        </tbody>
    </table>

    <hr>
    
    <div class="grafico-container">
        <h3>Gráfico R3: Población por sexo en 2017 (Top 10 CCAA)</h3>
        <img src="../imagenes/R3.png" alt="Gráfico de Población R3">
    </div>

</body>
</html>
"""

    #gravar o ficheiro
    try:
        with open(file_saida_R2, "w", encoding="utf-8") as f:
            f.write(html_header + html_body + html_footer)
        print(f"SUCESSO! Ficheiro gerado em: {file_saida_R2}")
    except FileNotFoundError:
        print("ERRO: Não consegui gravar o ficheiro. Verifica se a pasta 'resultados' existe.")

if __name__ == "__main__":
    main()
