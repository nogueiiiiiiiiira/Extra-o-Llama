import openpyxl
import os
import json

# Função para carregar uma planilha Excel e retornar o workbook e a sheet desejada
def carregar_excel(caminho, sheet='Resultados'):
    wb = openpyxl.load_workbook(caminho)  # Abre o arquivo Excel
    ws = wb[sheet]  # Seleciona a aba desejada
    return wb, ws  # Retorna o workbook e a aba

# Função para salvar alterações feitas em um workbook Excel
def salvar_excel(wb, caminho):
    wb.save(caminho)  # Salva o arquivo no caminho especificado

# Função para carregar um dicionário salvo em arquivo JSON
def carregar_dicionario(caminho):
    if os.path.exists(caminho):  # Verifica se o arquivo existe
        with open(caminho, 'r', encoding='utf-8') as f:
            content = f.read().strip()  # Lê e remove espaços extras
            if content:  # Se o arquivo não estiver vazio
                return json.loads(content)  # Converte JSON para dicionário
    return {}  # Retorna dicionário vazio caso não exista ou esteja vazio

# Função para salvar um dicionário em arquivo JSON
def salvar_dicionario(dicionario, caminho):
    with open(caminho, 'w', encoding='utf-8') as f:
        # Salva o dicionário em formato JSON legível (indentado, com caracteres UTF-8)
        json.dump(dicionario, f, indent=4, ensure_ascii=False)
