import streamlit as st
import google.generativeai as genai
import os

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Gerador de Flashcards ENEM", layout="centered")

# --- Função de Geração de Prompt ---
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
- **CRÍTICO: Os campos DEVEM ser separados EXCLUSIVAMENTE por UM caractere real de TABULAÇÃO (TAB real - ASCII 9). JAMAIS use quebras de linha, espaços extras, ou outros delimitadores para separar os campos. APENAS TAB REAL.**
- Não use caracteres como "\\t" para simular tab, use o caractere de tabulação literal.

✅ Regras sobre o conteúdo de cada campo:

- **Nenhum campo deve conter quebras de linha internas. Absolutamente nenhuma nova linha dentro da pergunta ou da resposta. Todas as informações de um campo devem estar em uma única linha contínua.**
- Toda a resposta (verso) deve ser entregue numa única linha.
- As respostas podem ser longas, com explicações detalhadas, mas devem permanecer dentro de um só campo, sem quebras de linha.

✅ Estrutura de conteúdo por flashcard:

- Pergunta clara e objetiva (frente).
- Resposta completa e bem explicada (verso).
- Ao final da resposta, inclua **OBRIGATORIAMENTE**:
  - Grau de Dificuldade: (Básico / Intermediário / Avançado)
  - Contexto ENEM: (Explique como o tema costuma ser cobrado na prova)

✅ O número de flashcards deve ser adequado ao nível de detalhamento dos tópicos e sub-tópicos informados.

✅ Não inclua:
- Cabeçalhos
- Numerações de flashcards
- Textos de introdução
- Instruções (como esta)
- Mensagens extras antes ou depois das linhas de flashcards.

✅ ENTREGUE APENAS O CONTEÚDO DO ARQUIVO .TXT, PRONTO PARA DOWNLOAD.
✅ A resposta deve começar imediatamente com o primeiro flashcard, sem preâmbulos ou qualquer texto antes da primeira linha de flashcard.

---

📌 EXEMPLO EXATO DE COMO CADA LINHA DO ARQUIVO DEVE FICAR (SEPARADO POR TAB REAL):

O que é fotossíntese?    É o processo pelo qual plantas, algas e algumas bactérias convertem energia solar em energia química, produzindo glicose e oxigênio. Grau: Básico. Contexto ENEM: O ENEM costuma cobrar relações entre fotossíntese e o ciclo do carbono, além de impactos ambientais.
Quais são as etapas da fotossíntese?    A fotossíntese ocorre em duas etapas principais: fase clara (captura de energia solar e produção de ATP e NADPH) e fase escura (fixação do carbono para formar glicose). Grau: Intermediário. Contexto ENEM: Costuma aparecer em questões sobre metabolismo energético em vegetais.

---

📌 SAÍDA FINAL OBRIGATÓRIA:
Saída esperada: um arquivo de texto para download.
✅ Apenas o arquivo .txt, com os flashcards no formato exato acima.
✅ Nenhum texto adicional.
✅ Entregue de forma que o usuário possa fazer o download direto.
"""
    return prompt.strip()

# --- Função para chamar a API do Gemini ---
def get_flashcards_from_gemini(prompt):
    try:
        # Verifica se a chave de API está configurada nos Streamlit Secrets
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Chave de API do Gemini não encontrada nos Streamlit Secrets. Por favor, adicione-a.")
            return None

        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        # Usando o modelo gemini-1.5-pro-latest, que é robusto para seguir instruções
        model_name_to_use = 'models/gemini-1.5-flash-latest'
        
        # Opcional: Para depuração, pode descomentar a linha abaixo para ver qual modelo está sendo usado
        # st.info(f"Usando o modelo: {model_name_to_use}")

        model = genai.GenerativeModel(model_name_to_use)

        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            return response.text
        else:
            st.error("A IA retornou uma resposta vazia ou em formato inesperado.")
            # Para debug, exibe a resposta bruta da IA se estiver vazia
            st.write(f"Resposta bruta da IA: {response}") 
            return None

    except Exception as e:
        st.error(f"Ocorreu um erro ao chamar a IA: {e}")
        st.info("Verifique se sua chave de API do Gemini está configurada corretamente nos Streamlit Secrets e se o modelo que estamos tentando usar está acessível para sua conta/região.")
        return None

# --- Função de Pós-processamento para garantir o formato correto ---
def clean_flashcard_output(raw_text):
    cleaned_lines = []
    # Divide o texto em linhas
    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip() # Remove espaços e quebras de linha no início/fim da linha

        # Ignora linhas vazias
        if not line:
            continue
        
        # Substitui qualquer quebra de linha ou retorno de carro remanescente DENTRO de uma linha
        # por um espaço, para garantir que o conteúdo do campo esteja em uma única linha.
        line = line.replace('\n', ' ').replace('\r', ' ').strip()
        
        # Garante que haja apenas um tab entre a pergunta e a resposta.
        # Isso é uma heurística caso a IA falhe em usar um tab, mas use espaços ou múltiplos tabs.
        # O ideal é que a IA já entregue no formato correto, mas isso é uma segurança.
        parts = line.split('\t') # Divide por todos os tabs
        
        if len(parts) >= 2: # Se encontrou pelo menos um tab, assume que os campos estão lá
            # Juntar as partes com um único tab, garantindo que não haja tabs extras
            # e que o conteúdo de cada parte esteja limpo de novas linhas internas.
            cleaned_part_0 = parts[0].strip()
            cleaned_part_1 = " ".join(part.strip() for part in parts[1:]) # Junta o restante como a parte da resposta
            
            cleaned_lines.append(f"{cleaned_part_0}\t{cleaned_part_1}")
        else:
            # Se não encontrou tab (ex: a IA usou 'enter' ou só espaços), isso é um problema maior.
            # Aqui, para o AnkiDroid, a única forma de garantir é que cada linha seja um flashcard
            # ou que se tente uma heurística para dividir a linha em dois campos.
            # No contexto do Anki, se não há um tab, a linha inteira pode virar a frente.
            # O mais seguro é que a IA gere o tab. Este pós-processamento foca em limpar *novas linhas internas*.
            # Se a IA consistentemente não usa tabs, o prompt precisa de mais ajustes ainda.
            
            # Para este cenário, se não há tab, vamos assumir que a linha inteira é um campo
            # e vamos deixá-la como está, pois pode ser uma linha de flashcard "quebrada"
            # que a IA deveria ter formatado com tab.
            # No entanto, a instrução do prompt é para ter TAB. Se não tiver, o Anki falha.
            # Portanto, a correção principal é o prompt. Este pós-processamento ajuda no 'inner-newline'.
            if line: # Adiciona a linha só se ela não estiver vazia após o strip
                 cleaned_lines.append(line)

    # Rejunta as linhas para o download, separadas por '\n'
    return "\n".join(cleaned_lines)

# --- Interface Principal do Streamlit ---
def main():
    st.title("📇 Gerador de Flashcards ENEM (com IA)")
    st.markdown("Configure seus flashcards e deixe a IA gerá-los para você, prontos para importação no AnkiDroid!")

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
            "txt com tabulação para AnkiDroid"
        ]
        output_format = st.selectbox("Formato de saída:", output_formats, help="O prompt é otimizado para .txt com tabulação para AnkiDroid.")

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

    # Botão para gerar os flashcards
    if st.button("✨ Gerar Flashcards com IA"):
        if not assunto or not materia or not bullet_topics.strip():
            st.warning("Por favor, preencha o Assunto Principal, a Matéria e os Tópicos para gerar os flashcards.")
        else:
            # Convertendo os booleanos de volta para "Sim"/"Não" para a função gerar_prompt
            _include_common_mistakes = "Sim" if include_common_mistakes else "Não"
            _tags = "Sim" if tags else "Não"
            _difficulty_level = "Sim" if difficulty_level else "Não"
            _include_exam_context = "Sim" if include_exam_context else "Não"

            # Gera o prompt
            prompt_para_ia = gerar_prompt(
                assunto, materia, bullet_topics, output_format, card_detail_level, question_style, content_focus,
                language, _include_common_mistakes, _tags, _difficulty_level, _include_exam_context
            )

            with st.spinner("Gerando seus flashcards... isso pode levar um momento. ⏳"):
                # Chama a IA com o prompt
                flashcards_raw_text = get_flashcards_from_gemini(prompt_para_ia)

            if flashcards_raw_text:
                # Aplica a função de pós-processamento para garantir o formato
                flashcards_final_text = clean_flashcard_output(flashcards_raw_text)
                
                st.subheader("✅ Flashcards Gerados!")
                st.text_area("Conteúdo dos Flashcards:", flashcards_final_text, height=300)

                # Botão para download do arquivo .txt
                st.download_button(
                    label="💾 Baixar Flashcards (.txt para AnkiDroid)",
                    data=flashcards_final_text.encode('utf-8'), # Use o texto final limpo aqui
                    file_name="flashcards_ENEM.txt",
                    mime="text/plain"
                )
                st.success("Seus flashcards estão prontos! Baixe o arquivo e importe no AnkiDroid.")
            else:
                st.error("Não foi possível gerar os flashcards. Por favor, tente novamente ou verifique as configurações da API.")

if __name__ == "__main__":
    main()