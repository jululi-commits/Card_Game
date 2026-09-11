from typing import Any, List, Dict, Tuple

import pygame

from core.escena_base import EscenaBase
from core.estados import EstadoJuego


class EscenaMenu(EscenaBase):
    """
    Escena del Menú Principal del juego de Solitario.
    Muestra el título del juego, 3 botones interactivos (Jugar, Instrucciones, Salir)
    y una ventana pop-up modal scrollable para las instrucciones del juego.
    """

    def __init__(self) -> None:
        super().__init__()
        # Fuentes de texto
        self.fuente_titulo: pygame.font.Font | None = None
        self.fuente_subtitulo: pygame.font.Font | None = None
        self.fuente_boton: pygame.font.Font | None = None
        self.fuente_modal_titulo: pygame.font.Font | None = None
        self.fuente_modal_cuerpo: pygame.font.Font | None = None

        # Estado del Modal de Instrucciones
        self.mostrar_modal_instrucciones: bool = False
        self.scroll_y_instrucciones: float = 0.0
        self.max_scroll_y: float = 0.0

        # Configuración de los botones principales (Rects y etiquetas)
        self.botones: Dict[str, pygame.Rect] = {}
        self.rect_modal_cerrar: pygame.Rect | None = None

        # Plantilla de texto de instrucciones editables por el usuario
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
        """Inicializa las fuentes y la geometría del menú al activarse la escena."""
        if not pygame.font.get_init():
            pygame.font.init()

        self.fuente_titulo = pygame.font.SysFont("Georgia", 64, bold=True)
        self.fuente_subtitulo = pygame.font.SysFont("Arial", 20, italic=True)
        self.fuente_boton = pygame.font.SysFont("Arial", 24, bold=True)
        self.fuente_modal_titulo = pygame.font.SysFont("Georgia", 28, bold=True)
        self.fuente_modal_cuerpo = pygame.font.SysFont("Courier New", 15, bold=True)

        self.mostrar_modal_instrucciones = False
        self.scroll_y_instrucciones = 0.0

    def manejar_eventos(self, eventos: List[pygame.event.Event]) -> None:
        pos_mouse = pygame.mouse.get_pos()

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if self.mostrar_modal_instrucciones:
                        self.mostrar_modal_instrucciones = False
                    else:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

                # Presionar ESPACIO o ENTER en el menú inicia el Juego
                elif not self.mostrar_modal_instrucciones and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.gestor:
                        self.gestor.cambiar_escena(
                            EstadoJuego.JUEGO,
                            modo="Estratégico",
                            limite_mesa=20
                        )

                # Desplazamiento por teclado en el modal de instrucciones
                elif self.mostrar_modal_instrucciones:
                    if evento.key == pygame.K_DOWN:
                        self.scroll_y_instrucciones = min(self.max_scroll_y, self.scroll_y_instrucciones + 25)
                    elif evento.key == pygame.K_UP:
                        self.scroll_y_instrucciones = max(0.0, self.scroll_y_instrucciones - 25)

            # Eventos de rueda de ratón para scroll
            elif evento.type == pygame.MOUSEWHEEL and self.mostrar_modal_instrucciones:
                self.scroll_y_instrucciones -= evento.y * 25
                self.scroll_y_instrucciones = max(0.0, min(self.max_scroll_y, self.scroll_y_instrucciones))

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if self.mostrar_modal_instrucciones:
                    # Scroll con botones de ratón antiguos (4=Up, 5=Down)
                    if evento.button == 4:
                        self.scroll_y_instrucciones = max(0.0, self.scroll_y_instrucciones - 25)
                    elif evento.button == 5:
                        self.scroll_y_instrucciones = min(self.max_scroll_y, self.scroll_y_instrucciones + 25)
                    elif evento.button == 1:
                        if self.rect_modal_cerrar and self.rect_modal_cerrar.collidepoint(pos_mouse):
                            self.mostrar_modal_instrucciones = False
                else:
                    if evento.button == 1:
                        # Clic en botón "Jugar" o "Juego" -> GestorEscenas cambia a EscenaJuego
                        btn_juego_cliqueado = any(
                            k in self.botones and self.botones[k].collidepoint(pos_mouse)
                            for k in ("Jugar", "Juego")
                        )
                        if btn_juego_cliqueado:
                            if self.gestor:
                                self.gestor.cambiar_escena(
                                    EstadoJuego.JUEGO,
                                    modo="Estratégico",
                                    limite_mesa=20
                                )

                        elif "Instrucciones" in self.botones and self.botones["Instrucciones"].collidepoint(pos_mouse):
                            self.mostrar_modal_instrucciones = True
                            self.scroll_y_instrucciones = 0.0

                        elif "Salir" in self.botones and self.botones["Salir"].collidepoint(pos_mouse):
                            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def actualizar(self, dt: float) -> None:
        pass

    def dibujar(self, pantalla: pygame.Surface) -> None:
        ancho, alto = pantalla.get_size()

        # 1. Fondo verde elegante estilo mesa de póker/solitario
        pantalla.fill((16, 44, 27))

        # Detalle de tapete (Marco interior)
        pygame.draw.rect(pantalla, (25, 65, 40), (15, 15, ancho - 30, alto - 30), 4, border_radius=12)

        # 2. Cálculo de posición del bloque central (Título, Subtítulo y Botones centrados)
        ancho_btn, alto_btn = 260, 52
        espaciado_btn = 18
        altura_botones = 3 * alto_btn + 2 * espaciado_btn
        altura_bloque_total = 70 + 25 + 40 + altura_botones

        y_top_bloque = (alto - altura_bloque_total) // 2

        # Título Provisorio "Solitario"
        if self.fuente_titulo:
            surf_sombra = self.fuente_titulo.render("Solitario", True, (10, 25, 15))
            pantalla.blit(surf_sombra, (ancho // 2 - surf_sombra.get_width() // 2 + 3, y_top_bloque + 3))

            surf_titulo = self.fuente_titulo.render("Solitario", True, (240, 215, 120))
            pantalla.blit(surf_titulo, (ancho // 2 - surf_titulo.get_width() // 2, y_top_bloque))

        if self.fuente_subtitulo:
            surf_sub = self.fuente_subtitulo.render("Edición Estratégica con Cartas Especiales", True, (170, 210, 185))
            pantalla.blit(surf_sub, (ancho // 2 - surf_sub.get_width() // 2, y_top_bloque + 72))

        # 3. Dibujar los tres botones principales: Jugar, Instrucciones, Salir centrados
        pos_mouse = pygame.mouse.get_pos()
        nombres_botones = ["Jugar", "Instrucciones", "Salir"]
        y_inicial_botones = y_top_bloque + 135

        for i, nombre in enumerate(nombres_botones):
            x_btn = (ancho - ancho_btn) // 2
            y_btn = y_inicial_botones + i * (alto_btn + espaciado_btn)
            rect_btn = pygame.Rect(x_btn, y_btn, ancho_btn, alto_btn)
            self.botones[nombre] = rect_btn

            en_hover = rect_btn.collidepoint(pos_mouse) and not self.mostrar_modal_instrucciones

            if en_hover:
                color_bg = (45, 120, 75)
                color_borde = (240, 215, 120)
                color_texto = (255, 255, 255)
            else:
                color_bg = (24, 68, 42)
                color_borde = (80, 150, 100)
                color_texto = (220, 235, 225)

            pygame.draw.rect(pantalla, (10, 28, 18), (x_btn + 3, y_btn + 4, ancho_btn, alto_btn), border_radius=10)
            pygame.draw.rect(pantalla, color_bg, rect_btn, border_radius=10)
            pygame.draw.rect(pantalla, color_borde, rect_btn, width=2, border_radius=10)

            if self.fuente_boton:
                surf_btn_txt = self.fuente_boton.render(nombre, True, color_texto)
                pantalla.blit(surf_btn_txt, surf_btn_txt.get_rect(center=rect_btn.center))

        # 4. Dibujar Pop-up Modal de Instrucciones (si está activo)
        if self.mostrar_modal_instrucciones:
            self._dibujar_modal_instrucciones(pantalla, pos_mouse)

    def _ajustar_linea(self, texto: str, fuente: pygame.font.Font, ancho_maximo: int) -> List[str]:
        """
        Divide una línea de texto en múltiples sublíneas si excede el ancho máximo disponible.
        Incluye fragmentación carácter por carácter para palabras excesivamente largas sin espacios.
        """
        texto_limpio = texto.rstrip()
        if not texto_limpio:
            return [""]
        if fuente.size(texto_limpio)[0] <= ancho_maximo:
            return [texto_limpio]

        # Si es una línea divisoria decorativa (ej. === o ---)
        primer_char = texto_limpio.strip()[:1]
        if primer_char in ("=", "-", "*") and set(texto_limpio.strip()).issubset({primer_char, " "}):
            div = primer_char
            while fuente.size(div + primer_char)[0] <= ancho_maximo:
                div += primer_char
            return [div]

        palabras = texto_limpio.split(" ")
        sublineas: List[str] = []
        linea_actual = ""

        for palabra in palabras:
            if not palabra:
                continue

            # Si una sola palabra sobrepasa el ancho por sí sola (sin espacios internos)
            if fuente.size(palabra)[0] > ancho_maximo:
                if linea_actual:
                    sublineas.append(linea_actual)
                    linea_actual = ""
                sub_palabra = ""
                for char in palabra:
                    if fuente.size(sub_palabra + char)[0] <= ancho_maximo:
                        sub_palabra += char
                    else:
                        sublineas.append(sub_palabra)
                        sub_palabra = char
                linea_actual = sub_palabra
                continue

            prueba = f"{linea_actual} {palabra}".strip() if linea_actual else palabra
            if fuente.size(prueba)[0] <= ancho_maximo:
                linea_actual = prueba
            else:
                if linea_actual:
                    sublineas.append(linea_actual)
                sangria = "  " if texto.startswith(" ") and not sublineas else ""
                linea_actual = f"{sangria}{palabra}"

        if linea_actual:
            sublineas.append(linea_actual)

        return sublineas

    def _dibujar_modal_instrucciones(self, pantalla: pygame.Surface, pos_mouse: Tuple[int, int]) -> None:
        """
        Dibuja la ventana emergente (Pop-up Modal) con recorte estricto de pantalla (Clipping)
        y soporte para desplazamiento vertical (Scroll).
        """
        ancho_pantalla, alto_pantalla = pantalla.get_size()

        # Overlay semi-transparente para oscurecer el fondo
        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        pantalla.blit(overlay, (0, 0))

        # Dimensiones del modal
        ancho_modal, alto_modal = 700, 530
        x_modal = (ancho_pantalla - ancho_modal) // 2
        y_modal = (alto_pantalla - alto_modal) // 2
        rect_modal = pygame.Rect(x_modal, y_modal, ancho_modal, alto_modal)

        # Sombra y marco del modal
        pygame.draw.rect(pantalla, (5, 10, 8), (x_modal + 6, y_modal + 6, ancho_modal, alto_modal), border_radius=14)
        pygame.draw.rect(pantalla, (20, 36, 26), rect_modal, border_radius=14)
        pygame.draw.rect(pantalla, (200, 170, 90), rect_modal, width=3, border_radius=14)

        # Encabezado del modal
        if self.fuente_modal_titulo:
            surf_titulo_modal = self.fuente_modal_titulo.render("Instrucciones del Juego", True, (240, 215, 120))
            pantalla.blit(surf_titulo_modal, (x_modal + 30, y_modal + 22))

        pygame.draw.line(pantalla, (80, 130, 95), (x_modal + 30, y_modal + 60), (x_modal + ancho_modal - 30, y_modal + 60), 2)

        # Configuración del recuadro de recorte (Clipping Area) para el texto
        x_clip = x_modal + 30
        y_clip = y_modal + 70
        ancho_clip = ancho_modal - 60
        alto_clip = alto_modal - 130
        rect_clip = pygame.Rect(x_clip, y_clip, ancho_clip, alto_clip)

        # Procesamiento de sublíneas
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

        # APLICAR CLIPPING: Garantiza que nada de texto sobresalga fuera del recuadro
        pantalla.set_clip(rect_clip)

        y_render = y_clip - int(self.scroll_y_instrucciones)
        if self.fuente_modal_cuerpo:
            for sublinea, color in lineas_para_render:
                if y_render + alto_linea >= y_clip and y_render <= y_clip + alto_clip:
                    surf_sub = self.fuente_modal_cuerpo.render(sublinea, True, color)
                    pantalla.blit(surf_sub, (x_clip, y_render))
                y_render += alto_linea

        # QUITAR CLIPPING
        pantalla.set_clip(None)

        # Dibujar barra de scroll si el contenido sobrepasa la altura del recuadro
        if self.max_scroll_y > 0:
            x_bar = x_modal + ancho_modal - 22
            y_bar = y_clip
            h_bar = alto_clip
            pygame.draw.rect(pantalla, (15, 30, 22), (x_bar, y_bar, 8, h_bar), border_radius=4)

            porcentaje_scroll = self.scroll_y_instrucciones / self.max_scroll_y
            h_thumb = max(30, int(h_bar * (alto_clip / altura_total_contenido)))
            y_thumb = y_bar + int((h_bar - h_thumb) * porcentaje_scroll)
            pygame.draw.rect(pantalla, (200, 170, 90), (x_bar, y_thumb, 8, h_thumb), border_radius=4)

        # Botón de Cerrar Modal
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
