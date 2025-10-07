from comando_llama.prompt import PROMPT_TEMPLATE 

# Função que divide um texto em blocos que cabem na janela de contexto do modelo
def dividir_texto_por_prompt_seguro(texto, llm, prompt_template, max_tokens_saida=256):
    
    # Divide o texto em blocos que, combinados com o prompt, cabem na janela de contexto do modelo.
    n_ctx = llm.n_ctx()  # Obtém tamanho da janela de contexto do modelo
    tokens = llm.tokenize(texto.encode())  # Converte o texto em tokens
    blocos = []
    inicio = 0

    while inicio < len(tokens):
        fim = len(tokens)
        while fim > inicio:
            # Tenta criar um bloco que caiba na janela de contexto
            bloco_tokens = tokens[inicio:fim]
            bloco_texto = llm.detokenize(bloco_tokens).decode('utf-8', errors='ignore')
            prompt = prompt_template.format(textoClinico=bloco_texto)
            total_tokens = len(llm.tokenize(prompt.encode())) + max_tokens_saida
            if total_tokens <= n_ctx:
                blocos.append(bloco_texto)  # Adiciona bloco válido
                inicio = fim
                break
            fim -= 50  # Reduz tamanho gradualmente até caber
        else:
            # Se nem um pedaço grande couber, corta metade da janela disponível
            corte = (n_ctx - max_tokens_saida) // 2
            bloco_tokens = tokens[inicio:inicio + corte]
            bloco_texto = llm.detokenize(bloco_tokens).decode("utf-8", errors="ignore")
            blocos.append(bloco_texto)
            inicio += len(bloco_tokens)

    return blocos  # Retorna lista de blocos de texto seguros

# Função que processa o texto clínico usando LLaMA
def PesquisaClin_Llama(textoClinico, llm, max_tokens=256, temperature=0.7):
    
    # Processa o texto clínico com LLaMA, dividindo automaticamente em blocos que cabem na janela de contexto.
    respostas = []

    # Divide o texto em blocos seguros para não estourar a janela de contexto
    blocos = dividir_texto_por_prompt_seguro(
        textoClinico,
        llm,
        PROMPT_TEMPLATE,
        max_tokens_saida=max_tokens
    )

    # Processa cada bloco separadamente
    for i, bloco in enumerate(blocos):
        prompt = PROMPT_TEMPLATE.format(textoClinico=bloco)
        try:
            print(f"\n🔹 Processando bloco {i+1}/{len(blocos)} ({len(llm.tokenize(prompt.encode()))} tokens incluindo prompt)...")
            result = llm(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
            respostas.append(result["choices"][0]["text"].strip())  # Armazena resposta do bloco
        except Exception as e:
            print(f"\nErro na chamada LLaMA para bloco {i+1}: {e}")
            respostas.append(f"Erro na chamada LLaMA: {e}")

    return "\n".join(respostas)  # Junta todas as respostas em uma string
