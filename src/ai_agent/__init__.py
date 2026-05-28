"""
ai_agent — Agente de IA con tool calling para detección de fraudes.
hackIAthon 2026 — Reto Aseguradora del Sur.
"""

from .agent import AgenteFraude
from .tools import TOOLS_DEFINICION, ejecutar_tool

__all__ = ["AgenteFraude", "TOOLS_DEFINICION", "ejecutar_tool"]
