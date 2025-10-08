# Extração e Avaliação de Termos Clínicos

Este projeto processa narrativas clínicas em formato XML, extrai termos clínicos (sinais/sintomas e doenças/síndromes) usando modelo LLaMA, compara com anotações gold standard, realiza análise de similaridade, mapeia para SNOMED CT e calcula métricas de avaliação.

## Pré-requisitos

- Python 3.8 ou superior.
- Pelo menos 8 GB de RAM (recomendado 16 GB para processamento de textos longos).
- GPU com suporte a CUDA (opcional, acelera o processamento com LLaMA).
- Espaço em disco: ~5 GB para o modelo LLaMA.

**Nota sobre Tokens e Limitações do Modelo:**  
Devido às limitações de hardware do computador usado no desenvolvimento, o código foi otimizado para dividir narrativas, prompts e textos em partes menores. O LLaMA trabalha com "tokens" (unidades de texto, como palavras ou fragmentos de palavras, que o modelo processa). Cada modelo tem um limite de tokens que pode processar de uma vez (contexto máximo). Se o texto exceder esse limite, o código divide automaticamente o conteúdo para evitar erros. Isso garante que o processamento funcione mesmo em máquinas com recursos limitados.  
**Aviso:** O processamento com LLaMA pode ser demorado, dependendo do tamanho das narrativas e da potência do hardware. Paciência é recomendada.  
**Atualização do Modelo:** Se desejar usar um modelo LLaMA superior (ex: com mais parâmetros ou melhor desempenho), altere o caminho do modelo em `main.py` (linha com `Llama(model_path=...)`) e ajuste parâmetros como `n_ctx` e `max_tokens` nas chamadas de função. Baixe o novo modelo via Hugging Face e coloque em `modelo/`.

## Instalação

1. Instale Python (versão 3.8+): [Download Python](https://www.python.org/downloads/)
2. Instale Hugging Face CLI: `pip install huggingface_hub`
3. Clone o repositório.
4. Instale dependências: `pip install -r requirements.txt`
5. Baixe o modelo LLaMA. Execute: `huggingface-cli download hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF --include "llama-3.2-3b-instruct-q4_k_m.gguf" --local-dir ./modelo/`
6. Coloque narrativas XML na pasta `narrativas/`.

## Preparação dos Dados

- As narrativas devem estar em formato XML, com o texto clínico dentro da tag `<TEXT>`.
- Arquivos gold standard devem ter o sufixo `_goldstandard.xml` (ex: `9053.xml` e `9053_goldstandard.xml`).
- Coloque os arquivos na pasta `narrativas/`.

## Uso

1. Certifique-se de que o modelo LLaMA está baixado em `modelo/`.
2. Execute `python main.py` para processar todas as narrativas e gerar resultados.
3. O processamento pode levar tempo dependendo do número e tamanho das narrativas.

## Estrutura do Projeto

A estrutura completa do projeto é a seguinte (arquivos obrigatórios, opcionais e gerados estão marcados):

```
projeto/
├── main.py                           # Obrigatório: Script principal para executar o pipeline.
├── README.md                         # Opcional: Documentação do projeto.
├── requirements.txt                  # Obrigatório: Dependências Python.
├── comando_llama/
│   └── prompt.py                     # Obrigatório: Template de prompt para LLaMA.
├── modelo/
│   └── Llama-3.2-3B-Instruct-Q4_K_M.gguf  # Obrigatório: Modelo LLaMA baixado (não incluído no repositório).
├── narrativas/
│   ├── 9053.xml                      # Obrigatório: Arquivos XML de narrativas clínicas (exemplo).
│   └── 9053_goldstandard.xml         # Obrigatório: Arquivos gold standard correspondentes.
├── utils/
│   ├── processador_narrativa.py      # Obrigatório: Processamento de narrativas.
│   ├── processador_csv.py            # Obrigatório: Manipulação de CSVs.
│   ├── processador_excel.py          # Obrigatório: Manipulação de Excel e dicionários.
│   ├── processador_llama.py          # Obrigatório: Interface com LLaMA.
│   ├── processador_relacoes.py       # Obrigatório: Processamento de relações XML.
│   ├── processador_xml.py            # Obrigatório: Parse de XML.
│   ├── similaridade.py               # Obrigatório: Cálculo de similaridade.
│   └── mapeamento_snomed.py          # Obrigatório: Mapeamento SNOMED CT.
└── data/                             # Gerado automaticamente: Pasta de saídas.
    ├── csv_output/
    │   ├── output_9053.xml.csv       # Gerado: CSVs individuais por narrativa.
    │   └── todas_narrativas_extraidas_ordenado.csv  # Gerado: CSV mestre.
    ├── Resultados.xlsx               # Gerado: Excel com métricas e classificações.
    └── dicionario.json               # Gerado: Dicionário SNOMED persistido.
```

**Notas sobre Arquivos:**
- **Obrigatórios:** Devem existir antes da execução (código fonte, modelo, dados de entrada).
- **Opcionais:** Melhoram a documentação ou são extras.
- **Gerados:** Criados automaticamente durante a execução; não precisam existir inicialmente.

## Módulos e Funções

### main.py
- Script principal que orquestra o pipeline.
- Inicializa modelo LLaMA.
- Chama funções de processamento e calcula métricas finais.

### utils/processador_narrativa.py
- `processar_narrativas()`: Processa arquivos XML, chama LLaMA para extração, formata saída para CSV.
- `formatar_saida()`: Chama criação de CSV.
- `criar_csv_mestre()`: Combina CSVs individuais em CSV mestre.
- `comparar_com_goldstandard()`: Compara termos extraídos com anotações gold standard XML, gera Excel com classificações VP/FP/FN.

### utils/processador_csv.py
- `criar_dataframe_e_exportar_csv()`: Faz parse da resposta LLaMA, extrai termos no formato [Texto | Abrev | Cat | SCTID], exporta para CSV.

### utils/processador_llama.py
- `PesquisaClin_Llama()`: Chama LLaMA com prompt, trata divisão de texto se necessário.
- `dividir_texto_por_prompt_seguro()`: Divide textos longos para caber na janela de contexto.

### utils/similaridade.py
- `medir_similaridade()`: Calcula similaridade cosseno entre termos usando TF-IDF.

### utils/mapeamento_snomed.py
- `prompt_avmap()`: Consulta API SNOMED CT para validar códigos.

### utils/processador_excel.py
- `carregar_dicionario()` / `salvar_dicionario()`: Carrega/salva dicionário SNOMED em JSON.
- `carregar_excel()` / `salvar_excel()`: Carrega/salva arquivos Excel.

### utils/processador_xml.py
- `relacoes()` / `dados_relacionados()`: Faz parse de anotações XML e relações.
- `padronizar_string()` / `stem_frase()`: Pré-processamento de texto.

### utils/processador_relacoes.py
- Funções para processar relações entre anotações XML.

### comando_llama/prompt.py
- `PROMPT_TEMPLATE`: Prompt detalhado para LLaMA extrair e anotar termos clínicos.

## Interpretação dos Resultados

- **Classificações**: VP (Verdadeiro Positivo), FP (Falso Positivo), FN (Falso Negativo), VPP (Verdadeiro Positivo após similaridade).
- **Métricas**: Precisão (VP / (VP + FP)), Recall (VP / (VP + FN)), F1-Score (média harmônica de Precisão e Recall).
- **Mapeamento SNOMED**: Verifica se códigos existem e correspondem aos termos.
- Resultados salvos em `data/Resultados.xlsx`.

## Solução de Problemas

- **Erro de memória ou "out of memory"**: Reduza `n_ctx` em `main.py` (ex: para 4096) ou use um modelo LLaMA menor. Certifique-se de ter pelo menos 8 GB de RAM livre.
- **Modelo não encontrado**: Verifique se o arquivo `.gguf` está em `modelo/` e o caminho em `main.py` está correto. Execute o comando de download novamente se necessário.
- **Erro ao parsear XML**: Certifique-se de que os arquivos XML têm a estrutura esperada com tag `<TEXT>`. Arquivos corrompidos podem causar falhas.
- **Sem resultados ou métricas zeradas**: Verifique se há arquivos gold standard correspondentes (ex: `9053.xml` e `9053_goldstandard.xml`). O processamento pode falhar se os dados de entrada estiverem incompletos.
- **Problemas com SNOMED CT**: Se o mapeamento falhar, verifique a conexão com a internet (para consultas à API SNOMED) e se os códigos SCTID são válidos.
- **Execução lenta**: Ajuste `n_threads` em `main.py` conforme o número de núcleos da CPU. Use GPU se disponível (aumente `n_gpu_layers`).
- **Dependências faltando**: Execute `pip install -r requirements.txt` novamente. Se `llama-cpp-python` falhar, instale com suporte a CUDA se houver GPU: `pip install llama-cpp-python[cuBLAS]`.

## Saída

- CSVs individuais em `data/csv_output/`
- CSV mestre: `data/csv_output/todas_narrativas_extraidas_ordenado.csv`
- Excel de resultados: `data/Resultados.xlsx` com classificações e mapeamentos.
- Saída no console: Métricas (Precisão, Recall, F1), contagens SNOMED, tempo de execução.
