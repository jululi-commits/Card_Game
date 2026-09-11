# Plan de Desarrollo: Videojuego de Solitario Estratégico

## Visión General del Proyecto
Un juego de cartas estilo solitario donde el objetivo es apilar exitosamente las 52 cartas de póker estándar sin superar la restricción de **máximo 26 cartas activas en la mesa** de forma simultánea. El juego cuenta con interacción **Drag & Drop** y **6 cartas especiales** (3 de beneficios y 3 de penalización/desafíos).

## 1. Hoja de Ruta Simple (Resumen Alto Nivel)
[Semana 1] Fundamentos y Tablero Base
   └── Estructura, mazo de 52 cartas, zonas del tablero y lógica del límite (26 cartas).

[Semana 2] Interacción Drag & Drop y Reglas de Juego
   └── Arrastre de cartas, validación de movimientos, apilamiento y estados Win/Lose.

[Semana 3] Sistema de Cartas Especiales (Poderes y Trampas)
   └── Implementación de 3 cartas positivas y 3 cartas negativas con sus efectos.

[Semana 4] Interfaz Visual (UI/UX), Animaciones y Pulido
   └── Diseño visual deslumbrante, animaciones, sonidos, menús y testing.

## 2. Hoja de Ruta Detallada

### 📅 Semana 1: Fundamentos del Juego y Estructura del Tablero
> **Objetivo:** Definir la arquitectura base, la representación visual del mazo y la restricción del límite de mesa.

* **Día 1-2: Configuración del Entorno y Modelo de Datos**
  * Definir clases/estructuras base: `Carta` (Palo, Valor, Estado), `Mazo` (52 cartas de póker), `Pila` y `Tablero`.
  * Generación y mezcla (shuffle) del mazo estándar de 52 cartas.
* **Día 3-4: Maquetación Espacial del Tablero**
  * Creación de las zonas del tablero:
    * **Mazo de Robo (Stock / Waste)**
    * **Pilas de Mesa (Tableau)**
    * **Pilas de Apilamiento Final (Foundations)**
* **Día 5: Control del Límite de Mesa (Regla Central)**
  * Implementar el contador global de cartas visibles en mesa.
  * Lógica para impedir revelar/robar nuevas cartas si se alcanza el **límite de 26 cartas en mesa**.
* **Entregable de la Semana:** Prototipo estático funcional donde se pueden repartir cartas en las distintas zonas respetando el límite de 26 cartas.

---

### 📅 Semana 2: Mecánicas de Interacción (Drag & Drop) y Reglas de Apilado
> **Objetivo:** Permitir al jugador mover cartas con el ratón/táctil y validar las reglas de apilado.

* **Día 1-2: Sistema de Arrastre y Soltado (Drag & Drop)**
  * Captura de eventos de ratón (`onMouseDown`, `onMouseMove`, `onMouseUp`) o táctiles.
  * Feedback visual al arrastrar (elevación de carta, sombra, movimiento fluido del cursor).
* **Día 3: Reglas de Apilamiento y Validaciones**
  * Programar condiciones para colocar cartas en las pilas de mesa (ej. color alterno y valor descendente).
  * Programar condiciones de victoria en la Fundación (apilar por palo de A a K).
  * Validación de soltado inválido (la carta vuelve a su posición original con animación suave).
* **Día 4-5: Flujo de Estado (Victoria / Derrota)**
  * Detección automática de **Victoria:** Las 52 cartas han sido apiladas en la fundación.
  * Detección automática de **Derrota (Game Over):** Se ha alcanzado el límite de 26 cartas en mesa y no existen movimientos válidos.
* **Entregable de la Semana:** Juego de solitario base 100% jugable mediante arrastrar y soltar cartas.

---

### 📅 Semana 3: Sistema de Cartas Especiales (Poderes y Trampas)
> **Objetivo:** Añadir dinamismo y profundidad táctica con cartas especiales.

* **Día 1-2: Cartas de Beneficio (3 Poderes Especiales)**
  1. 🧹 **Carta "Limpiador":** Devuelve 3 cartas de la mesa al mazo de robo para liberar espacio crítico.
  2. ⭐ **Carta "Comodín":** Puede apilarse sobre cualquier carta sin importar palo o valor.
  3. 🧲 **Carta "Magneto":** Agrupa automáticamente la siguiente carta que encaje en la fundación.
* **Día 3-4: Cartas de Penalización (3 Efectos Negativos)**
  1. 🔒 **Carta "Bloqueo":** Inmoviliza una pila de la mesa por 3 turnos/movimientos.
  2. ⚖️ **Carta "Sobrecarga":** Ocupa 2 espacios en el conteo del límite de 26 en la mesa.
  3. 🌀 **Carta "Desorden":** Reorganiza aleatoriamente las cartas no apiladas de 2 columnas al ser robada.
* **Día 5: Integración y Balance**
  * Mezclar las cartas especiales en el mazo con una probabilidad equilibrada.
  * Efectos visuales/iconos diferenciadores en las cartas especiales.
* **Entregable de la Semana:** Gameplay completo con la capa estratégica de superpoderes y obstáculos activa.

---

### 📅 Semana 4: Diseño UI/UX Premium, Animaciones, Sonido y Pulido
> **Objetivo:** Elevar la calidad visual y de experiencia del juego para lograr un acabado profesional.

* **Día 1-2: Interfaz Visual (UI/UX) y Estética**
  * Diseño con paleta de colores pulida (tapete de fieltro verde elegante o tema oscuro modernizado con detalles de neón/glassmorphism).
  * Indicador visual claro y dinámico del conteo de cartas en mesa (Ej: `Cartas en mesa: 18 / 26` con alerta roja al acercarse a 26).
* **Día 3: Animaciones y Micro-interacciones**
  * Transición al voltear cartas.
  * Animación de encaje magnético al soltar cartas en la posición correcta.
  * Animación de celebración de victoria (cascada clásica de cartas o lluvia de partículas).
* **Día 4: Audio, Efectos de Sonido y Menús**
  * Efectos de sonido (deslizar carta, encajar, activar poder especial, game over).
  * Menú Principal (Botón Jugar, Cómo Jugar / Reglas, Reiniciar Partida).
* **Día 5: Pruebas, Ajustes de Rendimiento y Empaquetado**
  * Corrección de bugs edge-case (arrastrar múltiples cartas, límites al borde del tablero).
  * Optimización de rendimiento y pruebas de jugabilidad.
* **Entregable de la Semana:** Juego finalizado, testeado y listo para ser disfrutado.
