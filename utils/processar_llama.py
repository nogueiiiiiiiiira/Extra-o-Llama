from llama_cpp import Llama
from comando_llama.prompt import PROMPT_TEMPLATE

def dividir_por_tamanho(texto, max_chars=500):
    # divide o texto em blocos menores.
    
    blocos = []
    palavras = texto.split()
    bloco = ""
    for palavra in palavras:
        if len(bloco) + len(palavra) + 1 <= max_chars:
            bloco += (" " if bloco else "") + palavra
        else:
            blocos.append(bloco.strip())
            bloco = palavra
    if bloco.strip():
        blocos.append(bloco.strip())
    return blocos

def PesquisaClin_Llama(textoClinico, llm, max_tokens=500, temperature=0.7):
    
    # processa o texto clínico com LLaMA usando o prompt.
    prompt = PROMPT_TEMPLATE.format(textoClinico=textoClinico)
    
    try:
        result = llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
        return result["choices"][0]["text"].strip()
    except Exception as e:
        print(f"Erro na chamada LLaMA: {e}")
        return f"Erro na chamada LLaMA: {e}"
