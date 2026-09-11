"""
Módulo core con la arquitectura base: GestorEscenas, EscenaBase y Estados.
"""
from .escena_base import EscenaBase
from .gestor_escenas import GestorEscenas
from .estados import EstadoJuego

__all__ = ["EscenaBase", "GestorEscenas", "EstadoJuego"]
