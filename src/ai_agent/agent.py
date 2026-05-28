"""
agent.py — Motor del agente de IA con tool calling para Fraudia Claims.
"""

import json
import os
from google import genai
from google.genai import types

from .prompts import SYSTEM_PROMPT
from .tools import TOOLS_DEFINICION, ejecutar_tool


class AgenteFraude:
    """Agente con function calling para consultar siniestros y responder en lenguaje natural."""

    MAX_ITERACIONES = 8

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        base_url = os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta"  # ✅ versión correcta
        )
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # ✅ modelo válido

        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")

        # ✅ Cliente inicializado correctamente
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(base_url=base_url)
        )

    def consultar(self, pregunta: str) -> str:
        # ✅ Historial en formato Gemini (solo roles "user" y "model")
        historial: list[types.Content] = []

        # El system prompt va aparte en la config, no en el historial
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2000,
            temperature=0.3,
            tools=TOOLS_DEFINICION,
        )

        # Mensaje inicial del usuario
        historial.append(types.Content(
            role="user",
            parts=[types.Part(text=pregunta)]
        ))

        for _ in range(self.MAX_ITERACIONES):
            response = self.client.models.generate_content(
                model=self.model,
                contents=historial,
                config=config,
            )

            candidate = response.candidates[0]
            content = candidate.content

            # Agregar respuesta del modelo al historial
            historial.append(content)

            # Verificar si hay function calls
            function_calls = [
                part for part in content.parts
                if part.function_call is not None
            ]

            if function_calls:
                # Ejecutar cada tool y agregar resultados
                tool_results = []
                for part in function_calls:
                    fc = part.function_call
                    func_args = dict(fc.args) if fc.args else {}
                    resultado = ejecutar_tool(fc.name, func_args)
                    tool_results.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": resultado},
                            )
                        )
                    )

                # ✅ Los resultados de tools van con role "user" en Gemini
                historial.append(types.Content(role="user", parts=tool_results))
                continue

            # Respuesta final de texto
            if candidate.finish_reason == types.FinishReason.STOP:
                return response.text

        return "No pude generar una respuesta completa. Intenta reformular la pregunta."