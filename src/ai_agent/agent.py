import os
import json
from typing import Optional
from openai import OpenAI
from .tools import ejecutar_tool, OPENAI_TOOLS, TOOLS_DEFINICION, ANTHROPIC_TOOLS
from .prompts import SYSTEM_PROMPT

# Configuración global en memoria para persistir la selección del usuario desde el frontend
_CURRENT_PROVIDER: Optional[str] = None
_CURRENT_XAI_MODEL: Optional[str] = None
_CURRENT_GEMINI_MODEL: Optional[str] = None
_CURRENT_ANTHROPIC_MODEL: Optional[str] = None

def actualizar_config_agente(provider: str, model: Optional[str] = None):
    global _CURRENT_PROVIDER, _CURRENT_XAI_MODEL, _CURRENT_GEMINI_MODEL, _CURRENT_ANTHROPIC_MODEL
    _CURRENT_PROVIDER = provider.lower()
    if model:
        if _CURRENT_PROVIDER == "xai":
            _CURRENT_XAI_MODEL = model
        elif _CURRENT_PROVIDER == "gemini":
            _CURRENT_GEMINI_MODEL = model
        elif _CURRENT_PROVIDER == "anthropic":
            _CURRENT_ANTHROPIC_MODEL = model

class AgenteFraude:
    def __init__(self):
        global _CURRENT_PROVIDER, _CURRENT_XAI_MODEL, _CURRENT_GEMINI_MODEL, _CURRENT_ANTHROPIC_MODEL
        
        self.provider = _CURRENT_PROVIDER if _CURRENT_PROVIDER is not None else os.getenv("AI_PROVIDER", "xai").lower()
        self.system_prompt = SYSTEM_PROMPT

        # xAI Config
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.xai_model = _CURRENT_XAI_MODEL if _CURRENT_XAI_MODEL is not None else os.getenv("XAI_MODEL", "grok-beta")
        self.xai_base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

        # Gemini Config
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = _CURRENT_GEMINI_MODEL if _CURRENT_GEMINI_MODEL is not None else "gemini-1.5-flash"

        # Anthropic Config
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = _CURRENT_ANTHROPIC_MODEL if _CURRENT_ANTHROPIC_MODEL is not None else os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    def consultar(self, pregunta: str) -> str:
        if self.provider == "xai":
            return self._consultar_xai(pregunta)
        elif self.provider == "anthropic":
            return self._consultar_anthropic(pregunta)
        else:
            return self._consultar_gemini(pregunta)


    def _consultar_xai(self, pregunta: str) -> str:
        if not self.xai_api_key:
            return "Falta configurar XAI_API_KEY en el archivo .env"

        client = OpenAI(api_key=self.xai_api_key, base_url=self.xai_base_url)

        mensajes = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": pregunta}
        ]

        try:
            # Llamamos a Grok con las herramientas habilitadas en formato OpenAI
            response = client.chat.completions.create(
                model=self.xai_model,
                messages=mensajes,
                tools=OPENAI_TOOLS,
                tool_choice="auto",
                temperature=0.1
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Si el modelo decide llamar a una herramienta
            if tool_calls:
                mensajes.append(response_message)
                for tool_call in tool_calls:
                    nombre_func = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # EJECUCIÓN EN LA DB REAL (vPoliza_Puntaje_Total)
                    resultado_db = ejecutar_tool(nombre_func, args)

                    mensajes.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": nombre_func,
                        "content": resultado_db
                    })

                # Volvemos a llamar a Grok para que resuma el resultado de la DB
                segunda_respuesta = client.chat.completions.create(
                    model=self.xai_model,
                    messages=mensajes,
                    temperature=0.1
                )
                return segunda_respuesta.choices[0].message.content

            return response_message.content

        except Exception as e:
            return f"Error en el agente xAI: {str(e)}"

    def _consultar_anthropic(self, pregunta: str) -> str:
        if not self.anthropic_api_key:
            return "Falta configurar ANTHROPIC_API_KEY en el archivo .env"

        import anthropic
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)

        mensajes = [{"role": "user", "content": pregunta}]

        try:
            response = client.messages.create(
                model=self.anthropic_model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=mensajes,
                tools=ANTHROPIC_TOOLS,
                temperature=0.1
            )

            if response.stop_reason == "tool_use":
                # Agregar respuesta del asistente a la lista de mensajes
                mensajes.append({"role": "assistant", "content": response.content})

                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_use_id = content_block.id
                        tool_name = content_block.name
                        tool_input = content_block.input

                        resultado_db = ejecutar_tool(tool_name, tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": resultado_db
                        })

                mensajes.append({"role": "user", "content": tool_results})

                segunda_respuesta = client.messages.create(
                    model=self.anthropic_model,
                    max_tokens=1024,
                    system=self.system_prompt,
                    messages=mensajes,
                    temperature=0.1
                )
                return segunda_respuesta.content[0].text

            # En caso de que no use tools
            if response.content:
                return response.content[0].text
            return "No se recibió respuesta de Anthropic"

        except Exception as e:
            return f"Error en el agente Anthropic: {str(e)}"

    def _consultar_gemini(self, pregunta: str) -> str:
        if not self.gemini_api_key:
            return "Falta configurar GEMINI_API_KEY en el archivo .env"

        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=self.gemini_api_key,
            http_options=types.HttpOptions(api_version="v1")
        )

        config = {
            "system_instruction": self.system_prompt,
            "tools": [TOOLS_DEFINICION],
            "temperature": 0.1,
        }

        chat = client.chats.create(model=self.gemini_model, config=config)

        try:
            response = chat.send_message(pregunta)
            for _ in range(8):
                if not response.candidates[0].content.parts or not any(p.function_call for p in response.candidates[0].content.parts):
                    return response.text

                tool_results = []
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        fc = part.function_call
                        resultado = ejecutar_tool(fc.name, dict(fc.args) if fc.args else {})
                        tool_results.append(
                            types.Part.from_function_response(
                                name=fc.name,
                                response={"result": resultado}
                            )
                        )
                response = chat.send_message(tool_results)
            return response.text
        except Exception as e:
            return f"Error en el agente Gemini: {str(e)}"
