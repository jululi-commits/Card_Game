"""
Módulo core con la arquitectura base: GestorEscenas, EscenaBase, Estados y Carta.
"""
from .escena_base import EscenaBase
from .gestor_escenas import GestorEscenas
from .estados import EstadoJuego
from .entidades import Carta

__all__ = ["EscenaBase", "GestorEscenas", "EstadoJuego", "Carta"]
