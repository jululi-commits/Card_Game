from pathlib import Path
from typing import Any, List, Tuple, Dict

import pygame

from core.escena_base import EscenaBase
from core.entidades import Mazo
from core.estados import EstadoJuego


class EscenaJuego(EscenaBase):
    """
    Escena principal del tablero de juego de Solitario.
    Muestra 20 casillas centradas (3 filas) y el espacio dispuesto para el mazo de cartas
    en la esquina inferior derecha. Admite ventana de pausa (ESC) con opciones de navegación
    y consulta de instrucciones.
    """

    def __init__(self) -> None:
        super().__init__()
        self.modo: str = "Estratégico"
        self.limite_mesa: int = 20
        self.cartas_activas: int = 3  # Cartas repartidas al inicio
        self.cartas_en_mazo: int = 49  # 52 cartas total - 3 iniciales repartidas
        self.movimientos_disponibles: bool = True
        self.puntuacion: int = 0
        self.tiempo_transcurrido: float = 0.0

        # Estado del Modal de Pausa e Instrucciones
        self.mostrar_modal_pausa: bool = False
        self.mostrar_modal_instrucciones: bool = False
        self.scroll_y_instrucciones: float = 0.0
        self.max_scroll_y: float = 0.0
        self.botones_pausa: Dict[str, pygame.Rect] = {}
        self.rect_modal_cerrar: pygame.Rect | None = None

        # Fuentes
        self.fuente: pygame.font.Font | None = None
        self.fuente_chica: pygame.font.Font | None = None
        self.fuente_casilla: pygame.font.Font | None = None
        self.fuente_modal_titulo: pygame.font.Font | None = None
        self.fuente_modal_cuerpo: pygame.font.Font | None = None
        self.fuente_boton: pygame.font.Font | None = None

        # Almacenamiento de geometrías de las casillas y del mazo
        self.rects_casillas: List[pygame.Rect] = []
        self.rect_mazo: pygame.Rect | None = None

        # Mazo de 52 cartas (se inicializa en al_entrar)
        self.mazo: Mazo | None = None
        # Cartas robadas del mazo que están activas en la mesa
        self.cartas_en_mesa: List = []

        # Plantilla de texto de instrucciones
        self.plantilla_instrucciones: List[str] = [
            "--------------------------------------------------",
            "        REGLAS E INSTRUCCIONES DEL JUEGO          ",
            "--------------------------------------------------",
            "",
            "1. OBJETIVO DEL JUEGO:",
            "  Apilar las 52 cartas por palo en las fundaciones de A a K.",
            "",
            "2. REGLA CENTRAL DE MESA:",
            "  Máximo de 20 casillas activas visibles en la mesa a la vez.",
            "  Si alcanzas 20 casillas, no podrás robar más hasta despejar.",
            "",
            "3. CARTAS ESPECIALES:",
            "  Beneficios: Limpiador, Comodín, Magneto.",
            "  Desafíos: Bloqueo, Sobrecarga, Desorden.",
            "",
            "--------------------------------------------------",
            "[ Escribe o modifica aquí tus propias instrucciones ]",
            "--------------------------------------------------"
        ]

    def al_entrar(self, **kwargs: Any) -> None:
        """Recibe la configuración e inicializa recursos de la escena de juego."""
        self.modo = kwargs.get("modo", "Estratégico")
        self.limite_mesa = kwargs.get("limite_mesa", 20)
        self.cartas_activas = kwargs.get("cartas_iniciales", 3)
        self.cartas_en_mazo = kwargs.get("cartas_mazo", 52 - self.cartas_activas)
        self.movimientos_disponibles = kwargs.get("movimientos_disponibles", True)
        self.puntuacion = 0
        self.tiempo_transcurrido = 0.0

        self.mostrar_modal_pausa = False
        self.mostrar_modal_instrucciones = False
        self.scroll_y_instrucciones = 0.0

        if not pygame.font.get_init():
            pygame.font.init()
        self.fuente = pygame.font.SysFont("Arial", 22, bold=True)
        self.fuente_chica = pygame.font.SysFont("Arial", 16)
        self.fuente_casilla = pygame.font.SysFont("Arial", 14, bold=True)
        self.fuente_modal_titulo = pygame.font.SysFont("Georgia", 28, bold=True)
        self.fuente_modal_cuerpo = pygame.font.SysFont("Courier New", 15, bold=True)
        self.fuente_boton = pygame.font.SysFont("Arial", 20, bold=True)

        # Instanciar el mazo completo de 52 cartas mezcladas
        # Ruta: src/escenas/ -> src/ -> Card_Game/ -> sprites/
        # Las dimensiones coinciden con las casillas del tablero (115x160)
        ruta_sprites = Path(__file__).resolve().parent.parent.parent / "sprites"
        self.mazo = Mazo(ruta_sprites=ruta_sprites, ancho_carta=115, alto_carta=160)

        # Repartir las 3 cartas iniciales a la mesa
        self.cartas_en_mesa.clear()
        for _ in range(self.cartas_activas):
            carta = self.mazo.robar()
            if carta:
                self.cartas_en_mesa.append(carta)

        # Sincronizar el contador con el estado real del mazo
        self.cartas_en_mazo = len(self.mazo)

    def manejar_eventos(self, eventos: List[pygame.event.Event]) -> None:
        pos_mouse = pygame.mouse.get_pos()

        # Delegar eventos a las cartas en mesa para habilitar arrastre
        for carta in self.cartas_en_mesa:
            carta.manejar_eventos(eventos)

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if self.mostrar_modal_instrucciones:
                        self.mostrar_modal_instrucciones = False
                    elif self.mostrar_modal_pausa:
                        self.mostrar_modal_pausa = False
                    else:
                        self.mostrar_modal_pausa = True

                elif self.mostrar_modal_instrucciones:
                    if evento.key == pygame.K_DOWN:
                        self.scroll_y_instrucciones = min(self.max_scroll_y, self.scroll_y_instrucciones + 25)
                    elif evento.key == pygame.K_UP:
                        self.scroll_y_instrucciones = max(0.0, self.scroll_y_instrucciones - 25)

                elif not self.mostrar_modal_pausa and not self.mostrar_modal_instrucciones:
                    if evento.key == pygame.K_v:
                        # Simular estado de Victoria (52 cartas repartidas, 0 en mazo, sin movimientos)
                        self.cartas_en_mazo = 0
                        self.movimientos_disponibles = False

                    elif evento.key == pygame.K_g:
                        # Simular estado de Derrota (20 casillas ocupadas, >0 cartas en mazo, sin movimientos)
                        self.cartas_activas = 20
                        self.cartas_en_mazo = 10
                        self.movimientos_disponibles = False

                    elif evento.key == pygame.K_m:
                        # Alternar disponibilidad de movimientos para pruebas
                        self.movimientos_disponibles = not self.movimientos_disponibles

                    elif evento.key == pygame.K_UP:
                        if self.cartas_activas < 30:
                            self.cartas_activas += 1

                    elif evento.key == pygame.K_DOWN:
                        if self.cartas_activas > 0:
                            self.cartas_activas -= 1

            elif evento.type == pygame.MOUSEWHEEL and self.mostrar_modal_instrucciones:
                self.scroll_y_instrucciones -= evento.y * 25
                self.scroll_y_instrucciones = max(0.0, min(self.max_scroll_y, self.scroll_y_instrucciones))

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if self.mostrar_modal_instrucciones:
                    if evento.button == 4:
                        self.scroll_y_instrucciones = max(0.0, self.scroll_y_instrucciones - 25)
                    elif evento.button == 5:
                        self.scroll_y_instrucciones = min(self.max_scroll_y, self.scroll_y_instrucciones + 25)
                    elif evento.button == 1:
                        if self.rect_modal_cerrar and self.rect_modal_cerrar.collidepoint(pos_mouse):
                            self.mostrar_modal_instrucciones = False

                elif self.mostrar_modal_pausa:
                    if evento.button == 1:
                        if "Volver al Menú" in self.botones_pausa and self.botones_pausa["Volver al Menú"].collidepoint(pos_mouse):
                            if self.gestor:
                                self.gestor.cambiar_escena(EstadoJuego.MENU)
                        elif "Instrucciones" in self.botones_pausa and self.botones_pausa["Instrucciones"].collidepoint(pos_mouse):
                            self.mostrar_modal_instrucciones = True
                            self.scroll_y_instrucciones = 0.0
                        elif "Seguir Jugando" in self.botones_pausa and self.botones_pausa["Seguir Jugando"].collidepoint(pos_mouse):
                            self.mostrar_modal_pausa = False

                elif evento.button == 1:
                    # Click sobre el mazo: robar 1 carta si hay disponibles y hay lugar en la mesa
                    if (
                        self.mazo is not None
                        and self.rect_mazo is not None
                        and self.rect_mazo.collidepoint(pos_mouse)
                        and not self.mazo.esta_vacio()
                        and self.cartas_activas < self.limite_mesa
                    ):
                        carta_robada = self.mazo.robar()
                        if carta_robada:
                            self.cartas_en_mesa.append(carta_robada)
                            self.cartas_activas += 1
                            self.cartas_en_mazo = len(self.mazo)

    def verificar_condiciones_fin_juego(self) -> None:
        """
        Evalúa las condiciones de Victoria y Derrota para cambiar el estado a GAME_OVER vía GestorEscenas:
        - Derrota: todas las 20 casillas están ocupadas, quedan >0 cartas en el mazo y no hay movimientos disponibles.
        - Victoria: las 52 cartas ya se repartieron (0 en mazo), no quedan movimientos y no se superaron las 20 casillas.
        """
        if not self.gestor:
            return

        # Condición de Derrota
        if self.cartas_activas >= self.limite_mesa and self.cartas_en_mazo > 0 and not self.movimientos_disponibles:
            self.gestor.cambiar_escena(
                EstadoJuego.GAME_OVER,
                resultado="¡DERROTA!",
                causa="Todas las 20 casillas están ocupadas, quedan cartas en el mazo y no hay movimientos disponibles.",
                puntuacion=self.puntuacion,
                tiempo_segundos=int(self.tiempo_transcurrido),
                cartas_apiladas=52 - self.cartas_en_mazo
            )

        # Condición de Victoria
        elif self.cartas_en_mazo == 0 and not self.movimientos_disponibles and self.cartas_activas <= self.limite_mesa:
            self.gestor.cambiar_escena(
                EstadoJuego.GAME_OVER,
                resultado="¡VICTORIA!",
                puntuacion=self.puntuacion + 1000,
                tiempo_segundos=int(self.tiempo_transcurrido),
                pilones_armados=self.cartas_activas
            )

    def actualizar(self, dt: float) -> None:
        # El juego se congela (el reloj se detiene) si el menú de pausa o instrucciones está activo
        if self.mostrar_modal_pausa or self.mostrar_modal_instrucciones:
            return

        self.tiempo_transcurrido += dt
        self.puntuacion += int(dt * 10)  # Puntuación simulada
        self.verificar_condiciones_fin_juego()

        for carta in self.cartas_en_mesa:
            carta.actualizar()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pos_mouse = pygame.mouse.get_pos()
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

            txt_limite = f"Casillas en uso: {self.cartas_activas} / {self.limite_mesa}"
            surf_limite = self.fuente.render(txt_limite, True, color_limite)
            pantalla.blit(surf_limite, (25, 15))

            # Puntuación y Tiempo
            txt_stats = f"Puntos: {self.puntuacion}  |  Tiempo: {int(self.tiempo_transcurrido)}s"
            surf_stats = self.fuente.render(txt_stats, True, (230, 230, 230))
            pantalla.blit(surf_stats, (ancho - surf_stats.get_width() - 25, 15))

        # 3. Dibujar las 20 casillas centradas (3 filas) y el mazo en la esquina inferior derecha
        self._dibujar_tablero_y_mazo(pantalla, alto_hud)

        # 4b. Dibujar las cartas en mesa, ancladas a su casilla si no se arrastran
        for i, carta in enumerate(self.cartas_en_mesa):
            if i < len(self.rects_casillas) and not carta.siendo_arrastrada:
                carta.rect.topleft = self.rects_casillas[i].topleft
            carta.dibujar(pantalla)

        # 4. Texto de ayuda en la parte inferior izquierda
        if self.fuente_chica:
            txt_movs = "Sí" if self.movimientos_disponibles else "NO"
            txt_ayuda = f"[ESC] Pausa  |  [V] Simular Victoria  |  [G] Simular Derrota  |  [M] Movimientos: {txt_movs}"
            surf_ayuda = self.fuente_chica.render(txt_ayuda, True, (150, 190, 165))
            pantalla.blit(surf_ayuda, (25, alto - 32))

        # 5. Modales (Pausa o Instrucciones)
        if self.mostrar_modal_instrucciones:
            self._dibujar_modal_instrucciones(pantalla, pos_mouse)
        elif self.mostrar_modal_pausa:
            self._dibujar_modal_pausa(pantalla, pos_mouse)

    def _dibujar_tablero_y_mazo(self, pantalla: pygame.Surface, alto_hud: int) -> None:
        """Calcula y dibuja las 20 casillas y el espacio del MAZO."""
        ancho_pantalla, alto_pantalla = pantalla.get_size()

        ancho_carta = 115
        alto_carta = 160
        gap_x = 16
        gap_y = 16

        filas = 3
        columnas = 7

        ancho_grid = columnas * ancho_carta + (columnas - 1) * gap_x
        alto_grid = filas * alto_carta + (filas - 1) * gap_y

        x_inicio_grid = (ancho_pantalla - ancho_grid) // 2
        espacio_vertical_disponible = alto_pantalla - alto_hud - 35
        y_centrado = alto_hud + (espacio_vertical_disponible - alto_grid) // 2
        offset_arriba = int(alto_pantalla * 0.10)
        y_inicio_grid = max(alto_hud + 12, y_centrado - offset_arriba)

        self.rects_casillas.clear()

        num_casilla = 1
        for fila in range(filas):
            columnas_en_fila = 6 if fila == 2 else 7
            for col in range(columnas_en_fila):
                x = x_inicio_grid + col * (ancho_carta + gap_x)
                y = y_inicio_grid + fila * (alto_carta + gap_y)
                rect_casilla = pygame.Rect(x, y, ancho_carta, alto_carta)
                self.rects_casillas.append(rect_casilla)

                pygame.draw.rect(pantalla, (24, 62, 38), rect_casilla, border_radius=10)
                pygame.draw.rect(pantalla, (50, 120, 75), rect_casilla, width=2, border_radius=10)

                if self.fuente_casilla:
                    surf_num = self.fuente_casilla.render(str(num_casilla), True, (70, 140, 95))
                    pantalla.blit(surf_num, surf_num.get_rect(center=rect_casilla.center))

                num_casilla += 1

        x_mazo = x_inicio_grid + 6 * (ancho_carta + gap_x)
        paso_fila_y = alto_carta + gap_y
        y_ultima_fila = y_inicio_grid + 2 * paso_fila_y
        y_mazo = y_ultima_fila + int(0.60 * paso_fila_y)

        self.rect_mazo = pygame.Rect(x_mazo, y_mazo, ancho_carta, alto_carta)

        pygame.draw.rect(pantalla, (10, 28, 18), (x_mazo + 4, y_mazo + 4, ancho_carta, alto_carta), border_radius=10)
        pygame.draw.rect(pantalla, (28, 70, 44), self.rect_mazo, border_radius=10)
        pygame.draw.rect(pantalla, (210, 180, 100), self.rect_mazo, width=2, border_radius=10)

        if self.fuente_casilla:
            lbl_mazo = f"MAZO ({self.cartas_en_mazo})" if self.cartas_en_mazo > 0 else "[ VACÍO ]"
            surf_lbl_mazo = self.fuente_casilla.render(lbl_mazo, True, (240, 215, 120))
            pantalla.blit(surf_lbl_mazo, surf_lbl_mazo.get_rect(center=self.rect_mazo.center))

    def _dibujar_modal_pausa(self, pantalla: pygame.Surface, pos_mouse: Tuple[int, int]) -> None:
        """Dibuja la ventana emergente con el título PAUSA y los 3 botones interactivos."""
        ancho_pantalla, alto_pantalla = pantalla.get_size()

        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        pantalla.blit(overlay, (0, 0))

        ancho_modal, alto_modal = 440, 340
        x_modal = (ancho_pantalla - ancho_modal) // 2
        y_modal = (alto_pantalla - alto_modal) // 2
        rect_modal = pygame.Rect(x_modal, y_modal, ancho_modal, alto_modal)

        pygame.draw.rect(pantalla, (5, 10, 8), (x_modal + 6, y_modal + 6, ancho_modal, alto_modal), border_radius=14)
        pygame.draw.rect(pantalla, (20, 36, 26), rect_modal, border_radius=14)
        pygame.draw.rect(pantalla, (200, 170, 90), rect_modal, width=3, border_radius=14)

        if self.fuente_modal_titulo:
            surf_titulo = self.fuente_modal_titulo.render("PAUSA", True, (240, 215, 120))
            pantalla.blit(surf_titulo, surf_titulo.get_rect(center=(ancho_pantalla // 2, y_modal + 40)))

        pygame.draw.line(pantalla, (80, 130, 95), (x_modal + 30, y_modal + 75), (x_modal + ancho_modal - 30, y_modal + 75), 2)

        etiquetas_botones = ["Volver al Menú", "Instrucciones", "Seguir Jugando"]
        ancho_btn, alto_btn = 260, 48
        y_inicio_btns = y_modal + 100
        gap_btns = 18

        self.botones_pausa.clear()

        for i, etiq in enumerate(etiquetas_botones):
            x_btn = (ancho_pantalla - ancho_btn) // 2
            y_btn = y_inicio_btns + i * (alto_btn + gap_btns)
            rect_btn = pygame.Rect(x_btn, y_btn, ancho_btn, alto_btn)
            self.botones_pausa[etiq] = rect_btn

            hover = rect_btn.collidepoint(pos_mouse)
            color_bg = (40, 95, 60) if hover else (28, 70, 44)
            color_borde = (240, 215, 120) if hover else (80, 140, 95)
            color_texto = (255, 255, 255) if hover else (220, 230, 220)

            pygame.draw.rect(pantalla, (10, 20, 15), (x_btn + 3, y_btn + 3, ancho_btn, alto_btn), border_radius=10)
            pygame.draw.rect(pantalla, color_bg, rect_btn, border_radius=10)
            pygame.draw.rect(pantalla, color_borde, rect_btn, width=2, border_radius=10)

            if self.fuente_boton:
                surf_txt = self.fuente_boton.render(etiq, True, color_texto)
                pantalla.blit(surf_txt, surf_txt.get_rect(center=rect_btn.center))

    def _ajustar_linea(self, texto: str, fuente: pygame.font.Font, ancho_maximo: int) -> List[str]:
        """Divide el texto en sublíneas que no excedan el ancho máximo en píxeles."""
        if not texto.strip():
            return [""]
        palabras = texto.split(" ")
        sublineas: List[str] = []
        linea_actual = ""

        for palabra in palabras:
            linea_prueba = f"{linea_actual} {palabra}".strip()
            if fuente.size(linea_prueba)[0] <= ancho_maximo:
                linea_actual = linea_prueba
            else:
                if linea_actual:
                    sublineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            sublineas.append(linea_actual)

        return sublineas

    def _dibujar_modal_instrucciones(self, pantalla: pygame.Surface, pos_mouse: Tuple[int, int]) -> None:
        """Dibuja la ventana emergente de instrucciones con scrollbar e idéntico estilo que en el Menú."""
        ancho_pantalla, alto_pantalla = pantalla.get_size()

        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        pantalla.blit(overlay, (0, 0))

        ancho_modal, alto_modal = 700, 530
        x_modal = (ancho_pantalla - ancho_modal) // 2
        y_modal = (alto_pantalla - alto_modal) // 2
        rect_modal = pygame.Rect(x_modal, y_modal, ancho_modal, alto_modal)

        pygame.draw.rect(pantalla, (5, 10, 8), (x_modal + 6, y_modal + 6, ancho_modal, alto_modal), border_radius=14)
        pygame.draw.rect(pantalla, (20, 36, 26), rect_modal, border_radius=14)
        pygame.draw.rect(pantalla, (200, 170, 90), rect_modal, width=3, border_radius=14)

        if self.fuente_modal_titulo:
            surf_titulo_modal = self.fuente_modal_titulo.render("Instrucciones del Juego", True, (240, 215, 120))
            pantalla.blit(surf_titulo_modal, (x_modal + 30, y_modal + 22))

        pygame.draw.line(pantalla, (80, 130, 95), (x_modal + 30, y_modal + 60), (x_modal + ancho_modal - 30, y_modal + 60), 2)

        x_clip = x_modal + 30
        y_clip = y_modal + 70
        ancho_clip = ancho_modal - 60
        alto_clip = alto_modal - 130
        rect_clip = pygame.Rect(x_clip, y_clip, ancho_clip, alto_clip)

        lineas_para_render: List[Tuple[str, Tuple[int, int, int]]] = []

        if self.fuente_modal_cuerpo:
            for linea_raw in self.plantilla_instrucciones:
                sublineas = self._ajustar_linea(linea_raw, self.fuente_modal_cuerpo, ancho_clip - 25)

                if "REGLAS" in linea_raw or "OBJE" in linea_raw or "REGLA" in linea_raw or "CARTAS" in linea_raw:
                    color_linea = (235, 210, 120)
                elif "[" in linea_raw:
                    color_linea = (140, 210, 255)
                else:
                    color_linea = (215, 230, 220)

                for sub in sublineas:
                    lineas_para_render.append((sub, color_linea))

        alto_linea = 21
        altura_total_contenido = len(lineas_para_render) * alto_linea
        self.max_scroll_y = max(0.0, float(altura_total_contenido - alto_clip))
        self.scroll_y_instrucciones = max(0.0, min(self.max_scroll_y, self.scroll_y_instrucciones))

        pantalla.set_clip(rect_clip)

        y_render = y_clip - int(self.scroll_y_instrucciones)
        if self.fuente_modal_cuerpo:
            for sublinea, color in lineas_para_render:
                if y_render + alto_linea >= y_clip and y_render <= y_clip + alto_clip:
                    surf_sub = self.fuente_modal_cuerpo.render(sublinea, True, color)
                    pantalla.blit(surf_sub, (x_clip, y_render))
                y_render += alto_linea

        pantalla.set_clip(None)

        if self.max_scroll_y > 0:
            x_bar = x_modal + ancho_modal - 22
            y_bar = y_clip
            h_bar = alto_clip
            pygame.draw.rect(pantalla, (15, 30, 22), (x_bar, y_bar, 8, h_bar), border_radius=4)

            porcentaje_scroll = self.scroll_y_instrucciones / self.max_scroll_y
            h_thumb = max(30, int(h_bar * (alto_clip / altura_total_contenido)))
            y_thumb = y_bar + int((h_bar - h_thumb) * porcentaje_scroll)
            pygame.draw.rect(pantalla, (200, 170, 90), (x_bar, y_thumb, 8, h_thumb), border_radius=4)

        ancho_cerrar, alto_cerrar = 140, 38
        x_cerrar = x_modal + (ancho_modal - ancho_cerrar) // 2
        y_cerrar = y_modal + alto_modal - 50
        self.rect_modal_cerrar = pygame.Rect(x_cerrar, y_cerrar, ancho_cerrar, alto_cerrar)

        hover_cerrar = self.rect_modal_cerrar.collidepoint(pos_mouse)
        color_bg_cerrar = (180, 60, 60) if hover_cerrar else (120, 40, 40)
        color_borde_cerrar = (240, 120, 120) if hover_cerrar else (180, 80, 80)

        pygame.draw.rect(pantalla, color_bg_cerrar, self.rect_modal_cerrar, border_radius=8)
        pygame.draw.rect(pantalla, color_borde_cerrar, self.rect_modal_cerrar, width=2, border_radius=8)

        if self.fuente_boton:
            surf_cerrar_txt = self.fuente_boton.render("Cerrar", True, (255, 255, 255))
            pantalla.blit(surf_cerrar_txt, surf_cerrar_txt.get_rect(center=self.rect_modal_cerrar.center))
