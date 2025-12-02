"""
Message Processor con LangChain, Memoria y Búsqueda en Google
Procesador que usa ConversationChain con herramientas de búsqueda
"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv()


class MessageProcessor:
    """Procesador de mensajes con LangChain, memoria y búsqueda en Google"""

    def __init__(self):
        """Inicializar procesador con LangChain y herramientas"""
        self.evolution_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance = os.getenv("EVOLUTION_INSTANCE", "ia-whatsapp")

        # Inicializar modelo de Google AI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-lite-lates",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Memoria que guarda últimas 10 interacciones
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )

        # Cargar prompt del sistema
        self.system_prompt = self._load_system_prompt()

        # Crear herramientas
        self.tools = self._create_tools()

        # Crear agente con herramientas
        self.agent = self._create_agent()

    def _load_system_prompt(self) -> str:
        """Cargar prompt desde Supabase o usar default"""
        try:
            from supabase_client import fetch_prompt_by_name
            prompt_data = fetch_prompt_by_name("system_welcome")
            if prompt_data and "content" in prompt_data:
                print("✅ Prompt cargado desde Supabase")
                return prompt_data["content"]
        except Exception as e:
            print(f"⚠️ No se pudo cargar prompt: {e}")

        return

    def _create_tools(self) -> list:
        """Crear herramientas disponibles para el agente"""
        tools = []

        # Herramienta de búsqueda en Google (usando Serper API)
        serper_api_key = os.getenv("SERPER_API_KEY")
        if serper_api_key:
            try:
                search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
                google_tool = Tool(
                    name="google_search",
                    description="Busca información actual en Google. Útil para responder preguntas sobre eventos recientes, noticias, datos actualizados o información que no conoces.",
                    func=search.run
                )
                tools.append(google_tool)
                print("✅ Herramienta de búsqueda Google activada")
            except Exception as e:
                print(f"⚠️ No se pudo activar búsqueda Google: {e}")
        else:
            print("⚠️ SERPER_API_KEY no encontrada - búsqueda Google desactivada")

        return tools

    def _create_agent(self) -> AgentExecutor:
        """Crear agente con herramientas y memoria"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def process_and_reply(self, message_text: str, from_number: str) -> None:
        """
        Procesar mensaje y enviar respuesta

        Args:
            message_text: Texto del mensaje
            from_number: Número del remitente
        """
        try:
            print(f"📨 Mensaje de {from_number}: {message_text}")

            # Generar respuesta con agente (puede usar herramientas)
            result = self.agent.invoke({"input": message_text})
            response = result.get(
                "output", "Lo siento, no pude generar una respuesta.")

            print(f"🤖 Respuesta: {response[:100]}...")

            # Guardar en Supabase
            self._save_to_supabase(from_number, response)

            # Enviar a Evolution
            self.send_to_evolution(from_number, response)

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            error_msg = "Lo siento, hubo un error procesando tu mensaje."
            self.send_to_evolution(from_number, error_msg)

    def _save_to_supabase(self, phone_number: str, response: str) -> None:
        """Guardar respuesta en Supabase"""
        try:
            from supabase_client import insert_row
            insert_row("message_logs", {
                "phone_number": phone_number,
                "message_text": response,
                "direction": "outgoing",
                "status": "sent"
            })
        except Exception as e:
            print(f"⚠️ No se pudo guardar en Supabase: {e}")

    def send_to_evolution(self, number: str, text: str) -> None:
        """Enviar mensaje a Evolution API"""
        try:
            url = f"{self.evolution_url}/message/sendText/{self.instance}"
            headers = {
                "Content-Type": "application/json",
                "apikey": self.api_key
            }
            data = {
                "number": number,
                "text": text
            }

            response = requests.post(
                url, json=data, headers=headers, timeout=10)

            if response.status_code == 201:
                print(f"✅ Mensaje enviado a {number}")
            else:
                print(f"⚠️ Error enviando: {response.status_code}")

        except Exception as e:
            print(f"❌ Error enviando a Evolution: {str(e)}")


# Instancia global
message_processor = MessageProcessor()
