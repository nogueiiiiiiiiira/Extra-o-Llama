import os
import time
import xml.etree.ElementTree as ET
import pandas as pd
from .processador_csv import criar_dataframe_e_exportar_csv
from .processador_llama import PesquisaClin_Llama 
from .processador_xml import padronizar_string
from .processador_relacoes import relacoes, dados_relacionados

# Função principal que processa todas as narrativas XML de uma pasta
def processar_narrativas(pasta_narrativas, csv_output_folder, llm, max_tokens=256, temperature=0.7):
    
    # Processa todos os arquivos XML na pasta usando LLaMA em blocos, salva CSVs individuais e retorna uma lista de DataFrames.
    lista_dataframes_individuais = []

    # Lista todos os arquivos XML válidos (ignora arquivos _goldstandard)
    arquivos_xml = [f for f in os.listdir(pasta_narrativas)
                    if f.endswith('.xml') and not f.endswith('_goldstandard.xml')]

    if not arquivos_xml:
        print("\n❌ Nenhum arquivo XML válido encontrado na pasta de narrativas.")
        return []

    print(f"\n\n✅ {len(arquivos_xml)} arquivos XML encontrados. Iniciando processamento...")

    # Processa cada narrativa individualmente
    for nome_narrativa in arquivos_xml:
        caminho_narrativa = os.path.join(pasta_narrativas, nome_narrativa)
        max_tentativas = 3
        delay = 2

        for tentativa in range(max_tentativas):
            try:
                if not os.path.exists(caminho_narrativa):
                    print(f"\nTentativa {tentativa + 1}: Arquivo não encontrado: {caminho_narrativa}. Tentando novamente...")
                    time.sleep(delay)
                    continue

                # Parse do XML
                tree = ET.parse(caminho_narrativa)
                root = tree.getroot()
                elemento_texto = root.find('.//TEXT')

                if elemento_texto is not None and elemento_texto.text:
                    xml_text = elemento_texto.text

                    # Chama LLaMA para processar o texto, dividindo em blocos se necessário
                    resposta = PesquisaClin_Llama(
                        xml_text,
                        llm,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    print(f"\n\n✅ Processado {nome_narrativa} (tentativa {tentativa + 1}):\n {resposta[:100]}...")

                    # Formata e salva CSV individual
                    dataframe_resultante = formatar_saida(resposta, nome_narrativa, csv_output_folder)
                    if dataframe_resultante is not None and not dataframe_resultante.empty:
                        lista_dataframes_individuais.append(dataframe_resultante)
                    break  # sucesso, sai do loop de retries
                else:
                    print(f"\n⚠️ Elemento TEXT não encontrado ou vazio em {nome_narrativa}. Pulando arquivo.")
                    break

            except ET.ParseError:
                print(f"\n⚠️ Erro ao parsear XML: {nome_narrativa}. Pulando arquivo.")
                break
            except Exception as e:
                print(f"\n⚠️ Erro inesperado em {nome_narrativa}: {e}. Retrying...")
                time.sleep(delay)
                continue

    return lista_dataframes_individuais

# Cria CSV individual a partir da resposta do modelo
def formatar_saida(resposta, nome_narrativa, csv_output_folder):
    
    os.makedirs(csv_output_folder, exist_ok=True)  # Garante que a pasta de saída exista
    nome_arquivo_csv_individual = os.path.join(csv_output_folder, f"output_{nome_narrativa}.csv")

    dataframe_resultante = criar_dataframe_e_exportar_csv(
        input_text=resposta,
        csv_filename=nome_arquivo_csv_individual,
        narrative_name=nome_narrativa
    )

    return dataframe_resultante

# Cria CSV mestre a partir dos DataFrames individuais
def criar_csv_mestre(lista_dataframes_individuais, csv_output_folder):
    
    # Junta todos os CSVs individuais em um único CSV mestre, ordenado por narrativa e termo.
    if lista_dataframes_individuais:
        df_mestre = pd.concat(lista_dataframes_individuais, ignore_index=True)

        # Ordena os dados por nome da narrativa e texto analisado
        df_mestre_sorted = df_mestre.sort_values(
            by=['nomeNarrativa', 'textoAnalisado'],
            ascending=[True, True],
            key=lambda col: col.str.lower() if col.name == 'textoAnalisado' else col,
            ignore_index=True
        )

        os.makedirs(csv_output_folder, exist_ok=True)
        csv_mestre_filename = os.path.join(csv_output_folder, "todas_narrativas_extraidas_ordenado.csv")
        df_mestre_sorted.to_csv(csv_mestre_filename, index=False, encoding='utf-8', sep=',')
        print(f"\n✅ CSV mestre gerado: {csv_mestre_filename}")
        return csv_mestre_filename
    else:
        print("\n❌ Nenhum DataFrame individual foi gerado.")
        return None

# Compara resultados do modelo com o gold standard e gera Excel de avaliação
def comparar_com_goldstandard(csv_mestre, pasta_narrativas, excel_resultados):
    
    # Compara os resultados extraídos pelo modelo com o gold standard e salva um Excel de avaliação.
    df_prompts = pd.read_csv(csv_mestre)
    df_resultado = pd.DataFrame(columns=[
        "nomeNarrativa", "textoPrompt", "categoria", "termoAnalisado",
        "abreviacao", "SCTID", "semClin_nomeNarrativa","semClin_textoAnalisado", "semClin_categoria", "classificacao"
    ])

    # Mapeia colunas do CSV mestre para o formato esperado
    col_mapping = {
        'nomeNarrativa': 'nomeNarrativa',
        'textoPrompt': 'textoPrompt',
        'categoria': 'categoria',
        'textoAnalisado': 'termo',
        'abreviacao': 'abreviacao',
        'SCTID': 'SCTID'
    }
    df_prompts = df_prompts.rename(columns=col_mapping)
    narrativas_unicas = df_prompts['nomeNarrativa'].unique()

    # Compara cada narrativa individual com seu gold standard
    for narrativa_atual in narrativas_unicas:
        df_narrativa_atual = df_prompts[df_prompts['nomeNarrativa'] == narrativa_atual].copy()
        achados_prompt = df_narrativa_atual[['termo', 'textoPrompt', 'categoria', 'abreviacao', 'SCTID']].to_dict('records')

        narrativa_semclin = os.path.join(pasta_narrativas, f"{narrativa_atual[:4]}.xml")
        try:
            tree = ET.parse(narrativa_semclin)
            root = tree.getroot()
            achados_semclin = []
            relacao = relacoes(root)

            # Extrai os achados do gold standard
            for annotation in root.find('TAGS'):
                specific_annotation = annotation.get('tag')
                id = annotation.get('id')
                dado = padronizar_string(annotation.get('text'))
                dadoFinal, negado = dados_relacionados(relacao, id, root, dado)

                if dadoFinal and ("Sign or Symptom" in specific_annotation or "Disease or Syndrome" in specific_annotation) and not negado and "Diagnostic Procedure" not in specific_annotation:
                    categoria = "Sinal ou Sintoma" if "Sign or Symptom" in specific_annotation else "Doença ou Síndrome"
                    achados_semclin.append({
                        "narrativa": narrativa_semclin[-8:],
                        "termo": dadoFinal,
                        "categoria": categoria
                    })

            # Ordena os achados do gold standard
            achados_semclin.sort(key=lambda item: item['termo'])
            usado_prompt = [False] * len(achados_prompt)
            usado_semclin = [False] * len(achados_semclin)

            # Identifica Verdadeiros Positivos (VP)
            for i, achado in enumerate(achados_prompt):
                for j, achado_xml in enumerate(achados_semclin):
                    if not usado_prompt[i] and not usado_semclin[j]:
                        if achado["termo"] == achado_xml["termo"]:
                            df_resultado = pd.concat([df_resultado, pd.DataFrame([{
                                "nomeNarrativa": narrativa_atual,
                                "textoPrompt": achado["textoPrompt"],
                                "categoria": achado["categoria"],
                                "termoAnalisado": achado["termo"],
                                "abreviacao": achado["abreviacao"],
                                "SCTID": achado["SCTID"],
                                "semClin_nomeNarrativa": achado_xml['narrativa'],
                                "semClin_textoAnalisado": achado_xml['termo'],
                                "semClin_categoria": achado_xml["categoria"],
                                "classificacao": 'VP'
                            }])], ignore_index=True)
                            usado_prompt[i] = True
                            usado_semclin[j] = True
                            break

            # Identifica Falsos Positivos (FP)
            for i, achado in enumerate(achados_prompt):
                if not usado_prompt[i]:
                    df_resultado = pd.concat([df_resultado, pd.DataFrame([{
                        "nomeNarrativa": narrativa_atual,
                        "textoPrompt": achado["textoPrompt"],
                        "categoria": achado["categoria"],
                        "termoAnalisado": achado["termo"],
                        "abreviacao": achado["abreviacao"],
                        "SCTID": achado["SCTID"],
                        "semClin_nomeNarrativa": "",
                        "semClin_textoAnalisado": "",
                        "semClin_categoria": "",
                        "classificacao": 'FP'
                    }])], ignore_index=True)

            # Identifica Falsos Negativos (FN)
            for j, achado_xml in enumerate(achados_semclin):
                if not usado_semclin[j]:
                    df_resultado = pd.concat([df_resultado, pd.DataFrame([{
                        "nomeNarrativa": "",
                        "textoPrompt": "",
                        "categoria": "",
                        "termoAnalisado": "",
                        "abreviacao": "",
                        "SCTID": "",
                        "semClin_nomeNarrativa": achado_xml['narrativa'],
                        "semClin_textoAnalisado": achado_xml['termo'],
                        "semClin_categoria": achado_xml["categoria"],
                        "classificacao": 'FN'
                    }])], ignore_index=True)

        except FileNotFoundError:
            print(f"\nErro: Arquivo XML não encontrado para a narrativa {narrativa_atual}")
            continue
        except Exception as e:
            print(f"\nErro ao processar narrativa {narrativa_atual}: {e}")
            continue

    # Salva o resultado da comparação em Excel
    df_resultado.to_excel(excel_resultados, index=False, sheet_name='Resultados')
    return df_resultado
