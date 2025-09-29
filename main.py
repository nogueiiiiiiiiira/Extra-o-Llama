import os
import pandas as pd
import time
from llama_cpp import Llama
from openpyxl import load_workbook
from utils.processador_csv import criar_dataframe_e_exportar_csv
from utils.config import carregar_config
from utils.processar_llama import PesquisaClin_Llama
from utils.processar_xml import processar_xml
from utils.analise import processar_narrativa_para_analise, calcular_similaridade_e_atualizar_excel, calcular_metricas
from utils.mapeamento_snomed import mapear_snomed_para_excel, contar_resultados_mapeamento, verificar_snomed

def main():

    # carrega config, que inclui paths e parâmetros
    config = carregar_config()

    # caminhos dos arquivos
    base_dir = config['base_dir']
    modelo_path = os.path.join(base_dir, config['modelo_path'])
    pasta_xml = os.path.join(base_dir, config['pasta_xml'])
    arquivo_excel = os.path.join(base_dir, config['arquivo_excel'])
    output_dir = os.path.join(base_dir, config['output_dir'])
    csv_path = os.path.join(base_dir, config['csv_path'])
    excel_resultados = os.path.join(base_dir, config['excel_resultados'])
    dicionario_path = os.path.join(base_dir, config['dicionario_path'])

    # parâmetros
    similaridade = config['similaridade']
    max_tokens_por_bloco = config['max_tokens_por_bloco']
    sleep_sec = config['sleep_sec']
    max_retries = config['max_retries']
    retry_delay_seconds = config['retry_delay_seconds']
    llm_max_tokens = config['llm_max_tokens']
    llm_temperature = config['llm_temperature']
    llm_n_ctx = config['llm_n_ctx']

    # inicializar LLaMA
    print("=== INICIALIZAÇÃO ===")
    try:
        llm = Llama(model_path=modelo_path, n_ctx=llm_n_ctx)
        print("\n\n✅ LLaMA inicializado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inicializar LLaMA: {e}")
        return

    # criar output_dir se não existir
    os.makedirs(output_dir, exist_ok=True)

    # inicializar CSV se não existir
    if not os.path.exists(csv_path):
        pd.DataFrame(columns=["arquivo", "resposta"]).to_csv(csv_path, index=False)
        print("CSV inicial criado!")

    # encontrar arquivos XML
    arquivos_xml = []
    for root, dirs, files in os.walk(pasta_xml):
        for f in files:
            if f.lower().endswith('.xml'):
                arquivos_xml.append(os.path.join(root, f))

    print("\n=== PROCESSAMENTO DOS XMLs ===")
    if not arquivos_xml:
        print("\n❌ Nenhum arquivo XML válido encontrado na pasta de narrativas.")
        return
    else:
        print(f"\n✅ {len(arquivos_xml)} arquivos XML encontrados. Iniciando processamento...")

    # iniciar timer para processamento dos XMLs
    start_time = time.time()

    # processar XMLs
    lista_dataframes_individuais = []
    for caminho_narrativa in arquivos_xml:
        print(f"\nProcessando {os.path.basename(caminho_narrativa)}")

        for attempt in range(max_retries):
            try:
                if not os.path.exists(caminho_narrativa):
                    print(f"\nArquivo não encontrado: {caminho_narrativa}. Tentando novamente...")
                    time.sleep(retry_delay_seconds)
                    continue

                resposta = processar_xml(caminho_narrativa, llm, max_tokens_por_bloco, sleep_sec)
                print(f"\n✅ Bloco processado (Tentativa {attempt + 1})")

                nome_arquivo_csv_individual = os.path.join(output_dir, f"output_{os.path.basename(caminho_narrativa)}.csv")
                dataframe_resultante = criar_dataframe_e_exportar_csv(
                    input_text=resposta,
                    csv_filename=nome_arquivo_csv_individual,
                    narrative_name=os.path.basename(caminho_narrativa)
                )

                if dataframe_resultante is None or dataframe_resultante.empty:
                    dataframe_resultante = pd.DataFrame([{
                        "nomeNarrativa": os.path.basename(caminho_narrativa),
                        "textoPrompt": "",
                        "categoria": "",
                        "textoAnalisado": "",
                        "abreviacao": "",
                        "SCTID": ""
                    }])

                lista_dataframes_individuais.append(dataframe_resultante)
                print(f"\n✅ DataFrame registrado.")
                break

            except Exception as e:
                print(f"\n❌ Erro: {e}. Pulando arquivo.")
                break

    # finalizar timer
    elapsed_time = time.time() - start_time
    print(f"\n⏱️ TEMPO TOTAL: {elapsed_time:.2f} segundos ({elapsed_time/60:.2f} minutos)")

    # consolidar CSVs
    if lista_dataframes_individuais:
        df_mestre = pd.concat(lista_dataframes_individuais, ignore_index=True)

        df_mestre_sorted = df_mestre.sort_values(
            by=['nomeNarrativa', 'textoAnalisado'],
            ascending=[True, True],
            key=lambda col: col.str.lower() if col.name == 'textoAnalisado' else col,
            ignore_index=True
        )

        master_csv_filename = os.path.join(output_dir, "todas_narrativas_extraidas_ordenado.csv")
        df_mestre_sorted.to_csv(master_csv_filename, index=False, encoding='utf-8', sep=',')
        print(f"\n✅ CSV mestre gerado: {master_csv_filename}")
    else:
        print("\n❌ Nenhum DataFrame individual foi gerado.")

    print("\nIniciando análise das narrativas...")
    print("\n=== ANÁLISE ===")
    excel_prompts = os.path.join(output_dir, "todas_narrativas_extraidas_ordenado.csv")
    df_prompts = pd.read_csv(excel_prompts, encoding='utf-8')

    col_mapping = {
        'nomeNarrativa': 'nomeNarrativa',
        'textoPrompt': 'textoPrompt',
        'categoria': 'categoria',
        'textoAnalisado': 'termo',
        'abreviacao': 'abreviacao',
        'SCTID': 'SCTID'
    }
    df_prompts = df_prompts.rename(columns=col_mapping)

    narrativas_unicas = df_prompts['nomeNarrativa'].dropna().unique()

    registros_resultado = []
    for narrativa_atual in narrativas_unicas:
        print(f"\nProcessando narrativa {narrativa_atual}")
        registros = processar_narrativa_para_analise(narrativa_atual, df_prompts, excel_resultados, pasta_xml, similaridade)
        registros_resultado.extend(registros)

    df_resultado = pd.DataFrame(registros_resultado)
    df_resultado.to_excel(excel_resultados, index=False, sheet_name='Resultados')
    print("\n✅ Resultados salvos no Excel.")

    print("\n=== SIMILARIDADE ===")
    calcular_similaridade_e_atualizar_excel(excel_resultados, similaridade)

    print("\n=== MÉTRICAS ===")
    VP, FP, FN, VPP, precisao, recall, f1_score = calcular_metricas(excel_resultados)
    print(f"VP: {VP}, FP: {FP}, FN: {FN}, VPP: {VPP}")
    print(f"Precisão: {precisao:.4f}, Recall: {recall:.4f}, F1-Score: {f1_score:.4f}")

    print("\n=== MAPEAMENTO SNOMED ===")
    dicionario = mapear_snomed_para_excel(excel_resultados, dicionario_path)
    print("\n✅ Dicionário SNOMED carregado.")

    # exemplo de verificação
    termo = 'febre'
    codigo = '386661006'
    resposta = verificar_snomed(codigo, termo, dicionario)
    print(f"\nVerificar se '{termo}' corresponde a {codigo}: {resposta}")

    # contar resultados
    contagem = contar_resultados_mapeamento(excel_resultados)

    # exemplo de execução
    termo = 'febre'
    codigo = '386661006'
    print(f"\nVerificar se '{termo}' corresponde a {codigo} na terminologia SNOMED: ")
    print("\nResposta do modelo: ")
    resposta = verificar_snomed(codigo, termo, dicionario)
    if resposta == 0:
        print("\nO código SNOMED CT fornecido não existe")
    elif resposta == 1:
        print("\nO código existe, mas não corresponde ao termo fornecido")
    elif resposta == 2:
        print("\nO código existe e corresponde corretamente ao termo fornecido")
    else:
        print(resposta)

    # visualizar resultados
    workbook = load_workbook(excel_resultados)
    planilha = workbook['Resultados']
    index = 2
    resultados = [0, 0, 0]
    while planilha[f'A{index}'].value or planilha[f'G{index}'].value:
        classificacao = planilha[f'K{index}'].value
        if classificacao is not None:
            if isinstance(classificacao, int):
                resultados[int(classificacao)] += 1
        index += 1

    contagem = {
        "O código SNOMED CT fornecido não existe": [resultados[0]],
        "O código existe, mas não corresponde ao termo fornecido": [resultados[1]],
        "O código existe E corresponde corretamente ao termo fornecido": [resultados[2]],
        "Total": [sum(resultados)]
    }

    df = pd.DataFrame(contagem)
    print("\n=== RESULTADOS DO MAPEAMENTO SNOMED: ===\n\n")
    print(df)

if __name__ == "__main__":
    main()
