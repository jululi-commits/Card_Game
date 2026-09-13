from __future__ import annotations

from pathlib import Path
from typing import Optional

import pygame


class Carta:
    """
    Clase base que representa una carta del juego.

    Responsabilidades:
    - Almacenar número y palo (ambos opcionales por ahora).
    - Cargar y renderizar un sprite desde disco, o dibujar un placeholder
      visual si no se proporciona ruta de imagen.
    - Detectar clics sobre su rectángulo (``collidepoint``) y permitir
      que el usuario la arrastre libremente por la pantalla.

    Ciclo de uso en una escena:
        1. ``manejar_eventos(eventos)`` — detecta MOUSEBUTTONDOWN / MOUSEMOTION /
           MOUSEBUTTONUP y actualiza el estado de arrastre.
        2. ``actualizar()``             — extensión para lógica adicional.
        3. ``dibujar(pantalla)``        — renderiza la carta en su posición actual.
    """

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        ancho: int = 100,
        alto: int = 140,
        numero: Optional[int] = None,
        palo: Optional[str] = None,
        ruta_sprite: Optional[str | Path] = None,
    ) -> None:
        """
        :param x:            Posición horizontal inicial (esquina superior izquierda).
        :param y:            Posición vertical inicial (esquina superior izquierda).
        :param ancho:        Ancho de la carta en píxeles.
        :param alto:         Alto de la carta en píxeles.
        :param numero:       Valor numérico de la carta (None = sin asignar).
        :param palo:         Palo de la carta (None = sin asignar).
        :param ruta_sprite:  Ruta al archivo de imagen del sprite (None = placeholder).
        """
        self.numero: Optional[int] = numero
        self.palo: Optional[str] = palo

        self.ancho: int = ancho
        self.alto: int = alto

        # Superficie visual
        self.imagen: pygame.Surface = self._cargar_sprite(ruta_sprite, ancho, alto)

        # Rectángulo de colisión y posición
        self.rect: pygame.Rect = self.imagen.get_rect(topleft=(x, y))

        # Estado de arrastre
        self._siendo_arrastrada: bool = False
        self._offset_arrastre: tuple[int, int] = (0, 0)

    # ------------------------------------------------------------------ #
    #  Carga de sprite                                                     #
    # ------------------------------------------------------------------ #

    def _cargar_sprite(
        self,
        ruta: Optional[str | Path],
        ancho: int,
        alto: int,
    ) -> pygame.Surface:
        """
        Carga el sprite desde ``ruta`` y lo escala a (ancho x alto).
        Si la ruta es None o el archivo no existe, devuelve un placeholder visual.

        :param ruta:  Ruta al archivo de imagen.
        :param ancho: Ancho destino en píxeles.
        :param alto:  Alto destino en píxeles.
        :return:      Superficie de Pygame lista para dibujar.
        """
        if ruta is not None:
            ruta = Path(ruta)
            if ruta.exists():
                try:
                    imagen = pygame.image.load(str(ruta)).convert_alpha()
                    return pygame.transform.scale(imagen, (ancho, alto))
                except pygame.error:
                    pass  # Cae al placeholder si la carga falla

        return self._crear_placeholder(ancho, alto)

    def cargar_sprite(self, ruta: str | Path) -> None:
        """
        Recarga el sprite desde una nueva ruta, conservando la posición actual.

        :param ruta: Ruta al archivo de imagen.
        """
        nueva_imagen = self._cargar_sprite(ruta, self.ancho, self.alto)
        pos_actual = self.rect.topleft
        self.imagen = nueva_imagen
        self.rect = self.imagen.get_rect(topleft=pos_actual)

    def _crear_placeholder(self, ancho: int, alto: int) -> pygame.Surface:
        """
        Crea una superficie de placeholder: fondo blanco, borde gris,
        y etiqueta con número/palo centrada (si están definidos).

        :param ancho: Ancho de la superficie.
        :param alto:  Alto de la superficie.
        :return:      Superficie de Pygame.
        """
        superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        superficie.fill((255, 255, 255, 255))

        # Borde gris redondeado
        pygame.draw.rect(
            superficie, (150, 150, 150), (0, 0, ancho, alto), width=2, border_radius=6
        )

        # Etiqueta con número y palo (si están disponibles y las fuentes están listas)
        if pygame.font.get_init():
            label = self._label()
            if label:
                fuente = pygame.font.SysFont("Arial", max(12, ancho // 5))
                texto = fuente.render(label, True, (30, 30, 30))
                texto_rect = texto.get_rect(center=(ancho // 2, alto // 2))
                superficie.blit(texto, texto_rect)

        return superficie

    # ------------------------------------------------------------------ #
    #  Propiedades de conveniencia                                         #
    # ------------------------------------------------------------------ #

    @property
    def x(self) -> int:
        """Posición X de la esquina superior izquierda."""
        return self.rect.x

    @x.setter
    def x(self, valor: int) -> None:
        self.rect.x = valor

    @property
    def y(self) -> int:
        """Posición Y de la esquina superior izquierda."""
        return self.rect.y

    @y.setter
    def y(self, valor: int) -> None:
        self.rect.y = valor

    @property
    def siendo_arrastrada(self) -> bool:
        """True mientras el usuario mantiene el botón del mouse presionado sobre la carta."""
        return self._siendo_arrastrada

    def _label(self) -> str:
        """Devuelve una etiqueta legible con número y palo para el placeholder."""
        partes = []
        if self.numero is not None:
            partes.append(str(self.numero))
        if self.palo is not None:
            partes.append(self.palo)
        return " ".join(partes)

    # ------------------------------------------------------------------ #
    #  Ciclo de vida                                                       #
    # ------------------------------------------------------------------ #

    def manejar_eventos(self, eventos: list[pygame.event.Event]) -> None:
        """
        Procesa los eventos de ratón para implementar el arrastre.

        Lógica:
        - MOUSEBUTTONDOWN (botón izquierdo): si ``rect.collidepoint(event.pos)``
          es True, activa el arrastre y calcula el offset relativo al cursor
          para que la carta no "salte" al hacer clic.
        - MOUSEMOTION: mientras está activo el arrastre, actualiza la posición
          de la carta restando el offset guardado.
        - MOUSEBUTTONUP (botón izquierdo): desactiva el arrastre.

        :param eventos: Lista de eventos de Pygame del frame actual.
        """
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Detección precisa: ¿el clic cayó dentro del rectángulo de esta carta?
                if self.rect.collidepoint(evento.pos):
                    self._siendo_arrastrada = True
                    # Offset para que la carta no salte al punto del cursor
                    self._offset_arrastre = (
                        self.rect.x - evento.pos[0],
                        self.rect.y - evento.pos[1],
                    )

            elif evento.type == pygame.MOUSEMOTION:
                if self._siendo_arrastrada:
                    self.rect.x = evento.pos[0] + self._offset_arrastre[0]
                    self.rect.y = evento.pos[1] + self._offset_arrastre[1]

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                self._siendo_arrastrada = False

    def actualizar(self) -> None:
        """
        Actualiza la lógica interna de la carta.
        El movimiento ya se aplica en manejar_eventos.
        Las subclases pueden sobrescribir este método para añadir animaciones, etc.
        """
        pass

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """
        Renderiza la carta sobre la superficie de destino.

        :param pantalla: Superficie de Pygame sobre la que dibujar.
        """
        pantalla.blit(self.imagen, self.rect)

    # ------------------------------------------------------------------ #
    #  Representación textual                                              #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        numero_str = str(self.numero) if self.numero is not None else "?"
        palo_str = self.palo if self.palo is not None else "?"
        return f"Carta({numero_str} de {palo_str}, pos={self.rect.topleft})"


# ======================================================================== #
#  Mazo                                                                      #
# ======================================================================== #

import random


# Nombre de archivo base por número (2-10 usan el número directamente)
_NOMBRE_NUMERO: dict[int, str] = {
    1: "as",
    11: "jota",
    12: "reina",
    13: "rey",
}

# Sufijo del palo en el nombre de archivo
_SUFIJO_PALO: dict[str, str] = {
    "Corazones": "corazon",
    "Diamantes": "diamante",
    "Tréboles":  "trebol",
    "Picas":     "pica",
}

PALOS: tuple[str, ...] = ("Corazones", "Diamantes", "Tréboles", "Picas")


class Mazo:
    """
    Representa el mazo completo de 52 cartas.

    Responsabilidades:
    - Generar las 52 instancias de ``Carta`` al construirse, asociando cada
      una con su sprite según la convención ``{nombre}_{palo}.png``
      (ej: ``as_corazon.png``, ``7_pica.png``, ``reina_diamante.png``).
      Si el archivo no existe, ``Carta`` usa su placeholder automáticamente.
    - Mezclar las cartas al inicio (``random.shuffle``).
    - Exponer ``robar()`` para sacar una carta del tope.

    Convención de nombres de sprite:
        - Números 2-10 : ``"2"``, ``"3"``, … ``"10"``
        - As (1)       : ``"as"``
        - Jota (11)    : ``"jota"``
        - Reina (12)   : ``"reina"``
        - Rey (13)     : ``"rey"``
        - Palos        : ``"corazon"``, ``"diamante"``, ``"trebol"``, ``"pica"``

    Ejemplo de ruta completa: ``sprites/as_corazon.png``, ``sprites/10_trebol.png``
    """

    def __init__(
        self,
        ruta_sprites: str | Path,
        ancho_carta: int = 100,
        alto_carta: int = 140,
    ) -> None:
        """
        :param ruta_sprites:  Carpeta que contiene los archivos PNG de las cartas.
        :param ancho_carta:   Ancho en píxeles para todas las cartas.
        :param alto_carta:    Alto en píxeles para todas las cartas.
        """
        self._ruta_sprites = Path(ruta_sprites)
        self.cartas: list[Carta] = []

        for palo in PALOS:
            for numero in range(1, 14):
                nombre_num = _NOMBRE_NUMERO.get(numero, str(numero))
                nombre_palo = _SUFIJO_PALO[palo]
                ruta = self._ruta_sprites / f"{nombre_num}_{nombre_palo}.png"
                self.cartas.append(
                    Carta(
                        numero=numero,
                        palo=palo,
                        ancho=ancho_carta,
                        alto=alto_carta,
                        ruta_sprite=ruta,
                    )
                )

        random.shuffle(self.cartas)

    # ------------------------------------------------------------------ #
    #  API pública                                                         #
    # ------------------------------------------------------------------ #

    def robar(self) -> Optional[Carta]:
        """
        Saca y devuelve la carta del tope del mazo.
        Devuelve ``None`` si el mazo está vacío.
        """
        return self.cartas.pop() if self.cartas else None

    def esta_vacio(self) -> bool:
        """``True`` si no quedan cartas en el mazo."""
        return len(self.cartas) == 0

    def __len__(self) -> int:
        """Número de cartas restantes en el mazo."""
        return len(self.cartas)

    def __repr__(self) -> str:
        return f"Mazo({len(self.cartas)} cartas restantes)"

