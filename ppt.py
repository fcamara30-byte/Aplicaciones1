from manim import *

class AnimacionPCP(Scene):
    def construct(self):
        # --- ETAPA 1: TÍTULO E INTRODUCCIÓN ---
        titulo = Text("Simulación de Desgaste PCP", color=BLUE).scale(0.9)
        subtitulo = Text("Optimización de Centralizadores", color=GRAY).scale(0.6)
        subtitulo.next_to(titulo, DOWN)
        
        self.play(Write(titulo), FadeIn(subtitulo, shift=DOWN))
        self.wait(1.5)
        self.play(FadeOut(titulo), FadeOut(subtitulo))

        # --- ETAPA 2: CREACIÓN DE LA TUBERÍA (SURVEY DEVIADO) ---
        # Trayectoria curva basada en los datos de un pozo desviado
        tuberia_centro = CubicBezier(
            LEFT * 3 + UP * 3, 
            LEFT * 3 + DOWN * 1, 
            RIGHT * 1 + DOWN * 2, 
            RIGHT * 3 + DOWN * 3
        )
        
        # Paredes del Tubing
        tuberia_izq = tuberia_centro.copy().shift(LEFT * 0.4)
        tuberia_der = tuberia_centro.copy().shift(RIGHT * 0.4)
        tuberia = VGroup(tuberia_izq, tuberia_der).set_color(GRAY_C).set_stroke(width=4)
        
        etiqueta_tubing = Text("Tubing (Tubería)", color=GRAY_C).scale(0.5).move_to(LEFT * 3.5 + UP * 2)

        self.play(Create(tuberia), FadeIn(etiqueta_tubing))
        self.wait(1)

        # --- ETAPA 3: LA COLUMNA DE VARILLAS ---
        varilla = tuberia_centro.copy().set_color(LIGHT_GREY).set_stroke(width=2)
        etiqueta_varilla = Text("Varilla de Bombeo", color=LIGHT_GREY).scale(0.5).move_to(RIGHT * 2 + UP * 2)

        self.play(Create(varilla), FadeIn(etiqueta_varilla))
        self.wait(1)

        # --- ETAPA 4: EFECTO DE DESGASTE METAL-METAL ---
        # La varilla se deforma hacia la pared por la tensión, cambiando a rojo
        varilla_con_friccion = CubicBezier(
            LEFT * 3.3 + UP * 3, 
            LEFT * 2.7 + DOWN * 0.8, 
            RIGHT * 1.3 + DOWN * 1.8, 
            RIGHT * 2.7 + DOWN * 3
        ).set_color(RED).set_stroke(width=2.5)

        alerta_texto = Text("¡Zona Crítica: Contacto Metal-Metal!", color=RED).scale(0.6).to_edge(UP)
        punto_contacto = Dot(point=LEFT * 0.4 + DOWN * 1.1, color=RED).scale(2)
        fuego_friccion = Flash(punto_contacto, color=YELLOW, num_lines=8, flash_radius=0.5)

        self.play(
            Transform(varilla, varilla_con_friccion),
            FadeIn(alerta_texto),
            Create(punto_contacto)
        )
        self.play(fuego_friccion)
        self.wait(2)

        # --- ETAPA 5: SOLUCIÓN CON CENTRALIZADORES ---
        texto_solucion = Text("Algoritmo: Posicionamiento de Centralizadores", color=GREEN).scale(0.6).to_edge(UP)
        
        # Ubicación óptima calculada por tu aplicación
        centralizador1 = Dot(point=LEFT * 2.4 + UP * 1, color=GREEN).scale(1.8)
        centralizador2 = Dot(point=LEFT * 0.7 + DOWN * 0.8, color=GREEN).scale(1.8)
        centralizador3 = Dot(point=RIGHT * 1.2 + DOWN * 2, color=GREEN).scale(1.8)
        centralizadores = VGroup(centralizador1, centralizador2, centralizador3)

        # La varilla vuelve a su posición segura y centrada
        varilla_centrada = tuberia_centro.copy().set_color(GREEN).set_stroke(width=2)

        self.play(
            Transform(alerta_texto, texto_solucion),
            FadeOut(punto_contacto),
            Transform(varilla, varilla_centrada),
            FadeIn(centralizadores)
        )
        self.wait(1)

        # Conclusión exitosa
        exito_txt = Text("Operación Segura & Vida Útil Prolongada", color=GREEN).scale(0.5).next_to(texto_solucion, DOWN)
        self.play(Write(exito_txt))
        self.wait(3)

        # Limpieza de pantalla
        self.play(FadeOut(VGroup(tuberia, varilla, centralizadores, alerta_texto, exito_txt, etiqueta_tubing, etiqueta_varilla)))

# ==============================================================================
# 3. COMANDO DE REPRODUCCIÓN EN NAVEGADOR (Jupyter / Colab)
# ==============================================================================
# Esta línea le dice al entorno web que renderice el video en calidad baja (rápido)
# y lo muestre directamente en la pantalla.
%manim -v WARNING --progress_bar None -pql AnimacionPCP
