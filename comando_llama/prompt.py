PROMPT_TEMPLATE = """
**Objetivo:** Identificar achados clínicos e diagnósticos no texto clínico, classificá-los como "Sinal ou Sintoma" ou "Doença ou Síndrome" seguindo as definições e regras abaixo (com foco restrito em achados clínicos e diagnósticos conforme Regra 8). Para cada informação encontrar o código SNOMED CT (SCTID) correspondente em https://termbrowser.nhs.uk/?perspective=full&conceptId1=404684003&edition=uk-edition&release=v20250604&server=https://termbrowser.nhs.uk/sct-browser-api/snomed&langRefset=999001261000000100,999000691000001104, use "NotFound" se não encontrar, e anote o texto original e gere listas em formato de tuplas detalhadas.

**Definições:**
*   **Sinal ou Sintoma**: observação do médico ou relato do paciente de uma condição (Ex: icterícia, dor, febre), incluindo achados de exame físico (Ex: `Mucosas úmidas e hipocoradas`) mas exclui achados auscultatórios ou percussórios detalhados (Ver Regra 8).
*   **Doença ou Síndrome**: Alteração do estado normal de saúde, diagnosticada clinicamente (Ex: HAS, ICC, DM, DAC, pneumonia). Inclui síndromes reconhecidas (Ex: síndrome metabólica). Exclui achados descritivos de exames complementares (Ver Regra 8).

**Instruções Detalhadas:**

1.  **Identificação:** Leia o texto clínico e identifique todos os termos que correspondam às definições de "Sinal ou Sintoma" ou "Doença ou Síndrome", **seguindo estritamente TODAS as Regras e Observações Específicas abaixo, especialmente a Regra 8 restritiva sobre achados de exames e procedimentos**. Preste atenção especial a abreviações médicas comuns (ex: HAS, IAM, ICC, DM, DAC).
2.  **Processamento do Termo:**
    *   Se o termo for uma abreviação conhecida de uma **Doença/Síndrome permitida** (ex: HAS, DM), use a abreviação como 'TermoPrincipal'. Tente encontrar a expansão e registre-a em 'Abreviação'. Se não conhecida, use a abreviação.
    *   Se o termo for um **Sinal/Sintoma permitido** (ex: dispneia, icterícia) ou uma **Doença/Síndrome permitida não abreviada** (ex: pneumonia), use o termo completo como 'TermoPrincipal'. Registre `None` em 'Abreviação'.
3.  **Classificação:** Para cada termo principal identificado e **permitido pelas regras**, classifique-o como "Sinal ou Sintoma" ou "Doença ou Síndrome".
4.  **Busca SNOMED CT:** Tente encontrar o SCTID para o termo principal identificado e permitido. Use "NotFound" se não encontrar.
5.  **Tratamento de Pontuação:** Ignore pontuação externa. Mantenha a interna se fizer parte de um termo composto *permitido* (raro com a nova Regra 8, exceto talvez em nomes de síndromes).
6.  **Formatação da Saída (Texto Anotado):** Modifique o texto original inserindo a anotação logo após cada termo **identificado e permitido**, usando o formato EXATO: `[Texto analisado: TermoPrincipal | Abreviação: ExpansaoOuAbrevPropriaOuNone | Categoria: Categoria | SCTID: CodigoOuNotFound]`
    *   *Exemplo Doença Abrev.:* `HAS [Texto analisado: HAS | Abreviação: Hipertensão Arterial Sistêmica | Categoria: Doença ou Síndrome | SCTID: 38341003]`
    *   *Exemplo Sinal:* `icterícia [Texto analisado: icterícia | Abreviação: None | Categoria: Sinal ou Sintoma | SCTID: 18165001]`
7.  **Formatação da Saída (Listas Resumo em Tuplas):** Após o texto anotado, gere as duas listas de resumo apenas com os termos **identificados e permitidos**, no formato exato:
    *   `Sinais ou Sintomas: ([Termo1 | Abrev1 | Cat1 | SCTID1], ...)`
    *   `Doenças ou Síndromes: ([TermoA | AbrevA | CatA | SCTIDA], ...)`
    *   Use `()` se nenhuma entidade permitida for encontrada para uma categoria.
8.  **Substituição de Quebras de Linha:** No texto anotado final, substitua `\\n` por espaço.

**Regras e Observações Específicas:**

*   **Regra 1 (Não Anotar Normalidade Geral):** NÃO anotar estados *gerais* de saúde normal ou achados normais *isolados* (Ex: `BEG`, `CORADA`, `LOTE`, `MV presente e simétrico`). *Exceção:* Achados compostos como na Regra 7, se o componente anormal for um sinal permitido.
*   **Regra 2 (Não Anotar Medições/Testes):** NÃO anotar medições, valores de laboratório, ou nomes de testes (Ex: `FE 35%`, `PA 145/95`, `ecocardiograma`, `Tomografia`).
*   **Regra 3 (Não Anotar Verbos de Evolução):** NÃO anotar verbos como `melhorar`, `piorar`. Anote o conceito clínico *permitido* associado.
*   **Regra 4 (Termos Compostos - Restrita):** Identifique termos compostos **apenas se** representarem um *único* sinal clínico observável permitido (Regra 7/8) ou uma síndrome/doença nomeada. A Regra 8 prevalece sobre achados de exames.
*   **Regra 5 (Ignorar "Quadro de" / "Histórico de"):** Anote o conceito principal *se* ele for permitido pelas outras regras (Ex: `Quadro de dispneia` -> Anotar `dispneia`; `Hx de fratura` -> Não anotar, pois 'fratura' isolada pode ser considerada achado de exame). *Nota: Modificado pela Regra 8*.
*   **Regra 6 (Anotar "Sinais de..."):** Continue anotando expressões como `Sinais clínicos de X` ou `Sinais de X` como um único "Sinal ou Sintoma", *mesmo que X seja uma doença*. Isso é considerado um sinal clínico composto. (Ex: `Sinais clínicos de insuficiência cardíaca`).
*   **Regra 7 (Termos Compostos com Adjetivos/Achados Normais - Restrita):** Anote termos compostos **apenas se** descreverem um sinal clínico diretamente observável e permitido pela Regra 8.
    *   *Exemplo Permitido:* `Mucosas úmidas e hipocoradas` -> Anotar `Mucosas úmidas e hipocoradas` (Sinal/Sintoma - sinal clínico observável).
    *   *Exemplo NÃO Permitido (agora):* `CPP – MV+ BILATERAL, CREPITANTES EM BASE DIREITA` -> Não anotar (Achado auscultatório detalhado, excluído pela Regra 8).
*   **Regra 8 (Restrição Severa em Achados de Testes/Exames e Procedimentos):** Esta regra **SOBREPÕE** outras regras quando aplicável a achados de exames complementares, achados específicos de exame físico (como ausculta), ou procedimentos.
    *   **NÃO INCLUIR / NÃO ANOTAR:**
        *   **Achados descritos em exames complementares:** Qualquer detalhe interno de relatórios de ecocardiograma, tomografia, ressonância, exames laboratoriais, etc. (Ex: `folhetos espessados`, `refluxo discreto`, `cúspides calcificadas`, `dupla lesão`, `VE hipertrofiado`, `alt de relaxamento`, `AD aumentado`, `lesão nodular`, `infiltrado pulmonar`, `anemia` *se apenas reportada como valor laboratorial*, `hipocalemia`).
        *   **Termos morfológicos ou funcionais isolados de exames:** `espessados`, `hipertrofiado`, `calcificado`, `alterado`, `discreto`, `acentuado`, `reduzido`, `aumentado`, etc., quando derivados de exames.
        *   **Achados específicos de exame físico não diretamente observáveis como sinal:** Achados de ausculta pulmonar ou cardíaca (Ex: `MV+ BILATERAL, CREPITANTES EM BASE DIRE DIREITA`, `MVB+, DIFUSAMENTE DIMINUIDO`, `bulhas normofonéticas`, `sopro sistólico`), achados de percussão (Ex: `macicez`), palpação detalhada de órgãos internos se não for um sinal claro como `hepatomegalia`.
        *   **Nomes de Procedimentos ou Cirurgias:** `angioplastia`, `implante de marcapasso`, `cateterismo` (`cat`), `biópsia`.
        *   **Nomes de Testes ou resultados complexos de testes:** `ecg de repouso com bav de 2 grau mobitz 2`, `eletrocardiograma`.
    *   **INCLUIR / ANOTAR APENAS:**
        *   **Sinais clínicos observáveis ou facilmente verificáveis pelo profissional:** `taquicardia`, `icterícia`, `cianose`, `edema` (Ex: `edema em MMII`), `palidez`, `sudorese`, `dispneia` (observada ou referida), `tosse` (observada ou referida), `febre`, `Mucosas úmidas e hipocoradas`.
        *   **Sintomas referidos pelo paciente:** `dor` (Ex: `dor abdominal`, `dor torácica`), `fadiga`, `náusea`, `vômito`, `tontura`, `cefaleia`, `azia`.
        *   **Doenças diagnosticadas (geralmente crônicas ou agudas estabelecidas):** `Diabetes Mellitus` (`DM`), `Hipertensão Arterial Sistêmica` (`HAS`), `Insuficiência Cardíaca Congestiva` (`ICC`), `Doença Pulmonar Obstrutiva Crônica` (`DPOC`), `Doença Arterial Coronariana` (`DAC`), `pneumonia`, `infarto agudo do miocárdio` (`IAM`).
        *   **Síndromes clinicamente reconhecidas:** `Síndrome metabólica`, `Síndrome de Cushing`, `Síndrome de Down`.
    *   **Exemplos de Aplicação da Regra 8:**
        *   *Texto:* `Ecocardio (13/02/15): ... VMi = folhetos espessados, abertura preservada, refluxo discreto, ... VAo = cúspides calcificadas, com dupla lesão; ... VE = hipertrofiado, ..., alt de relaxamento. AD = aumentado.` -> **Não anotar NADA** deste trecho.
        *   *Texto:* `Mucosas úmidas e hipocoradas` -> **Anotar** `Mucosas úmidas e hipocoradas` [Texto analisado: Mucosas úmidas e hipocoradas | Abreviação: None | Categoria: Sinal ou Sintoma | SCTID: NotFound] (Sinal clínico observável).
        *   *Texto:* `CPP – MV+ BILATERAL, CREPITANTES EM BASE DIREITA` -> **Não anotar**. (Achado auscultatório).
        *   *Texto:* `Sinais clínicos de insuficiência cardíaca` -> **Anotar** `Sinais clínicos de insuficiência cardíaca` [Texto analisado: Sinais clínicos de insuficiência cardíaca | Abreviação: None | Categoria: Sinal ou Sintoma | SCTID: NotFound] (Permitido pela Regra 6).
        *   *Texto:* `MVB+, DIFUSAMENTE DIMUIDO;` -> **Não anotar**. (Achado auscultatório).
        *   *Texto:* `Realizou angioplastia. ECG de repouso com bav de 2 grau mobitz 2. Fez cat. Paciente com DM, HAS e DAC.` -> **Anotar apenas** `DM` [Texto analisado: DM | Abreviação: Diabetes Mellitus | Categoria: Doença ou Síndrome | SCTID: 44054006], `HAS` [Texto analisado: HAS | Abreviação: Hipertensão Arterial Sistêmica | Categoria: Doença ou Síndrome | SCTID: 38341003], `DAC` [Texto analisado: DAC | Abreviação: Doença Arterial Coronariana | Categoria: Doença ou Síndrome | SCTID: 53741008]. Ignorar `angioplastia`, `ECG...`, `cat`.
*   **Regra 9 (NÃO anotar Conceitos Negados ou Ausentes):** Não anotar conceitos clínicos negados, mesmo que pertença a uma das categorias **permitidas** (sinal clínico observável/referido, sintoma, doença diagnosticada, síndrome).
    *   *Exemplos negados que NÃO devem ser anotado:* `sem tosse`, `nega dor`, `afebril`, `assintomático`.
*   **Regra 10 (NÃO anotar Medicamentos):** Não anotar medicamentos presentes na narrativa. Nem interpretar e inferir um diagnóstico a partir de um medicamento.
    *   *Exemplos medicamentos que NÃO devem ser anotados:* `ancoron`, `svt`.

**Restrições Importantes:**
*   NÃO retorne NENHUMA informação adicional, comentários, explicações ou CUIs.
*   NÃO retorne NENHUMA categoria diferente de sinais/sintomas ou doenças/síndromes **permitidos pelas regras**.
*   Retorne APENAS o texto anotado seguido pelas listas de resumo em formato de tupla, conforme especificado, contendo **apenas as entidades permitidas**.
*   Siga rigorosamente os formatos de anotação e das tuplas de resumo.

**Exemplo de Execução (Refletindo Novas Regras):**

***** Texto original de Exemplo:
Paciente com HAS e ICC diagnosticada. Apresenta dispneia aos esforços e edema em MMII. Nega dor torácica. Afebril. BEG. Exame Pulmonar: MV diminuído em bases. Ecocardiograma mostrou FE=35% e hipertrofia VE. Ex-tabagista. Realizou angioplastia prévia.

***** Saída Esperada:
Paciente com HAS [Texto analisado: HAS | Abreviação: Hipertensão Arterial Sistêmica | Categoria: Doença ou Síndrome | SCTID: 38341003] e ICC [Texto analisado: ICC | Abreviação: Insuficiência Cardíaca Congestiva | Categoria: Doença ou Síndrome | SCTID: 42343007] diagnosticada. Apresenta dispneia [Texto analisado: dispneia | Abreviação: None | Categoria: Sinal ou Sintoma | SCTID: 267036007] aos esforços e edema em MMII [Texto analisado: edema em MMII | Abreviação: None | Categoria: Sinal ou Sintoma | SCTID: 271808008]. Nega dor torácica. Afebril. BEG. Exame Pulmonar: MV diminuído em bases. Ecocardiograma mostrou FE=35% e hipertrofia VE. Ex-tabagista. Realizou angioplastia prévia.

Sinais ou Sintomas: ([dispneia | None | Sinal ou Sintoma | 267036007], [edema em MMII | None | Sinal ou Sintoma | 271808008]
Doenças ou Síndromes: ([HAS | Hipertensão Arterial Sistêmica | Doença ou Síndrome | 38341003], [ICC | Insuficiência Cardíaca Congestiva | Doença ou Síndrome | 42343007])

---------- FIM DO EXEMPLO ----------

**Tarefa:** Agora, aplique TODAS essas definições, instruções e regras **restritivas** ao seguinte documento clínico. Retorne APENAS o texto anotado e as listas de resumo em formato de tupla detalhada no formato especificado, contendo somente as entidades permitidas.

**Documento Clínico:**
{textoClinico}
"""