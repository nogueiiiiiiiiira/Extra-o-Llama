import pandas as pd
import re
import nltk
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# baixar stemmer do NLTK (apenas primeira execução)
nltk.download('rslp')

stemmer = RSLPStemmer()

# pré-processamento de texto
def preprocess(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = re.sub(r'[^a-zà-ú0-9\s]', '', texto)  # remove pontuação
    palavras = texto.split()
    palavras_stem = [stemmer.stem(p) for p in palavras]
    return " ".join(palavras_stem)

# cálculo de similaridade semântica
def similaridade_semantica(texto1, texto2, limiar=0.7):
    corpus = [preprocess(texto1), preprocess(texto2)]
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(corpus)
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return sim >= limiar, sim

# processamento da narrativa para análise
def processar_narrativa_para_analise(narrativa, df_prompts, excel_resultados, pasta_xml, similaridade):
    registros = []
    df_filtrado = df_prompts[df_prompts['nomeNarrativa'] == narrativa]

    for _, linha in df_filtrado.iterrows():
        termo = str(linha['termo'])
        categoria = str(linha['categoria'])
        prompt = str(linha['textoPrompt'])
        abreviacao = str(linha['abreviacao'])
        sctid = str(linha['SCTID'])

        registros.append({
            "Narrativa": narrativa,
            "Prompt": prompt,
            "Categoria": categoria,
            "Termo": termo,
            "Abreviacao": abreviacao,
            "SCTID": sctid
        })
    return registros

# similaridade e atualização do Excel
def calcular_similaridade_e_atualizar_excel(excel_resultados, limiar=0.7):
    df = pd.read_excel(excel_resultados, sheet_name='Resultados')

    df['Similaridade'] = 0.0
    df['Classificacao'] = None  # 1 = VP, 0 = FP, -1 = FN

    for i, row in df.iterrows():
        resposta = str(row['Termo'])
        referencia = str(row['Prompt'])

        ok, sim = similaridade_semantica(resposta, referencia, limiar)
        df.at[i, 'Similaridade'] = round(sim, 4)

        if ok:
            df.at[i, 'Classificacao'] = 1  # VP
        else:
            df.at[i, 'Classificacao'] = 0  # FP (inicialmente)

    # Ajusta FN: referência que não apareceu em nenhuma resposta válida
    termos_validos = set(df.loc[df['Classificacao'] == 1, 'Prompt'])
    for i, row in df.iterrows():
        if row['Classificacao'] == 0 and row['Prompt'] not in termos_validos:
            df.at[i, 'Classificacao'] = -1  # FN

    df.to_excel(excel_resultados, index=False, sheet_name='Resultados')
    print("\n✅ Similaridade calculada e Excel atualizado.")

# cálculo de métricas
def calcular_metricas(excel_resultados):
    df = pd.read_excel(excel_resultados, sheet_name='Resultados')

    VP = sum(df['Classificacao'] == 1)
    FP = sum(df['Classificacao'] == 0)
    FN = sum(df['Classificacao'] == -1)

    try:
        VPP = VP / (VP + FP)
    except ZeroDivisionError:
        VPP = 0

    try:
        precisao = VP / (VP + FP)
    except ZeroDivisionError:
        precisao = 0

    try:
        recall = VP / (VP + FN)
    except ZeroDivisionError:
        recall = 0

    try:
        f1_score = 2 * (precisao * recall) / (precisao + recall)
    except ZeroDivisionError:
        f1_score = 0

    return VP, FP, FN, VPP, precisao, recall, f1_score
