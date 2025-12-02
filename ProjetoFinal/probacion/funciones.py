import csv
from bs4 import BeautifulSoup

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