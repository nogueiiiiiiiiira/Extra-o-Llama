# Projeto PIBIC: Extração de Achados Clínicos com Llama

Este projeto utiliza um modelo de linguagem Llama para extrair achados clínicos (sinais, sintomas, doenças e síndromes) de narrativas médicas em português, mapeá-los para códigos SNOMED CT e comparar com anotações de referência (goldstandard) para avaliação de desempenho.

## Descrição do Projeto

O código processa arquivos XML contendo narrativas clínicas, utiliza o modelo Llama para identificar e classificar termos médicos relevantes, e gera métricas de precisão, recall e F1-score comparando com anotações manuais de especialistas.

### Funcionalidades Principais
- **Extração de Termos Clínicos**: Identifica sinais/sintomas e doenças/síndromes em textos clínicos.
- **Mapeamento SNOMED CT**: Busca códigos SCTID correspondentes aos termos extraídos.
- **Comparação com Gold Standard**: Avalia a precisão do modelo contra anotações de referência.
- **Cálculo de Métricas**: Gera VP (Verdadeiros Positivos), FP (Falsos Positivos), FN (Falsos Negativos) e métricas agregadas.
- **Similaridade Semântica**: Usa TF-IDF e stemming para melhorar a correspondência de termos similares.

## Requisitos

- Python 3.8+
- Bibliotecas: `llama-cpp-python`, `pandas`, `openpyxl`, `scikit-learn`, `nltk`, `unidecode`, `requests`
- Modelo Llama: Llama-3.2-3B-Instruct-Q4_K_M.gguf (aprox. 2GB de espaço em disco)

### Hardware Recomendado
- RAM: 8GB mínimo (16GB recomendado)
- Espaço em disco: 5GB para modelo e dados
- GPU: Opcional, mas acelera a inferência (suporte CUDA se disponível)

## Instalação

1. **Clone ou baixe o repositório**:
   ```
   git clone <url-do-repositorio>
   cd <diretorio-do-projeto>
   ```

2. **Instale as dependências**:
   ```
   pip install llama-cpp-python pandas openpyxl scikit-learn nltk unidecode requests
   ```

3. **Baixe o modelo Llama** (veja seção "Modelo Llama" abaixo).

4. **Prepare os dados**:
   - Coloque os arquivos XML de narrativas na pasta `narrativas/`.
   - Certifique-se de que há um arquivo `equivalências.xlsx` para mapeamentos adicionais.

## Uso

1. **Execute o script principal**:
   ```
   python main.py
   ```
   **Nota sobre tempo de execução**: O script pode demorar alguns minutos a horas para processar todas as narrativas, dependendo do hardware (CPU/GPU, RAM) e do número de arquivos. Isso ocorre devido ao carregamento do modelo Llama (que consome memória) e ao processamento sequencial dos textos com inferência de IA. Em máquinas com GPU, o tempo é reduzido significativamente.

2. **Saídas**:
   - CSVs individuais por narrativa em `csv_output/`.
   - CSV consolidado: `csv_output/todas_narrativas_extraidas_ordenado.csv`.
   - Resultados finais: `Resultados.xlsx` com métricas e comparações.

3. **Visualização de Métricas**:
   O script imprime no console as métricas finais (Precisão, Recall, F1-Score).

## Estrutura do Projeto

```
.
├── main.py                  # Script principal
├── config.json              # Configurações do projeto (caminhos, parâmetros)
├── dicionario.json          # Dicionário local de códigos SNOMED CT (cache para mapeamentos de códigos SNOMED para termos médicos, preenchido automaticamente durante a execução)
├── modelo/                  # Pasta para o modelo Llama
│   └── Llama-3.2-3B-Instruct-Q4_K_M.gguf
├── narrativas/              # Arquivos XML de narrativas clínicas
│   ├── 9400_goldstandard.xml
│   ├── 9410.xml
│   └── equivalências.xlsx
├── comando_llama/           # Prompts para o modelo Llama
│   └── prompt.py
├── utils/                   # Módulos utilitários
│   ├── config.py            # Funções para carregar configurações
│   ├── processador_csv.py   # Funções para processar e exportar dados CSV
│   ├── analise.py           # Funções de análise e métricas
│   ├── mapeamento_snomed.py # Funções para mapeamento SNOMED CT
│   ├── processar_llama.py   # Funções para interação com Llama
│   └── processar_xml.py     # Funções para processar arquivos XML
├── csv_output/              # Saídas CSV geradas (criada automaticamente)
├── Resultados.xlsx          # Resultados finais com métricas
└── README.md                # Este arquivo
```

## Pastas e Arquivos Necessários vs. Gerados

### Pastas/Arquivos que devem existir no repositório (inputs necessários):
- `modelo/`: Contém o modelo LLaMA (`Llama-3.2-3B-Instruct-Q4_K_M.gguf`).
- `narrativas/`: Contém os arquivos XML das narrativas (ex: `9400_goldstandard.xml`, `9410.xml`) e o arquivo `equivalências.xlsx`.
- `dicionario.json`: Dicionário local de códigos SNOMED CT (se não existir, será criado vazio e atualizado durante a execução).

### Pastas/Arquivos gerados automaticamente pelo código:
- `csv_output/`: Criada automaticamente se não existir.
- `Resultados.xlsx`: Gerado com as métricas finais e comparações.
- Arquivos CSV individuais em `csv_output/` (ex: `output_9410.xml.csv`).
- `todas_narrativas_extraidas_ordenado.csv` em `csv_output/`.

## Tecnologias e Bibliotecas Utilizadas

O projeto utiliza uma stack de tecnologias open-source para processamento de linguagem natural, manipulação de dados e inferência de IA local. 

### Modelo de IA: Llama-3.2-3B-Instruct

- **O que é?** Modelo de linguagem grande (LLM) da família Llama 3.2, desenvolvido pela Meta (anteriormente Facebook). Versão "Instruct" otimizada para seguir instruções e tarefas conversacionais.
- **Formato GGUF**: Quantizado em formato GGUF (GGML Unified Format), compatível com bibliotecas como `llama-cpp-python` para inferência eficiente em CPU/GPU.
- **Por que este modelo?** Foi o mais recomendável para o projeto: não muito pesado (3B parâmetros, ~2GB quantizado), executa localmente sem necessidade de hardware avançado, e atende à tarefa de extração de entidades clínicas em português. Mesmo com limitações de contexto (8192 tokens), consegui contornar dividindo as narrativas em blocos menores (máx. 500 caracteres) para processamento sequencial.

### Hugging Face

- **O que é?** Plataforma open-source para compartilhamento de modelos de IA, datasets e ferramentas. Funciona como um "GitHub para IA", permitindo download gratuito de modelos pré-treinados. É mantido pela Hugging Face Inc. e conta com uma comunidade ativa.
- **Uso no projeto**: Fonte para baixar o modelo Llama quantizado (via repositório TheBloke, que converte modelos oficiais para formatos otimizados como GGUF).

### Biblioteca Principal: llama-cpp-python

- **O que é?** Wrapper Python para a biblioteca C++ llama.cpp, que permite executar modelos Llama (e similares) localmente em CPU ou GPU, sem dependência de APIs em nuvem.
- **Uso no projeto**: Carrega e executa o modelo Llama para gerar respostas às prompts de extração de achados clínicos. Configurado com `n_ctx=8192` para contexto máximo e `temperature=0.7` para criatividade controlada.

### Outras Bibliotecas Python

- **pandas**: Manipulação e análise de dados tabulares (DataFrames). Usado para criar, filtrar e exportar CSVs com os achados extraídos.
- **openpyxl**: Leitura/escrita de arquivos Excel (.xlsx). Utilizado para gerar o relatório final `Resultados.xlsx` com métricas e comparações.
- **xml.etree.ElementTree**: Parsing de XML nativo do Python. Processa os arquivos de narrativas clínicas e gold standard para extrair texto e anotações.
- **unidecode**: Normalização de texto, removendo acentos e caracteres especiais. Padroniza termos médicos para comparação (ex.: "coração" vs "coracao").
- **scikit-learn (sklearn)**:
  - `TfidfVectorizer`: Converte texto em vetores TF-IDF para cálculo de similaridade.
  - `cosine_similarity`: Mede similaridade entre termos para reduzir falsos positivos/negativos por variações (ex.: "dispneia" vs "falta de ar").
- **nltk**: Biblioteca de processamento de linguagem natural.
  - `RSLPStemmer`: Redução de palavras à raiz (stemming) em português, usado na similaridade semântica.
- **numpy**: Computação numérica. Suporte para arrays e operações matemáticas (usado indiretamente via sklearn).
- **requests**: Cliente HTTP para APIs. Planejado para consultas à API SNOMED CT, mas no código atual usa dicionário local (`dicionario.json`).
- **json**: Manipulação de dados JSON. Carrega/salva o dicionário local de códigos SNOMED (arquivo `dicionario.json` na raiz do projeto).
- **os**: Interações com o sistema operacional (caminhos de arquivos, criação de pastas).
- **time**: Controle de tempo. Adiciona delays (`sleep`) entre processamentos para evitar sobrecarga.

### Infraestrutura

- **Execução Local**: Tudo roda na máquina do usuário (CPU/GPU), garantindo privacidade de dados médicos.
- **Processamento em Blocos**: Devido ao limite de contexto do modelo, textos longos são divididos em blocos de ~500 caracteres, processados sequencialmente e recombinados.
- **Armazenamento**: Dados em CSV/Excel para análise posterior; modelo em pasta dedicada.

## Modelo Llama

O projeto utiliza a biblioteca `llama-cpp-python` para executar modelos Llama localmente em formato GGUF (GGML Unified Format), garantindo privacidade e independência de APIs externas. O modelo padrão é o `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, mas você pode especificar e baixar outras versões conforme necessário.

#### Onde Especificar a Versão do Modelo

A versão do modelo é especificada no arquivo `config.json`, na chave `modelo_path`:

```json
{
  "modelo_path": "modelo/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
}
```

Para usar uma versão diferente:
1. Baixe o arquivo GGUF desejado (veja seções abaixo).
2. Coloque o arquivo na pasta `modelo/`.
3. Atualize o valor da chave `modelo_path` em `config.json`.
4. Ajuste parâmetros como `llm_n_ctx` em `config.json` se necessário (ex.: aumentar para modelos maiores).

#### Qual Versão Usar

- **Padrão**: `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (~2GB) - Equilibra desempenho e recursos, adequado para extração de entidades clínicas em português.
- **Para Melhor Desempenho**: Modelos maiores como `Llama-3.2-7B-Instruct-Q4_K_M` (~4GB) ou `Llama-3.2-13B-Instruct-Q4_K_M` (~7GB) oferecem maior precisão, mas requerem mais RAM (8-32GB) e tempo de processamento.
- **Para Máxima Precisão**: `Llama-3.1-70B-Instruct-Q4_K_M` (~40GB), mas impraticável sem GPUs dedicadas.

#### Como Baixar Outras Versões

Os modelos GGUF são baixados do Hugging Face, especificamente do repositório [TheBloke](https://huggingface.co/TheBloke), que fornece versões quantizadas otimizadas.

1. **Escolha o Repositório**:
   - Para Llama 3.2: [TheBloke/Llama-3.2-*-Instruct-GGUF](https://huggingface.co/TheBloke/Llama-3.2-3B-Instruct-GGUF) (substitua * pelo tamanho, ex.: 3B, 7B).
   - Para Llama 3.1: [TheBloke/Llama-3.1-*-Instruct-GGUF](https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF).

2. **Baixe o Arquivo**:
   - Acesse o repositório no Hugging Face.
   - Baixe o arquivo `.gguf` desejado (recomendado: variantes Q4_K_M para equilíbrio qualidade/tamanho).
   - Coloque na pasta `modelo/` do projeto.

3. **Usando CLI (Opcional)**:
   Se tiver `huggingface-cli` instalado (`pip install huggingface-hub`):
   ```
   huggingface-cli download TheBloke/Llama-3.2-7B-Instruct-GGUF Llama-3.2-7B-Instruct-Q4_K_M.gguf --local-dir ./modelo
   ```

**Nota**: Certifique-se de ter espaço em disco suficiente e conexão estável. Modelos maiores podem levar tempo para baixar.

## Resultados e Avaliação

- **Métricas Calculadas**: Precisão, Recall, F1-Score baseadas em VP, FP, FN.
- **Comparação**: Inclui similaridade semântica para reduzir FPs/FNs por variações de termos.
- **Mapeamento SNOMED**: Verifica códigos SCTID contra um dicionário local e API (se disponível).

## Diferença entre Ollama e Llama

- **Llama**: Refere-se à família de modelos de linguagem grande (LLMs) desenvolvidos pela Meta (anteriormente Facebook). Estes modelos são treinados em grandes quantidades de dados e podem ser usados para tarefas como geração de texto, tradução e extração de informações. No projeto, usamos o `llama-cpp-python` para executar versões quantizadas do Llama localmente em formato GGUF.

- **Ollama**: É uma ferramenta de software open-source que facilita a execução de modelos de IA, incluindo modelos Llama, localmente na máquina do usuário. Ollama fornece uma interface simplificada para baixar, gerenciar e executar LLMs sem necessidade de configurações complexas. É uma alternativa ao `llama-cpp-python`, oferecendo maior facilidade de uso, mas com menos controle sobre parâmetros avançados e potencialmente maior consumo de recursos.
