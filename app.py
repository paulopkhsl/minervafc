import streamlit as st

def gerar_prompt(assunto, materia, bullet_topics, output_format, card_detail_level, question_style, content_focus, language,
                 include_common_mistakes, tags, difficulty_level, include_exam_context):
    prompt = f"""
Você é um assistente especializado em criar flashcards de estudo para o ENEM, com saída pronta para download como arquivo .txt, formatado para importação direta no AnkiDroid.

📌 DADOS DO USUÁRIO:
- Assunto Principal: {assunto}
- Matéria: {materia}
- Tópicos com Detalhamento (incluindo sub-tópicos, se houver):
{bullet_topics}

---

📌 INSTRUÇÕES ABSOLUTAS SOBRE O FORMATO DE ENTREGA:

✅ Sua resposta deve ser entregue como um arquivo de texto (.txt), pronto para o usuário baixar imediatamente.

✅ Nome do arquivo: **flashcards_ENEM.txt**

✅ Formato de cada linha do arquivo:

- Cada flashcard deve ocupar uma única linha.
- Campo 1: Frente da pergunta.
- Campo 2: Verso da resposta completa (explicação, grau de dificuldade, contexto ENEM, exemplos, etc).
- Os campos devem ser separados por **um caractere real de tabulação (TAB real - ASCII 9)**.
- Não use espaços, múltiplos espaços ou caracteres como "\\t" para separar os campos. Apenas TAB real.

✅ Regras sobre o conteúdo de cada campo:

- Nenhum campo deve conter quebras de linha internas.
- Toda a resposta (verso) deve ser entregue numa única linha.
- As respostas podem ser longas, com explicações, mas devem ficar dentro de um só campo.

✅ Estrutura de conteúdo por flashcard:

- Pergunta clara e objetiva (frente).
- Resposta completa e bem explicada (verso).
- Ao final da resposta, inclua:
  - Grau de Dificuldade: (Básico / Intermediário / Avançado)
  - Contexto ENEM: (Explique como o tema costuma ser cobrado na prova)

✅ O número de flashcards deve ser adequado ao nível de detalhamento dos tópicos e sub-tópicos informados.

✅ Não inclua:
- Cabeçalhos
- Numerações de flashcards
- Textos de introdução
- Instruções
- Mensagens extras antes ou depois das linhas de flashcards.

✅ ENTREGUE APENAS O ARQUIVO .TXT, PRONTO PARA DOWNLOAD.

---

📌 EXEMPLO EXATO DE COMO CADA LINHA DO ARQUIVO DEVE FICAR (SEPARADO POR TAB REAL):

O que é fotossíntese?    É o processo pelo qual plantas, algas e algumas bactérias convertem energia solar em energia química, produzindo glicose e oxigênio. Grau: Básico. Contexto ENEM: O ENEM costuma cobrar relações entre fotossíntese e o ciclo do carbono, além de impactos ambientais.

Quais são as etapas da fotossíntese?    A fotossíntese ocorre em duas etapas principais: fase clara (captura de energia solar e produção de ATP e NADPH) e fase escura (fixação do carbono para formar glicose). Grau: Intermediário. Contexto ENEM: Costuma aparecer em questões sobre metabolismo energético em vegetais.

---

📌 SAÍDA FINAL OBRIGATÓRIA:
Saída esperada: um arquivo de texto para download
✅ Apenas o arquivo .txt, com os flashcards no formato exato acima.
✅ Nenhum texto adicional.
✅ Entregue de forma que o usuário possa fazer o download direto.

"""
    return prompt.strip()

def main():
    st.set_page_config(page_title="Gerador de Flashcards ENEM", layout="centered")

    st.title("📇 Gerador de Prompt para Flashcards ENEM")
    st.markdown("Crie prompts personalizados para gerar flashcards (.txt pronto para AnkiDroid) para seus estudos do ENEM.")

    st.markdown("---")
    st.subheader("📝 Dados do Flashcard")

    assunto = st.text_input("Assunto Principal (ex: Geomorfologia):", placeholder="Geomorfologia")
    materia = st.text_input("Matéria (ex: Geografia):", placeholder="Geografia")

    st.markdown("---")
    st.subheader("📚 Tópicos Detalhados")
    st.markdown("""
    Digite os tópicos com detalhamento (incluindo sub-tópicos, se quiser).
    **Formato sugerido:**
    ```
    Terremotos: como ocorrem; tipos;
    Dinâmica de Placas:
    Orogênese: convergência, divergência;
    Epirogênese: positiva, negativa
    ```
    """)
    bullet_topics = st.text_area("Tópicos:", height=200, placeholder="Digite seus tópicos aqui, um por linha ou com sub-tópicos.")

    st.markdown("---")
    st.subheader("⚙️ Configurações Adicionais")

    col1, col2 = st.columns(2)

    with col1:
        output_formats = [
            "txt com tabulação para AnkiDroid",
            "csv para Excel",
            "markdown simples"
        ]
        output_format = st.selectbox("Formato de saída:", output_formats)

        card_detail_levels = [
            "1 flashcard resumo por tópico",
            "múltiplos flashcards detalhados por tópico"
        ]
        card_detail_level = st.selectbox("Número de flashcards por tópico:", card_detail_levels)

        question_styles = [
            "Direto",
            "Contextual",
            "Misto"
        ]
        question_style = st.selectbox("Estilo das perguntas:", question_styles)

    with col2:
        content_focuses = [
            "Definições conceituais",
            "Exemplos de aplicação no ENEM",
            "Erros comuns e pegadinhas",
            "Definições + Exemplos",
            "Definições + Exemplos + Erros comuns"
        ]
        content_focus = st.selectbox("Foco do conteúdo:", content_focuses)

        languages = [
            "Português (Brasil)",
            "Inglês",
            "Espanhol"
        ]
        language = st.selectbox("Idioma:", languages)

    st.markdown("---")
    st.subheader("➕ Opções de Conteúdo")

    col3, col4 = st.columns(2)
    with col3:
        include_common_mistakes = st.checkbox("Incluir erros comuns e pegadinhas?", value=True)
        tags = st.checkbox("Adicionar tags por tema?", value=True)
    with col4:
        difficulty_level = st.checkbox("Indicar grau de dificuldade (Básico/Intermediário/Avançado)?", value=True)
        include_exam_context = st.checkbox("Incluir contexto de prova (ex: como o ENEM cobra esse tema)?", value=True)

    st.markdown("---")

    if st.button("Gerar Prompt"):
        if not assunto or not materia or not bullet_topics.strip():
            st.warning("Por favor, preencha o Assunto Principal, a Matéria e os Tópicos para gerar o prompt.")
        else:
            # Convertendo os booleanos de volta para "Sim"/"Não" para a função gerar_prompt
            # (Streamlit checkboxes retornam True/False)
            _include_common_mistakes = "Sim" if include_common_mistakes else "Não"
            _tags = "Sim" if tags else "Não"
            _difficulty_level = "Sim" if difficulty_level else "Não"
            _include_exam_context = "Sim" if include_exam_context else "Não"


            prompt_gerado = gerar_prompt(
                assunto, materia, bullet_topics, output_format, card_detail_level, question_style, content_focus,
                language, _include_common_mistakes, _tags, _difficulty_level, _include_exam_context
            )

            st.subheader("✨ Seu Prompt Gerado:")
            st.code(prompt_gerado, language="text")

            # Botão para copiar o prompt
            st.download_button(
                label="Copiar Prompt",
                data=prompt_gerado,
                file_name="prompt_flashcards_enem.txt",
                mime="text/plain"
            )

            st.info("Copie o prompt acima e cole em sua IA de preferência (ex: Gemini, ChatGPT) para gerar os flashcards!")

if __name__ == "__main__":
    main()