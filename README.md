# Extração e Avaliação de Termos Clínicos

Este projeto automatiza o processamento de narrativas clínicas em formato XML, utilizando o modelo de linguagem LLaMA para extrair termos médicos relevantes (sinais, sintomas, doenças e síndromes). Em seguida, compara os resultados com anotações gold standard, realiza análise de similaridade semântica, mapeia os termos para códigos SNOMED CT e calcula métricas de avaliação como precisão, recall e F1-Score.

## Pré-requisitos

- **Python**: Versão 3.8 ou superior.
- **Memória RAM**: Mínimo 8 GB (recomendado 16 GB para textos longos).
- **GPU**: Opcional, com suporte a CUDA para aceleração (reduz tempo de processamento).
- **Espaço em disco**: Aproximadamente 5 GB para o modelo LLaMA.

### Notas Técnicas sobre o Modelo LLaMA
O LLaMA processa texto em "tokens" (unidades como palavras ou fragmentos). Cada modelo tem um limite de contexto (máximo de tokens por vez). Para evitar erros em textos longos, o código divide automaticamente o conteúdo em partes menores. Isso garante compatibilidade com hardware limitado. O processamento pode ser lento; ajuste parâmetros como `n_ctx` e `max_tokens` para otimizar. Para modelos superiores, baixe via Hugging Face e atualize o caminho em `main.py`.

## Instalação

1. Baixe e instale Python 3.8+: [Site oficial](https://www.python.org/downloads/).
2. Instale a CLI do Hugging Face: `pip install huggingface_hub`.
3. Clone este repositório.
4. Instale as dependências: `pip install -r requirements.txt`.
5. Baixe o modelo LLaMA: Execute `huggingface-cli download hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF --include "llama-3.2-3b-instruct-q4_k_m.gguf" --local-dir ./modelo/`.
6. Coloque os arquivos XML de narrativas na pasta `narrativas/`.

## Preparação dos Dados

- **Formato**: Narrativas em XML, com texto clínico dentro da tag `<TEXT>`.
- **Gold Standard**: Arquivos com sufixo `_goldstandard.xml` (ex.: `9053.xml` e `9053_goldstandard.xml`).
- **Localização**: Salve todos os arquivos na pasta `narrativas/`.

## Como Usar

1. Certifique-se de que o modelo está em `modelo/`.
2. Execute: `python main.py`.
3. Aguarde o processamento (pode levar tempo dependendo do volume de dados).

## Estrutura do Projeto

```
projeto/
├── main.py                           # Script principal (orquestra o pipeline).
├── README.md                         # Documentação (este arquivo).
├── requirements.txt                  # Dependências Python.
├── comando_llama/
│   └── prompt.py                     # Template de prompt para LLaMA.
├── modelo/
│   └── Llama-3.2-3B-Instruct-Q4_K_M.gguf  # Modelo LLaMA (baixado separadamente).
├── narrativas/
│   ├── 9053.xml                      # Exemplo de narrativa XML.
│   └── 9053_goldstandard.xml         # Exemplo de gold standard.
├── utils/
│   ├── processador_narrativa.py      # Processamento de narrativas XML.
│   ├── processador_csv.py            # Manipulação de CSVs.
│   ├── processador_excel.py          # Manipulação de Excel e dicionários.
│   ├── processador_llama.py          # Interface com LLaMA.
│   ├── processador_relacoes.py       # Processamento de relações XML.
│   ├── processador_xml.py            # Parsing de XML.
│   ├── similaridade.py               # Cálculo de similaridade (TF-IDF).
│   └── mapeamento_snomed.py          # Mapeamento SNOMED CT.
└── data/                             # Saídas geradas automaticamente.
    ├── csv_output/
    │   ├── output_9053.xml.csv       # CSVs individuais por narrativa.
    │   └── todas_narrativas_extraidas_ordenado.csv  # CSV consolidado.
    ├── Resultados.xlsx               # Excel com classificações e métricas.
    └── dicionario.json               # Cache de mapeamentos SNOMED.
```

**Legenda dos Arquivos**:
- **Obrigatórios**: Essenciais para execução (código, modelo, dados de entrada).
- **Opcionais**: Melhoram a experiência (documentação).
- **Gerados**: Criados durante execução; não precisam existir inicialmente.

## Módulos e Funcionalidades

### main.py
- Coordena todo o pipeline: inicializa LLaMA, processa narrativas, compara com gold standard, calcula similaridade, mapeia SNOMED e exibe métricas.

### utils/processador_narrativa.py
- `processar_narrativas()`: Lê XMLs, chama LLaMA para extração, salva CSVs individuais.
- `formatar_saida()`: Gera CSVs por narrativa.
- `criar_csv_mestre()`: Consolida CSVs em um arquivo mestre ordenado.
- `comparar_com_goldstandard()`: Compara extrações com anotações manuais, gera Excel com VP/FP/FN.

### utils/processador_csv.py
- `criar_dataframe_e_exportar_csv()`: Parseia resposta LLaMA, extrai termos no formato [Texto | Abrev | Cat | SCTID], exporta CSV.

### utils/processador_llama.py
- `PesquisaClin_Llama()`: Envia prompt para LLaMA, divide texto se necessário.
- `dividir_texto_por_prompt_seguro()`: Quebra textos longos para caber no contexto.

### utils/similaridade.py
- `medir_similaridade()`: Calcula similaridade cosseno entre termos usando TF-IDF.

### utils/mapeamento_snomed.py
- `prompt_avmap()`: Consulta API SNOMED CT para validar códigos.

### utils/processador_excel.py
- `carregar_dicionario()` / `salvar_dicionario()`: Gerencia cache SNOMED em JSON.
- `carregar_excel()` / `salvar_excel()`: Lê/escreve arquivos Excel.

### utils/processador_xml.py
- `relacoes()` / `dados_relacionados()`: Parseia anotações XML e relações.
- `padronizar_string()` / `stem_frase()`: Pré-processamento textual.

### utils/processador_relacoes.py
- Funções auxiliares para relações entre anotações XML.

### comando_llama/prompt.py
- `PROMPT_TEMPLATE`: Prompt estruturado para guiar LLaMA na extração de termos clínicos.

## Interpretação dos Resultados

- **Classificações**: VP (Verdadeiro Positivo), FP (Falso Positivo), FN (Falso Negativo), VPP (Verdadeiro Positivo após similaridade).
- **Métricas**: Precisão = (VP + VPP) / (VP + VPP + FP); Recall = (VP + VPP) / (VP + VPP + FN); F1-Score = média harmônica de Precisão e Recall.
- **Mapeamento SNOMED**: Verifica existência e correspondência de códigos SCTID.
- Resultados salvos em `data/Resultados.xlsx`.

## Solução de Problemas

- **Erro de memória ("out of memory")**: Reduza `n_ctx` em `main.py` (ex.: 4096) ou use modelo menor. Garanta 8 GB RAM livre.
- **Modelo não encontrado**: Verifique caminho em `main.py` e presença do arquivo `.gguf` em `modelo/`. Reexecute download se necessário.
- **Erro ao parsear XML**: Arquivos devem ter tag `<TEXT>`. Corrija estruturas inválidas.
- **Resultados zerados**: Confirme presença de gold standards correspondentes (ex.: `9053.xml` + `9053_goldstandard.xml`).
- **Falha no SNOMED**: Verifique conexão internet e validade dos SCTIDs.
- **Execução lenta**: Ajuste `n_threads` (CPUs) e `n_gpu_layers` (GPUs) em `main.py`.
- **Dependências faltando**: Reinstale com `pip install -r requirements.txt`. Para CUDA: `pip install llama-cpp-python[cuBLAS]`.

## Saídas

- **CSVs individuais**: `data/csv_output/output_*.csv` (um por narrativa).
- **CSV mestre**: `data/csv_output/todas_narrativas_extraidas_ordenado.csv`.
- **Excel de resultados**: `data/Resultados.xlsx` (classificações, mapeamentos).
- **Console**: Tabelas com métricas, contagens SNOMED e tempo total.
