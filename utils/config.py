import json
import os

def carregar_config(config_path='config.json'):
    
    # carrega a configuração do arquivo JSON, que serve para definir parâmetros do sistema 
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Configuração carregada de {config_path}")
        return config
    except FileNotFoundError:
        print(f"Arquivo de configuração não encontrado: {config_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        raise
