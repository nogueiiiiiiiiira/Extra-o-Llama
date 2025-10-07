import xml.etree.ElementTree as ET
from .processador_xml import padronizar_string

# Cria um dicionário com todas as relações entre anotações do XML
def relacoes(root):
    relacaoDicionario = {}
    for rel in root.find('RELATIONS'):
        an1 = rel.get('annotation1')  # ID da primeira anotação
        an2 = rel.get('annotation2')  # ID da segunda anotação
        tipo = rel.get('reltype')     # Tipo da relação
        # Adiciona a relação à lista existente ou cria nova entrada
        if an1 in relacaoDicionario:
            relacaoDicionario[an1].append({'id_relacionado': an2, 'tipo_relacionamento': tipo})
        else:
            relacaoDicionario[an1] = [{'id_relacionado': an2, 'tipo_relacionamento': tipo}]
    return relacaoDicionario

# Verifica se a tag é do tipo que desejamos extrair
def tagDesejada(tag):
    if "Diagnostic Procedure" in tag:
        return False  # Ignora procedimentos diagnósticos
    # Mantém apenas sinais/sintomas, doenças/síndromes ou localização corporal
    return (
        "Sign or Symptom" in tag
        or "Disease or Syndrome" in tag
        or "Body Location or Region" in tag
    )

# Analisa uma anotação e suas relações, retornando o texto final e se está negada
def dados_relacionados(dicionarioRelacao, id, root, dado):
    dadoFinal = ""
    verNegado = False

    # Obtém a anotação principal pelo ID
    anotacaoPrincipal = root.find(f".//annotation[@id='{id}']")
    if anotacaoPrincipal is None:
        return "", False  # Se não existir, retorna vazio

    tagPrincipal = anotacaoPrincipal.get('tag')

    # Ignora anotações diretamente ligadas a Diagnostic Procedure
    for key, value_list in dicionarioRelacao.items():
        for value in value_list:
            if id == value['id_relacionado']:
                anotRel = root.find(f".//annotation[@id='{key}']")
                if anotRel is not None and "Diagnostic Procedure" in anotRel.get('tag'):
                    return "", False

    # Ignora se a própria anotação for Diagnostic Procedure
    if "Diagnostic Procedure" in tagPrincipal:
        return "", False

    # Marca como negado se a tag principal contiver Negation
    if "Negation" in tagPrincipal:
        verNegado = True

    # Analisa relações normais e concatena textos relacionados
    for key, value_list in dicionarioRelacao.items():
        for value in value_list:
            if id == value['id_relacionado']:
                anotRel = root.find(f".//annotation[@id='{key}']")
                if anotRel is None:
                    continue
                tagRel = anotRel.get('tag')
                if "Diagnostic Procedure" in tagRel:
                    continue  # ignora relações com procedimentos diagnósticos
                if "Negation" in tagRel:
                    verNegado = True  # marca como negado se a relação indicar
                # Adiciona texto se a tag for desejada ou se for relação de negação
                if tagDesejada(tagRel) or value['tipo_relacionamento'] == 'negation_of':
                    relacao = padronizar_string(anotRel.get('text')) + " "
                    dadoFinal += relacao
                    if value['tipo_relacionamento'] == 'negation_of':
                        verNegado = True

    # Adiciona o texto da anotação principal ao final
    dadoFinal += dado
    return dadoFinal, verNegado
