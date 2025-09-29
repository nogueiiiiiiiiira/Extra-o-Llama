import os
import xml.etree.ElementTree as ET
import time
from utils.processar_llama import PesquisaClin_Llama, dividir_por_tamanho

def processar_xml(caminho_xml, llm, max_tokens_por_bloco=2000, sleep_sec=0.5):
    
    # processa um arquivo XML, extrai texto e aplica LLaMA em blocos.

    try:
        tree = ET.parse(caminho_xml)
        root = tree.getroot()

        texto = root.find(".//TEXT").text.strip()
        if not texto:
            print(f"XML {caminho_xml} sem conteúdo de texto.")
            return f"Erro: XML {caminho_xml} sem conteúdo de texto."

        paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
        blocos = []
        bloco_atual = ""
        for p in paragrafos:
            if len(bloco_atual) + len(p) < max_tokens_por_bloco * 4:
                bloco_atual += ("\n\n" + p) if bloco_atual else p
            else:
                blocos.append(bloco_atual)
                bloco_atual = p
        if bloco_atual:
            blocos.append(bloco_atual)

        respostas = []
        for i, bloco in enumerate(blocos, 1):
            print(f"\nProcessando bloco {i}/{len(blocos)} do XML...\n\n")
            resp = PesquisaClin_Llama(bloco, llm)
            respostas.append(resp)
            time.sleep(sleep_sec)

        texto_final = "\n".join(respostas)
        return texto_final

    except ET.ParseError as e:
        print(f"Erro ao parsear XML {caminho_xml}: {e}")
        return f"Erro ao parsear XML: {caminho_xml}"
    except Exception as e:
        print(f"Erro inesperado ao processar {caminho_xml}: {e}")
        return f"Erro inesperado ao processar {caminho_xml}: {e}"
