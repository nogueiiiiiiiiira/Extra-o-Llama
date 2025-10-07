from utils.processador_llama import PesquisaClin_Llama as gerar_resposta_local

# Função que verifica se um código SNOMED CT corresponde a um termo clínico
def prompt_avmap(codigo, termo):
    # Monta o prompt que será enviado ao modelo
    # Explica ao modelo como verificar o código SNOMED CT em relação ao termo
    prompt = f"""
        Dado um termo clínico em português e um código SNOMED CT (SCTID), determine a validade do código em relação ao termo.

        Responda apenas com um dos seguintes números:
        0 – O código SNOMED CT fornecido NÃO existe (nenhum resultado retornado);
        1 – O código existe, mas NÃO corresponde ao termo fornecido;
        2 – O código existe E corresponde corretamente ao termo fornecido.

        ### Dados fornecidos:
        Código SNOMED CT: {codigo}
        Termo em português: {termo}

        ### Instruções:
        - Acesse o navegador SNOMED CT pelo seguinte link:
        https://termbrowser.nhs.uk/?perspective=full&conceptId1={codigo}&edition=uk-edition&release=v20250604&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104
        - Verifique se o código retorna algum conceito (caso contrário, é 0).
        - Caso retorne um conceito, traduza o termo principal para o português e compare com o termo fornecido.
        - A comparação deve considerar correspondência clínica ou semântica (tradução precisa e direta).
        - Responda somente com o número correspondente: 0, 1 ou 2. Nenhuma explicação adicional.
        """
    # Envia o prompt para o modelo local e recebe a resposta
    resposta = gerar_resposta_local(prompt)
    for char in resposta:
        # Retorna o número como inteiro
        if char in "012":
            return int(char) 
    return 0 # Caso nenhum número válido seja encontrado, retorna 0 por padrão
