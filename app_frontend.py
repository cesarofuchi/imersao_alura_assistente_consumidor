import streamlit as st
# Importa a classe do backend ADK
from backend_agent_consumer_defense import ConsumerChatADK, GOOGLE_API_KEY, data_atual_formatada 
import os

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Assistente de Defesa ao Consumidor",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("⚖️ Assistente de Defesa ao Consumidor")
st.caption("Seu assistente virtual para questões de Direito do Consumidor no Brasil")

# --- Verificação da API Key (Apenas informativo para o usuário) ---
if not GOOGLE_API_KEY:
    st.error(
        "A variável de ambiente GOOGLE_API_KEY não está definida. "
        "O assistente pode não funcionar corretamente. "
        "Por favor, configure-a e reinicie o aplicativo Streamlit."
    )
    # Você pode desabilitar a entrada do chat aqui se a API Key for estritamente necessária
    # st.stop()


# --- Gerenciamento do Estado da Sessão ---
if 'consumer_bot_adk' not in st.session_state:
    try:
        # Verifica se o ADK foi importado corretamente no backend
        # Esta é uma forma indireta, verificando se uma classe principal do ADK existe no módulo
        from google.adk.agents import Agent as ADKAgentTest
        if not hasattr(ADKAgentTest, '__call__'): # Se for a dummy
            raise ImportError("ADK classes dummy foram usadas. Backend não funcional.")

        st.session_state.consumer_bot_adk = ConsumerChatADK(user_id="streamlit_user_01")
        st.session_state.chat_history_adk = [{
            "role": "assistant",
            "content": "Olá! Sou o Assistente de Defesa do Consumidor. Para que eu possa te ajudar, por favor, me conte em detalhes o problema que você está enfrentando."
        }]
        st.session_state.error_message_adk = None
    except ImportError as ie: # Captura o erro de importação do ADK se as classes dummy foram ativadas
        st.session_state.consumer_bot_adk = None
        st.session_state.chat_history_adk = []
        st.session_state.error_message_adk = (
            "Erro ao inicializar o assistente: O framework 'google.adk' não parece estar instalado ou configurado corretamente. "
            "Verifique os logs do console para mais detalhes."
        )
        st.error(st.session_state.error_message_adk)
        print(f"DEBUG ImportError: {ie}")
    except Exception as e:
        st.session_state.consumer_bot_adk = None
        st.session_state.chat_history_adk = []
        st.session_state.error_message_adk = f"Erro crítico ao inicializar o assistente ADK: {e}. Verifique sua API Key e a configuração do ADK."
        st.error(st.session_state.error_message_adk)
        import traceback
        print("--- TRACEBACK ERRO STREAMLIT INIT ---")
        traceback.print_exc()
        print("------------------------------------")


# --- Exibição do Histórico da Conversa ---
if st.session_state.get("consumer_bot_adk") and st.session_state.get("chat_history_adk"):
    for message in st.session_state.chat_history_adk:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    if st.session_state.get("error_message_adk"):
        st.error(st.session_state.error_message_adk) # Mostra o erro se o bot não carregou
    else:
        # Este caso pode ocorrer se consumer_bot_adk for None mas não houver erro_message_adk (improvável com a lógica atual)
        st.warning("O assistente não pôde ser carregado. Verifique a configuração.")


# --- Entrada do Usuário ---
user_prompt = st.chat_input("Descreva seu problema aqui...")

if user_prompt and st.session_state.get("consumer_bot_adk"):
    st.session_state.chat_history_adk.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.spinner("Analisando sua situação com o agente ..."):
        # Chama o método send_message do nosso bot ADK
        ai_response = st.session_state.consumer_bot_adk.send_message(user_prompt)

    st.session_state.chat_history_adk.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
    
    # Força o rerender para exibir a última mensagem (Streamlit >1.1 reruns chat_input automatically)
    # st.rerun() # Descomente se necessário para versões mais antigas do Streamlit

elif user_prompt and not st.session_state.get("consumer_bot_adk"):
    st.error("O assistente não está disponível. Verifique a mensagem de erro acima e os logs do console.")


# --- Informações Adicionais na Barra Lateral (Opcional) ---
st.sidebar.header("Sobre o Assistente de Defensa do Consumidor")
st.sidebar.info(
    "Este é um protótipo de assistente virtual para Direito do Consumidor, "
    "utilizando o framework de Agentes do Google (ADK) e a API Gemini. "
    "As informações são para orientação e não substituem um profissional."
)
st.sidebar.markdown("---")
st.sidebar.subheader("Lembre-se:")
st.sidebar.markdown(
    """
    - **Guarde Provas:** Notas fiscais, contratos, e-mails, protocolos.
    - **Tente Resolver Amigavelmente:** Contato direto com o fornecedor.
    - **Conheça seus Prazos:** Para reclamar, cancelar, garantia.
    """
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Data de referência do conhecimento do AI: {data_atual_formatada}")