import csv
from bs4 import BeautifulSoup
import os

#base directory = folder where funciones.py is located
base_dir = os.path.dirname(os.path.abspath(__file__))
projeto_dir = os.path.dirname(base_dir)

def caminho(rel_path):
    return os.path.join(projeto_dir, rel_path)

#ficheiros de entrada
file_csv = caminho("entradas/poblacionProvinciasHM2010-17.csv")
file_comunidades = caminho("entradas/comunidadesAutonomas.htm")
file_relacao = caminho("entradas/comunidadAutonoma-Provincia.htm")

#ficheiros de saida
file_saida_R1 = caminho("resultados/variacionProvincias.html")
file_saida_R2 = caminho("resultados/poblacionComAutonomas.html")
file_saida_R3 = caminho("imagenes/R3.png")
file_saida_R4 = caminho("variacionComAutonomas.html")
file_saida_R5 = caminho("imagenes/R5.png")

anos = [2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]
anos_variacion = anos[:-1]

def formatar_numero(numero):
    """
    Recebe um valor float e devolve uma string formatada 
    com separador de milhares (.) e decimais (,).
    Ex: 1234.56 -> "1.234,56"
    """
    try:
        val = float(numero)
        # Formata primeiro no estilo inglês (1,234.56)
        texto = "{:,.2f}".format(val)
        # Troca os caracteres para o estilo europeu
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(numero)

def ler_comunidades(ficheiro):
    """
    Lê o HTML de comunidades e devolve dicionário {codigo: nome}.
    Preserva a ordem de leitura.
    """
    dic_comunidades = {}
    # Tenta abrir com utf-8, se der erro tenta latin-1 (comum em ficheiros do INE)
    try:
        with open(ficheiro, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except UnicodeDecodeError:
        with open(ficheiro, 'r', encoding='latin-1') as f:
            soup = BeautifulSoup(f, 'html.parser')

    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            codigo = cols[0].get_text(strip=True)
            nome = cols[1].get_text(strip=True)
            # Verifica se o código é numérico para evitar cabeçalhos
            if codigo.isdigit(): 
                dic_comunidades[codigo] = nome
    return dic_comunidades

def ler_relacao_prov_cca(ficheiro):
    """
    Lê o HTML e devolve dicionário {codigo_provincia: codigo_ccaa}
    """
    dic_prov_ccaa = {}
    try:
        with open(ficheiro, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except UnicodeDecodeError:
        with open(ficheiro, 'r', encoding='latin-1') as f:
            soup = BeautifulSoup(f, 'html.parser')

    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        # Col 0 = Cod CCAA, Col 2 = Cod Provincia (segundo o enunciado/HTML)
        if len(cols) >= 3:
            cod_ccaa = cols[0].get_text(strip=True)
            # Por vezes o código da província está na coluna 2 ou 3, depende da formatação
            # No ficheiro fornecido: 
            # col[0]=CODAUTO, col[1]=NomeAut, col[2]=CPRO, col[3]=Provincia
            if len(cols) >= 3:
                cod_prov = cols[2].get_text(strip=True)
                if cod_prov.isdigit():
                    dic_prov_ccaa[cod_prov] = cod_ccaa
    return dic_prov_ccaa
