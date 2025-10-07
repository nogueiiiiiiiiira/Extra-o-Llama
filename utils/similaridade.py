from .processador_xml import stem_frase
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Calcula similaridade entre dois textos usando TF-IDF e cosine similarity
def medir_similaridade(t1, t2):
    # Aplica stemmer para reduzir palavras à raiz
    doc1 = stem_frase(t1)
    doc2 = stem_frase(t2)

    # TF-IDF com stemmer
    vetorizador_radical = TfidfVectorizer()
    try:
        matriz_radical = vetorizador_radical.fit_transform([doc1, doc2])
        # Faz cosine similarity (1 se idênticos, 0 se totalmente diferentes) com stemmer)
        resultado_radical = cosine_similarity(matriz_radical[0:1], matriz_radical[1:2])[0][0]
    except ValueError:
        resultado_radical = 0.0  # Caso algum texto esteja vazio

    # TF-IDF sem stemmer (texto original)
    vetorizador = TfidfVectorizer()
    try:
        tfidf_matrix = vetorizador.fit_transform([t1, t2])
        # Cosine similarity entre os dois textos sem stemmer
        resultado = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        resultado = 0.0  # Caso algum texto esteja vazio

    # Retorna o valor máximo entre comparação com stemmer e sem stemmer
    return max(resultado_radical, resultado)
