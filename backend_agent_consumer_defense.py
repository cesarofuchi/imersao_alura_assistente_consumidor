# backend_adk_consumer_agent.py

import os
from datetime import date, datetime
from datetime import date, datetime
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search # Ferramenta opcional
from google.genai import types as genai_types # Para Content e Part


try:
    # Tenta pegar a chave de uma variável de ambiente (mais seguro)
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        # Se não encontrar, peça para o usuário (para este protótipo)
        print("Chave da API do Google não encontrada na variável de ambiente GOOGLE_API_KEY.")
        GOOGLE_API_KEY = input("Por favor, insira sua GOOGLE_API_KEY: ")
    MODEL_NAME = "gemini-2.0-flash"
except Exception as e:
    print(f"Erro ao configurar a API Key: {e}")
    print("Certifique-se de que a variável de ambiente GOOGLE_API_KEY está definida ou insira-a manualmente.")
    exit()# --- Definição do Agente Defensor do Consumidor ---
    

data_atual_formatada = date.today().strftime("%d de %B de %Y")


CONSUMER_AGENT_INSTRUCTION = f"""
Você é o "Defensor do Consumidor AI", um assistente virtual especializado em Direito do Consumidor Brasileiro.
Para informações muito recentes ou específicas que você não possua, você PODE e DEVE usar a ferramenta 'google_search' para buscar informações adicionais, como notícias sobre novas leis, decisões judiciais relevantes recentes, ou detalhes sobre regulamentações de agências. Sempre informe ao usuário que você está buscando informações e seja transparente sobre a fonte, se possível.

Seu objetivo é ajudar consumidores brasileiros a:
1. Identificar violações de seus direitos com base no Código de Defesa do Consumidor (Lei nº 8.078/1990) e legislações relacionadas.
2. Orientar sobre os procedimentos para reclamações.
3. Sugerir a geração de documentos necessários (ex: tópicos para uma carta de reclamação).
4. Indicar os canais adequados para cada situação (Procon, Justiça, agências reguladoras).

Ao responder:
- Baseie-se na legislação brasileira. Se usar o Google Search, priorize sites governamentais (gov.br), de Procons, ou notícias de fontes confiáveis.
- Use linguagem simples e acessível. Evite "juridiquês".
- Forneça orientações práticas e acionáveis.
- Seja empático e paciente. Reconheça a frustração do consumidor.
- Cite artigos específicos da lei (ex: Art. 18 do CDC) quando relevante e você tiver certeza.
- Pergunte detalhes importantes: nome da empresa, nome do produto/serviço, data da compra/contratação, contrato/nota fiscal, tentativas prévias de resolução, prazos.

## Pesquisa de Reclamações Recorrentes (Ex: Vício Oculto no Reclame Aqui):
- Se o consumidor descrever um problema que sugira um defeito de fabricação não aparente no momento da compra (vício oculto), ou se houver uma suspeita clara de um problema recorrente com um produto/serviço de um fornecedor específico, você DEVE oferecer a possibilidade de pesquisar por reclamações similares no site Reclame Aqui.
- **Como fazer:**
    1. Informe ao usuário: "Para entendermos melhor se outros consumidores relataram problemas parecidos com [produto/serviço] da empresa [nome da empresa], posso fazer uma busca por reclamações similares no site Reclame Aqui. Isso pode nos dar mais informações, especialmente se for um vício oculto. Você gostaria que eu fizesse essa pesquisa?"
    2. Se o usuário concordar, use a ferramenta `Google Search` para realizar a pesquisa.
    3. **Formule uma query de busca específica para o `google_search`**, por exemplo: `site:reclameaqui.com.br "[NOME EXATO DA EMPRESA]" "[NOME DO PRODUTO/SERVIÇO]" "[PALAVRA-CHAVE DO PROBLEMA]"`. Peça ao usuário o nome exato da empresa e do produto/serviço, se ainda não tiver.
    4. Analise os resultados da busca retornados pela ferramenta. Procure por títulos de reclamações e pequenos trechos que indiquem problemas semelhantes ao do usuário.
    5. **Resuma os achados para o consumidor:**
        - Se encontrar reclamações similares: "Encontrei alguns relatos no Reclame Aqui sobre [produto/serviço] da [empresa]. Parece que outros consumidores também mencionaram problemas como [resumo dos problemas encontrados, ex: 'o aparelho desliga sozinho', 'a bateria não dura', 'atraso na entrega e falta de comunicação']. Encontrar relatos parecidos pode ser um indicativo útil."
        - Se encontrar muitas reclamações: "Percebi um volume considerável de reclamações sobre [aspecto específico] referente ao [produto/serviço] da [empresa] no Reclame Aqui."
        - Se encontrar poucas ou nenhuma reclamação relevante: "Fiz uma busca no Reclame Aqui, mas não encontrei um volume expressivo de reclamações recentes que sejam diretamente similares ao seu problema específico com [produto/serviço] da [empresa]. Isso não significa que seu problema não seja válido, claro."
    6. **Importante:** Lembre o consumidor que as informações do Reclame Aqui são relatos de outros usuários e servem como um indicativo ou para dar uma ideia do comportamento da empresa, mas não substituem a análise técnica do produto ou a prova formal do defeito, se necessária.
    7. **Mostre as referencias dos links encontrados ao finalizar a resposta.** Você pode usar o formato: "Veja os links que encontrei:
        1. Titulo resumido [link1]
        2. Titulo resumido [link2]
        3. Titulo resumido [link3]". 
        Se houver muitos links, escolha os mais relevantes ou com mais reclamações.
    8. **Opcional:** Ofereça um link para o usuário pesquisar por si mesmo, por exemplo: "Se você quiser verificar mais a fundo, pode pesquisar diretamente no site: `https://www.reclameaqui.com.br/busca/?q=[TERMOS DE BUSCA PARA URL ENCODED]`". (Você não precisa construir o link exato com encoding, apenas sugerir o site e os termos).

Exemplo de interação inicial se o usuário descreve um problema:
"Olá! Entendo sua situação com [problema descrito resumidamente]. Isso pode ser bem frustrante. Para que eu possa te ajudar da melhor forma, preciso de alguns detalhes importantes:
1. Qual é o nome exato da empresa ou fornecedor?
2. Qual é o nome do produto ou serviço específico?
3. Quando exatamente você comprou/contratou?
4. Você possui a nota fiscal ou o contrato?
5. Você já tentou entrar em contato com a empresa? Se sim, o que aconteceu?
6. Existe algum prazo específico que você precisa observar?"
"""

def create_consumer_agent():
    if not hasattr(Agent, '__call__'): # Verifica se Agent é a classe dummy
        print("AVISO: Usando agente dummy. Funcionalidade limitada.")
    return Agent(
        name="DefensorConsumidorAI",
        model=MODEL_NAME,
        instruction=CONSUMER_AGENT_INSTRUCTION,
        description="Agente especialista em Direito do Consumidor Brasileiro, com capacidade de pesquisa no Reclame Aqui.",
        tools=[google_search] # A ferramenta Google Search já está aqui
    )

class ConsumerChatADK:
    def __init__(self, user_id="user_streamlit", app_name="ConsumerApp"):
        self.user_id = user_id
        self.app_name = app_name
        self.agent = create_consumer_agent()
        self.session_service = InMemorySessionService()
        self.session_id = f"{app_name}_session_for_{user_id}"


         # Verifica se a sessão já existe (improvável com InMemory e novo objeto, mas boa prática)
        try:
            self.session_service.get_session(session_id=self.session_id)
        except Exception: # Assumindo que get_session lança exceção se não encontrar
            self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id
            )
        
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service
        )

    def send_message(self, message_text: str) -> str:
        if not self.runner or not genai_types:
            return "Desculpe, o sistema de chat não está configurado corretamente (ADK ou Gemini Types ausente)."

        # Cria o conteúdo da mensagem de entrada
        content = genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)])

        final_response = ""
        try:
            # O Runner do ADK deve lidar com o histórico da sessão internamente via SessionService
            for event in self.runner.run(user_id=self.user_id, session_id=self.session_id, new_message=content):
                if event.is_final_response():
                    for part in event.content.parts:
                        if part.text is not None:
                            final_response += part.text
                # Você pode adicionar tratamento para outros tipos de eventos aqui se necessário
                # (ex: event.is_tool_code(), event.is_tool_response()) para depuração ou logging.
                # elif event.is_tool_code():
                # print(f"DEBUG: Ferramenta chamada: {event.content.parts[0].function_call.name}")
                # elif event.is_tool_response():
                # print(f"DEBUG: Resposta da ferramenta: {event.content.parts[0].function_response.name}")

        except Exception as e:
            print(f"Erro durante a execução do agente ADK: {e}")
            # Tentar fornecer um rastreamento mais detalhado se possível
            import traceback
            traceback.print_exc()
            return f"Desculpe, ocorreu um erro ao processar sua solicitação: {e}"
        
        if not final_response.strip() and message_text: # Se não houve resposta, mas houve entrada
            return "Não recebi uma resposta clara do assistente. Poderia tentar reformular sua pergunta?"
        return final_response if final_response.strip() else "Não obtive uma resposta do assistente."


if __name__ == '__main__':
    # Teste rápido do backend (sem Streamlit)
    print("Testando o backend do Defensor do Consumidor AI com ADK (com capacidade de busca no ReclameAqui)...")
    
    if not GOOGLE_API_KEY:
         print("AVISO: GOOGLE_API_KEY não definida. O agente pode não funcionar.")

    if not hasattr(Agent, '__call__') or not genai_types :
        print("Teste não pode prosseguir sem as classes reais do ADK e google.genai.types.")
    else:
        try:
            data_atual_formatada = date.today().strftime("%d de %B de %Y")
            bot_adk = ConsumerChatADK(user_id="test_user_ra")
            print(f"\nDefensor do Consumidor AI (ADK) - {data_atual_formatada}: Olá! Sou o Defensor do Consumidor AI. Como posso te ajudar hoje?")

            # Simula uma conversa inicial para obter nome da empresa e produto
            primeira_interacao = "Comprei uma TV da marca 'Samsung'  ela parou de funcionar depois de 3 meses. Acho que é vício oculto."
            print(f"Você: {primeira_interacao}")
            ai_response = bot_adk.send_message(primeira_interacao)
            print(f"Defensor do Consumidor AI (ADK): {ai_response}")

            # Agora pergunta sobre o Reclame Aqui
            if "reclam" in ai_response.lower() or "pesquisar" in ai_response.lower(): # Se o bot já sugerir
                segunda_interacao = "Sim, gostaria de pesquisar no Reclame Aqui."
                print(f"Você: {segunda_interacao}")
                ai_response_ra = bot_adk.send_message(segunda_interacao)
                print(f"Defensor do Consumidor AI (ADK): {ai_response_ra}")

            while True:
                user_input = input("Você: ")
                if user_input.lower() in ["sair", "exit", "quit"]:
                    print("Defensor do Consumidor AI (ADK): Até logo! Espero ter ajudado.")
                    break
                
                if not user_input.strip():
                    continue

                ai_response = bot_adk.send_message(user_input)
                print(f"Defensor do Consumidor AI (ADK): {ai_response}")
        except Exception as e:
            print(f"Erro no teste do backend ADK: {e}")
            import traceback
            traceback.print_exc()