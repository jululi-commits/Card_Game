from typing import Any, List, Tuple

import pygame

from core.escena_base import EscenaBase
from core.estados import EstadoJuego


class EscenaJuego(EscenaBase):
    """
    Escena principal del tablero de juego de Solitario.
    Muestra 21 casillas centradas (3 filas x 7 columnas) y el espacio dispuesto para el mazo de cartas
    en la esquina inferior derecha.
    """

    def __init__(self) -> None:
        super().__init__()
        self.modo: str = "Estratégico"
        self.limite_mesa: int = 26
        self.cartas_activas: int = 7  # Ejemplo inicial para indicador
        self.puntuacion: int = 0
        self.tiempo_transcurrido: float = 0.0
        self.fuente: pygame.font.Font | None = None
        self.fuente_chica: pygame.font.Font | None = None
        self.fuente_casilla: pygame.font.Font | None = None

        # Almacenamiento de geometrías de las 21 casillas y del mazo
        self.rects_casillas: List[pygame.Rect] = []
        self.rect_mazo: pygame.Rect | None = None

    def al_entrar(self, **kwargs: Any) -> None:
        """Recibe la configuración e inicializa recursos de la escena de juego."""
        self.modo = kwargs.get("modo", "Estratégico")
        self.limite_mesa = kwargs.get("limite_mesa", 26)
        self.cartas_activas = kwargs.get("cartas_iniciales", 7)
        self.puntuacion = 0
        self.tiempo_transcurrido = 0.0

        if not pygame.font.get_init():
            pygame.font.init()
        self.fuente = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_chica = pygame.font.SysFont("Arial", 16)
        self.fuente_casilla = pygame.font.SysFont("Arial", 14, bold=True)

    def manejar_eventos(self, eventos: List[pygame.event.Event]) -> None:
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # Volver al menú principal
                    if self.gestor:
                        self.gestor.cambiar_escena(EstadoJuego.MENU)

                elif evento.key == pygame.K_v:
                    # Simular victoria
                    if self.gestor:
                        self.gestor.cambiar_escena(
                            EstadoJuego.GAME_OVER,
                            resultado="¡VICTORIA!",
                            puntuacion=1250,
                            tiempo_segundos=int(self.tiempo_transcurrido),
                            cartas_apiladas=52
                        )

                elif evento.key == pygame.K_g:
                    # Simular derrota (Game Over)
                    if self.gestor:
                        self.gestor.cambiar_escena(
                            EstadoJuego.GAME_OVER,
                            resultado="GAME OVER",
                            causa="Has alcanzado el límite de 26 cartas activas en mesa sin movimientos válidos.",
                            puntuacion=340,
                            tiempo_segundos=int(self.tiempo_transcurrido),
                            cartas_apiladas=18
                        )

                elif evento.key == pygame.K_UP:
                    if self.cartas_activas < 30:
                        self.cartas_activas += 1

                elif evento.key == pygame.K_DOWN:
                    if self.cartas_activas > 0:
                        self.cartas_activas -= 1

    def actualizar(self, dt: float) -> None:
        self.tiempo_transcurrido += dt
        self.puntuacion += int(dt * 10)  # Puntuación simulada

    def dibujar(self, pantalla: pygame.Surface) -> None:
        ancho, alto = pantalla.get_size()

        # 1. Fondo verde provisorio tipo mesa de póker
        pantalla.fill((16, 44, 27))

        # Detalle de tapete (Marco interior de la mesa)
        pygame.draw.rect(pantalla, (25, 65, 40), (12, 12, ancho - 24, alto - 24), 3, border_radius=12)

        # 2. Barra superior de HUD
        alto_hud = 55
        pygame.draw.rect(pantalla, (24, 68, 42), (0, 0, ancho, alto_hud))
        pygame.draw.line(pantalla, (45, 110, 70), (0, alto_hud), (ancho, alto_hud), 2)

        if self.fuente:
            # Indicador dinámico de límite de mesa
            color_limite = (255, 255, 255)
            if self.cartas_activas >= self.limite_mesa:
                color_limite = (255, 80, 80)
            elif self.cartas_activas >= self.limite_mesa - 4:
                color_limite = (255, 200, 80)

            txt_limite = f"Cartas en Mesa: {self.cartas_activas} / {self.limite_mesa}"
            surf_limite = self.fuente.render(txt_limite, True, color_limite)
            pantalla.blit(surf_limite, (25, 15))

            # Puntuación y Tiempo
            txt_stats = f"Puntos: {self.puntuacion}  |  Tiempo: {int(self.tiempo_transcurrido)}s"
            surf_stats = self.fuente.render(txt_stats, True, (230, 230, 230))
            pantalla.blit(surf_stats, (ancho - surf_stats.get_width() - 25, 15))

        # 3. Dibujar las 21 casillas centradas (3 filas x 7 columnas) y el mazo en la esquina inferior derecha
        self._dibujar_tablero_y_mazo(pantalla, alto_hud)

        # 4. Texto de ayuda en la parte inferior izquierda
        if self.fuente_chica:
            txt_ayuda = "[ESC] Menú  |  [V] Simular Victoria  |  [G] Simular Game Over"
            surf_ayuda = self.fuente_chica.render(txt_ayuda, True, (150, 190, 165))
            pantalla.blit(surf_ayuda, (25, alto - 32))

    def _dibujar_tablero_y_mazo(self, pantalla: pygame.Surface, alto_hud: int) -> None:
        """
        Calcula y dibuja las 21 casillas distribuidas en 3 filas de 7 columnas.
        Ubica el espacio del MAZO en la 7ma columna, desplazado un 60% más abajo que la ÚLTIMA fila.
        """
        ancho_pantalla, alto_pantalla = pantalla.get_size()

        # Dimensiones de casilla tipo carta escaladas (115x160 px)
        ancho_carta = 115
        alto_carta = 160
        gap_x = 16
        gap_y = 16

        filas = 3
        columnas = 7

        # Ancho y Alto total de la cuadrícula
        ancho_grid = columnas * ancho_carta + (columnas - 1) * gap_x  # 901 px
        alto_grid = filas * alto_carta + (filas - 1) * gap_y         # 512 px

        # Centrado horizontal y offset del 10% hacia arriba
        x_inicio_grid = (ancho_pantalla - ancho_grid) // 2
        espacio_vertical_disponible = alto_pantalla - alto_hud - 35
        y_centrado = alto_hud + (espacio_vertical_disponible - alto_grid) // 2
        offset_arriba = int(alto_pantalla * 0.10)
        y_inicio_grid = max(alto_hud + 12, y_centrado - offset_arriba)

        self.rects_casillas.clear()

        # Renderizar 20 casillas (Fila 0: 7, Fila 1: 7, Fila 2: 6 casillas sin centrar)
        num_casilla = 1
        for fila in range(filas):
            columnas_en_fila = 6 if fila == 2 else 7  # La 3ª fila sólo dibuja de la col 0 a la 5 (sin casilla 21)
            for col in range(columnas_en_fila):
                x = x_inicio_grid + col * (ancho_carta + gap_x)
                y = y_inicio_grid + fila * (alto_carta + gap_y)
                rect_casilla = pygame.Rect(x, y, ancho_carta, alto_carta)
                self.rects_casillas.append(rect_casilla)

                # Fondo tenue translúcido para la casilla
                pygame.draw.rect(pantalla, (24, 62, 38), rect_casilla, border_radius=10)
                # Borde verde tapete
                pygame.draw.rect(pantalla, (50, 120, 75), rect_casilla, width=2, border_radius=10)

                # Número de casilla (1 a 20)
                if self.fuente_casilla:
                    surf_num = self.fuente_casilla.render(str(num_casilla), True, (70, 140, 95))
                    pantalla.blit(surf_num, surf_num.get_rect(center=rect_casilla.center))

                num_casilla += 1

        # 4. Posicionamiento del MAZO en la 7ma columna (col = 6), desplazado 60% más abajo que la ÚLTIMA fila (fila 2)
        x_mazo = x_inicio_grid + 6 * (ancho_carta + gap_x)
        paso_fila_y = alto_carta + gap_y
        y_ultima_fila = y_inicio_grid + 2 * paso_fila_y  # Posición Y de la 3ª fila
        y_mazo = y_ultima_fila + int(0.60 * paso_fila_y)  # 60% más abajo que la 3ª fila

        self.rect_mazo = pygame.Rect(x_mazo, y_mazo, ancho_carta, alto_carta)

        # Sombra del mazo
        pygame.draw.rect(pantalla, (10, 28, 18), (x_mazo + 4, y_mazo + 4, ancho_carta, alto_carta), border_radius=10)
        # Cuerpo de la casilla del mazo
        pygame.draw.rect(pantalla, (28, 70, 44), self.rect_mazo, border_radius=10)
        # Borde dorado para destacar el mazo
        pygame.draw.rect(pantalla, (210, 180, 100), self.rect_mazo, width=2, border_radius=10)

        # Etiqueta "MAZO"
        if self.fuente_casilla:
            surf_lbl_mazo = self.fuente_casilla.render("[ MAZO ]", True, (240, 215, 120))
            pantalla.blit(surf_lbl_mazo, surf_lbl_mazo.get_rect(center=self.rect_mazo.center))
