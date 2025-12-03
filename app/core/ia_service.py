"""
IA Service - Servicio de Inteligencia Artificial con LangChain
Maneja la lógica de LangChain, agentes, memoria y herramientas
"""

import os
from dotenv import load_dotenv
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper

# Importar despues de las otras importaciones para evitar import circular
from app.services.supabase_service import supabase_service

load_dotenv()


class IAService:
    """Servicio de IA que maneja LangChain, agentes y memoria conversacional"""

    def __init__(self):
        """Inicializar servicio de IA con LangChain"""
        # Inicializar modelo de Google AI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            temperature=1.0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Memoria que guarda ultimas 10 interacciones
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
        """Cargar prompt del sistema desde Supabase"""
        # Intentar obtener prompt desde Supabase
        db_prompt = supabase_service.get_active_prompt("system_prompt")

        if db_prompt:
            print("✅ Prompt del sistema cargado desde Supabase")
            return db_prompt

        # Prompt por defecto si no existe en la base de datos
        default_prompt = """Eres un asistente virtual inteligente y servicial. 
Tu objetivo es ayudar a los usuarios de la mejor manera posible.
Cuando necesites informacion actualizada o datos que no conoces, usa la herramienta de busqueda de Google.
Se conciso, amigable y profesional en tus respuestas."""

        print("⚠️ Usando prompt por defecto (no encontrado en Supabase)")

        # Intentar guardar el prompt por defecto en Supabase
        try:
            supabase_service.create_or_update_prompt(
                name="system_prompt",
                content=default_prompt,
                description="Prompt del sistema principal para el chatbot",
                is_active=True
            )
            print("✅ Prompt por defecto guardado en Supabase")
        except Exception as e:
            print(f"⚠️ No se pudo guardar prompt en Supabase: {e}")

        return default_prompt

    def _create_tools(self) -> list:
        """Crear herramientas disponibles para el agente"""
        tools = []

        # Herramienta de busqueda en Google (usando Serper API)
        serper_api_key = os.getenv("SERPER_API_KEY")
        if serper_api_key:
            try:
                search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
                google_tool = Tool(
                    name="google_search",
                    description="Busca informacion actual en Google. Util para responder preguntas sobre eventos recientes, noticias, datos actualizados o informacion que no conoces.",
                    func=search.run
                )
                tools.append(google_tool)
                print("herramienta de busqueda Google activada")
            except Exception as e:
                print(f"no se pudo activar busqueda  {e}")
        else:
            print("⚠️ SERPER_API_KEY no encontrada - busqueda Google desactivada")

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

    def generate_response(self, message: str) -> str:
        """
        Generar respuesta usando el agente de IA

        Args:
            message: Mensaje del usuario

        Returns:
            Respuesta generada por el agente
        """
        try:
            result = self.agent.invoke({"input": message})
            response = result.get(
                "output", "o siento, no pude generar una respuesta")
            return response
        except Exception as e:
            print(f"error generando respuesta{str(e)}")
            return "Lo siento, hubo un error procesando tu mensaje."

    def clear_memory(self) -> None:
        """Limpiar memoria conversacional"""
        self.memory.clear()


# Instancia global del servicio de IA
ia_service = IAService()
