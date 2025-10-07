from nltk.stem import RSLPStemmer
import unidecode
import xml.etree.ElementTree as ET

# Inicializa o stemmer da língua portuguesa
stemmer = RSLPStemmer()

# Função que padroniza strings: lower case, sem acentos e sem espaços extras
def padronizar_string(string):
    if isinstance(string, str):
        return unidecode.unidecode(string.lower().strip())
    else:
        return str(string) if string is not None else ""

# Aplica stemmer a cada palavra de uma frase
def stem_frase(frase):
    frase_str = str(frase)  # garante que seja string
    return " ".join(stemmer.stem(w) for w in frase_str.split())

# Carrega XML e retorna a raiz; trata erros caso arquivo não exista ou não seja válido
def carregar_xml(caminho):
    try:
        tree = ET.parse(caminho)
        root = tree.getroot()
        return root
    except FileNotFoundError:
        print(f"\nErro: arquivo {caminho} não encontrado.")
        return None
    except Exception as e:
        print(f"\nErro ao processar {caminho}: {e}")
        return None

# Extrai achados (termos e categorias) de uma narrativa XML
def extrair_achados(root):
    achados = []
    if root is None:
        return achados  # Retorna lista vazia se XML não foi carregado
    for annotation in root.find('TAGS'):
        termo = padronizar_string(annotation.get('text'))
        categoria = annotation.get('tag')
        if termo != "":
            achados.append({"termo": termo, "categoria": categoria})
    return achados

# Cria dicionário de relações entre anotações do XML
def relacoes(root):
    relacaoDicionario = {}
    for rel in root.find('RELATIONS'):
        an1 = rel.get('annotation1')  # ID da anotação principal
        an2 = rel.get('annotation2')  # ID da anotação relacionada
        tipo = rel.get('reltype')     # Tipo de relação
        # Adiciona a relação à lista existente ou cria nova entrada
        if an1 in relacaoDicionario:
            relacaoDicionario[an1].append({'id_relacionado': an2, 'tipo_relacionamento': tipo})
        else:
            relacaoDicionario[an1] = [{'id_relacionado': an2, 'tipo_relacionamento': tipo}]
    return relacaoDicionario
