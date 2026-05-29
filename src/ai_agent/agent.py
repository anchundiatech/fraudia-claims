import os
import json
from openai import OpenAI
from .tools import ejecutar_tool, OPENAI_TOOLS, TOOLS_DEFINICION
from .prompts import SYSTEM_PROMPT

class AgenteFraude:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        self.system_prompt = SYSTEM_PROMPT

        # xAI Config
        self.xai_api_key = os.getenv("XAI_API_KEY")
        self.xai_model = os.getenv("XAI_MODEL", "grok-beta")
        self.xai_base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")

        # Gemini Config
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = "gemini-1.5-flash"

    def consultar(self, pregunta: str) -> str:
        if self.provider == "xai":
            return self._consultar_xai(pregunta)
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
