import numpy as np
import csv
import sys
# Importar as funções que criámos no funciones.py
from funciones import ler_comunidades, ler_relacao_prov_cca, formatar_numero

def main():
    print("A iniciar o processamento R2...")

    # 1. Definir os caminhos
    # Nota: Confirmámos que as extensões são .htm e o csv está na pasta entradas
    file_comunidades = "entradas/comunidadesAutonomas.htm"
    file_relacao = "entradas/comunidadAutonoma-Provincia.htm"
    file_csv = "entradas/poblacionProvinciasHM2010-17.csv"
    file_saida = "resultados/poblacionComAutonomas.html"

    # 2. Carregar os Dicionários (Mapas)
    try:
        dic_ccaa = ler_comunidades(file_comunidades)
        dic_mapa = ler_relacao_prov_cca(file_relacao)
        print(f"Dicionários carregados. {len(dic_ccaa)} Comunidades encontradas.")
    except FileNotFoundError as e:
        print(f"ERRO CRÍTICO: Não foi possível encontrar um ficheiro: {e}")
        print("Verifica se a pasta 'entradas' existe e se os ficheiros têm a extensão correta (.htm).")
        return

    # 3. Preparar Estrutura de Dados (Numpy)
    # 24 colunas de dados (8 anos Total + 8 anos Homens + 8 anos Mulheres)
    dados_agregados = {}
    
    # Inicializar arrays a zeros para cada CCAA
    for cod_ccaa in dic_ccaa:
        dados_agregados[cod_ccaa] = np.zeros(24, dtype=float)

    # 4. Ler CSV e Somar
    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=';')
            # Saltar linhas de cabeçalho irrelevantes (2 linhas)
            for _ in range(2): 
                next(leitor, None)
            
            for linha in leitor:
                # Verificar se a linha tem dados suficientes, não é rodapé nem cabeçalho extra
                if not linha or len(linha) < 2 or "Notas" in linha[0]:
                    continue
                
                nome_completo = linha[0]
                # O enunciado diz para ignorar o Total Nacional neste exercício
                if "Total Nacional" in nome_completo:
                    continue
                
                # O código da província são os primeiros caracteres (ex: "02 Albacete" -> "02")
                partes = nome_completo.split(" ")
                cod_prov = partes[0].strip()
                
                # Se encontrarmos a província no nosso mapa, somamos à comunidade correta
                if cod_prov in dic_mapa:
                    cod_ccaa = dic_mapa[cod_prov]
                    
                    valores = []
                    # Lemos as colunas 1 a 25 (exclusivo), que contêm os dados numéricos
                    try:
                        for x in linha[1:25]:
                            # Remove o ponto dos milhares (.) e troca vazio por 0 antes de converter
                            val_limpo = x.replace(".", "")
                            if val_limpo.strip() == "": 
                                val_limpo = 0
                            valores.append(float(val_limpo))
                        
                        # Converter para numpy array e somar ao acumulador da CCAA correspondente
                        if cod_ccaa in dados_agregados:
                            dados_agregados[cod_ccaa] += np.array(valores, dtype=float)
                    except ValueError:
                        continue # Ignora linhas com erros de conversão

    except FileNotFoundError:
        print(f"ERRO: Não encontrei o ficheiro CSV em {file_csv}")
        return

    # 5. Gerar HTML de Saída
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

    # Rodapé com a Imagem do R3 incorporada
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

    # Gravar o ficheiro
    try:
        with open(file_saida, "w", encoding="utf-8") as f:
            f.write(html_header + html_body + html_footer)
        print(f"SUCESSO! Ficheiro gerado em: {file_saida}")
    except FileNotFoundError:
        print("ERRO: Não consegui gravar o ficheiro. Verifica se a pasta 'resultados' existe.")

if __name__ == "__main__":
    main()