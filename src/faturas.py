import requests
import json
import os

# copy from login
COOKIE = os.getenv('COOKIE', '')

DATA_INICIO = os.getenv('DATA_INICIO', '2023-01-01')
DATA_FIM = os.getenv('DATA_FIM', '2023-12-31')

AMBITO_AQUISICAO_MAP_NIF = {
  '502011475': 'Outros',    #Modelo/Continente
  '500829993': 'Outros',    #Pingo doce
  '514038942': 'Outros',    #Mercadona
  '502607920': 'Outros',    #Auchan
  '501661654': 'Outros',    #pastelaria
  '221151303': 'Outros',    #frutaria
  '503933813': 'Outros',    #Portagens
  '500792615': 'Outros',    #Caixa Montepio,
  '500766681': 'Outros',    #Montepio,
  '502604751': 'Outros',    #Nos
  '514425253': 'Ginasios'   #Infesta
}

AMBITO_AQUISICAO = {
    'Restauracao': 'C03',
    'Cabeleireiro': 'C04',
    'Veterenario': 'C09',
    'PassePublico': 'C10',
    'Saude': 'C05',
    'Educacao': 'C06',
    'Imoveis': 'C07',
    'Lares': 'C08',
    'Outros': 'C99',
    'Ginasios': 'C11',
    'Jornais': 'C12'
}

def get_items(dataInicioFilter: str, dataFimFilter: str):
    url = f'https://faturas.portaldasfinancas.gov.pt/json/obterDocumentosAdquirente.action'
    params = {
        'dataInicioFilter': dataInicioFilter,
        'dataFimFilter': dataFimFilter,
        'estadoDocumentoFilter': 'P'
    }
    headers = {
        'Accept': 'application/json',
        'Cookie': COOKIE
    }

    r = requests.get(url, params=params, headers=headers)
    data = r.json()
    if(r.status_code != 200 or not data['success']):
        raise Exception('Failed to call get items!', r.status_code, r.text)

    items = data['linhas']
    total_items = data['totalElementos']
    print(f'Fetched {len(items)} items from a total of {total_items}')
    return items


def get_item_details(item):
    url = f'https://faturas.portaldasfinancas.gov.pt/detalheDocumentoAdquirente.action'
    params = {
        'idDocumento': item['idDocumento'],
        'dataEmissaoDocumento': item['dataEmissaoDocumento']
    }
    headers = {
        'Accept': 'text/html',
        'Cookie': COOKIE
    }
    # response payload is HTML, need to parse to get linhasDocument array
    r = requests.get(url, params=params, headers=headers)
    data = r.text

    match_str = 'dadosLinhasDocumento ='
    start_pos = data.index(match_str)
    # parse statement after array instantiation
    end_pos = data.index('Opensoft.', start_pos+1)
    linhas_document = data[start_pos+len(match_str):end_pos-1].strip()
    # remove trailing ';'
    linhas_document = linhas_document[:-1]  
    parsed_linhas_document = json.loads(linhas_document)
    return parsed_linhas_document


def update_item(item, linhas_document):
    nif_emitente = str(item['nifEmitente'])
    if AMBITO_AQUISICAO_MAP_NIF.get(nif_emitente) is None:
        print(f'NIF {item["nifEmitente"]} {item["nomeEmitente"]} not mapped')
        return
    
    url = f'https://faturas.portaldasfinancas.gov.pt/resolverPendenciaAdquirente.action'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': COOKIE
    }
    data = {
        'idDocumento': item['idDocumento'],
        'dataEmissaoDocumento': item['dataEmissaoDocumento'],
        'dataEmissaoDocumentoOriginal': item['dataEmissaoDocumento'],
        'linhasDocumento': linhas_document,
        'ambitoAquisicaoPend': AMBITO_AQUISICAO[AMBITO_AQUISICAO_MAP_NIF[nif_emitente]]
    }
    r = requests.post(url, data=data, headers=headers)
    if(r.status_code != 302):
        raise Exception('Failed to call update item!', r.status_code, r.text)


def process_item(item):
    try:
        linhas_document = get_item_details(item)
        update_item(item, linhas_document)
    except Exception as error:
        print(f'Error: {error}')


if __name__ == '__main__':
    items = get_items(dataInicioFilter=DATA_INICIO, dataFimFilter=DATA_FIM)

    list(map(lambda item: process_item(item), items))

    print(f'Finished processing {len(items)} items')