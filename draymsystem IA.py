import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard

Window.softinput_mode = 'below_target'

# Importar el Orquestador actual del sistema con manejo estricto de excepciones
try:
    from core.orquestador import Orquestador
    print("✅ Orquestador cargado correctamente")
except Exception as e:
    print(f"❌ Error cargando Orquestador: {e}")
    raise


class CanvasBoxLayout(BoxLayout):
    def __init__(self, bg_color=(0.1, 0.1, 0.1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class ChatMessage(BoxLayout):
    """Globo de mensaje estable con opción de copiar texto y metadatos de ejecución."""
    def __init__(self, sender, text, is_user=False, details=None, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, padding=dp(10), spacing=dp(5), **kwargs)
        
        bg_color = (0.14, 0.38, 0.92, 1) if is_user else (0.12, 0.16, 0.23, 1)
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Encabezado
        if not is_user:
            header_text = f"[b]{sender}[/b]"
            self.lbl_header = Label(
                text=header_text, 
                markup=True, 
                size_hint_y=None, 
                height=dp(20), 
                halign='left', 
                valign='middle',
                color=(0.38, 0.65, 0.98, 1)
            )
            self.lbl_header.bind(size=self.lbl_header.setter('text_size'))
            self.add_widget(self.lbl_header)

        # Contenido principal de texto
        self.content_label = Label(
            text=text, 
            markup=True, 
            size_hint_y=None, 
            halign='left', 
            valign='top',
            color=(0.94, 0.96, 0.98, 1)
        )
        self.content_label.text_size = (Window.width - dp(40), None)
        self.content_label.bind(texture_size=self._on_texture_size)
        self.add_widget(self.content_label)

        # Metadatos de ejecución (si existen y es mensaje del bot)
        if not is_user and details and isinstance(details, dict):
            modo = details.get('modo', 'individual')
            agentes = details.get('agentes_utilizados', ['N/A'])
            if isinstance(agentes, list):
                agentes_str = ", ".join(str(a) for a in agentes)
            else:
                agentes_str = str(agentes)
            duracion = details.get('duracion', 'N/A')
            errores = details.get('errores', None)

            meta_text = f"[size=10][color=60a5fa]Modo:[/color] {modo} | [color=60a5fa]Agentes:[/color] {agentes_str} | [color=60a5fa]Duración:[/color] {duracion}[/size]"
            if errores:
                meta_text += f"\n[size=10][color=ef4444]Errores:[/color] {errores}[/size]"

            self.lbl_meta = Label(
                text=meta_text,
                markup=True,
                size_hint_y=None,
                halign='left',
                valign='top',
                color=(0.7, 0.7, 0.7, 1)
            )
            self.lbl_meta.text_size = (Window.width - dp(40), None)
            self.lbl_meta.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
            self.add_widget(self.lbl_meta)

        # Botón discreto para copiar respuesta
        if not is_user:
            self.btn_copy = Button(
                text="📋 Copiar texto",
                size_hint_y=None,
                height=dp(25),
                background_normal='',
                background_color=(0.2, 0.25, 0.33, 1),
                color=(0.8, 0.8, 0.8, 1),
                font_size=dp(11)
            )
            self.btn_copy.bind(on_release=lambda b: Clipboard.copy(text))
            self.add_widget(self.btn_copy)

        Clock.schedule_once(self._fix_height, 0.05)

    def _on_texture_size(self, instance, value):
        instance.height = value[1]

    def _fix_height(self, dt):
        self.content_label.text_size = (self.width - dp(20), None)
        self.content_label.texture_update()
        self.content_label.height = self.content_label.texture_size[1]
        
        extra = dp(20)
        if hasattr(self, 'btn_copy'):
            extra += dp(30)
        if hasattr(self, 'lbl_meta'):
            self.lbl_meta.text_size = (self.width - dp(20), None)
            self.lbl_meta.texture_update()
            extra += self.lbl_meta.texture_size[1] + dp(5)

        self.height = self.content_label.height + extra

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class DraymSystemApp(App):
    def build(self):
        self.title = "DraymSystem - IA Híbrida Estable"
        self.orquestador = None
        system_status_text = "● activo"
        status_color = (0.22, 0.78, 0.42, 1)

        # Inicializar el orquestador y obtener estado real
        try:
            self.orquestador = Orquestador()
            if hasattr(self.orquestador, 'obtener_estado'):
                estado = self.orquestador.obtener_estado()
                ver = estado.get('version', '1.0')
                ags = estado.get('agentes_registrados', 0)
                mem = "Sí" if estado.get('memoria_activa') else "No"
                sup = "Sí" if estado.get('supervisor_activo') else "No"
                enj = "Sí" if estado.get('enjambre_activo') else "No"
                self.system_info_str = f"Ver: {ver} | Agentes: {ags} | Mem: {mem} | Sup: {sup} | Enj: {enj}"
            else:
                self.system_info_str = "Orquestador activo sin método de estado."
        except Exception as e:
            print(f"Error iniciando orquestador: {e}")
            self.orquestador = None
            system_status_text = "● error"
            status_color = (0.9, 0.2, 0.2, 1)
            self.system_info_str = f"Error de inicialización: {str(e)}"

        main_layout = CanvasBoxLayout(bg_color=(0.06, 0.09, 0.16, 1), orientation='vertical')

        # ==================== 1. HEADER ====================
        header = CanvasBoxLayout(bg_color=(0.09, 0.12, 0.18, 1), orientation='horizontal', size_hint_y=None, height=dp(65), padding=dp(10))
        
        header_title = Label(
            text=f"[b]DraymSystem[/b]\n[size=9][color=9ca3af]{self.system_info_str}[/color][/size]",
            markup=True,
            halign='left',
            valign='middle'
        )
        header_title.bind(size=header_title.setter('text_size'))
        
        header_right_layout = BoxLayout(orientation='horizontal', size_hint_x=None, width=dp(120), spacing=dp(5))
        
        self.lbl_status = Label(
            text=system_status_text,
            color=status_color,
            size_hint_x=None,
            width=dp(65),
            font_size=12,
            bold=True,
            halign='right'
        )

        btn_clear = Button(
            text="🗑️", 
            size_hint_x=None, 
            width=dp(45), 
            background_normal='', 
            background_color=(0.8, 0.2, 0.2, 1)
        )
        btn_clear.bind(on_release=self.limpiar_chat)

        header_right_layout.add_widget(self.lbl_status)
        header_right_layout.add_widget(btn_clear)

        header.add_widget(header_title)
        header.add_widget(header_right_layout)
        main_layout.add_widget(header)

        # ==================== 2. ÁREA DE CHAT ====================
        self.chat_scroll = ScrollView(size_hint=(1, 1))
        self.chat_box = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(10))
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.chat_scroll.add_widget(self.chat_box)
        main_layout.add_widget(self.chat_scroll)

        if self.orquestador:
            self.agregar_mensaje_bot("🤖 DraymSystem Bot", "Sistema autónomo inicializado correctamente. El orquestador gestiona todas las tareas.")
        else:
            self.agregar_mensaje_bot("⚠️ Alerta de Sistema", f"No se pudo cargar el orquestador:\n{self.system_info_str}")

        # ==================== 3. INDICADOR DE PROCESANDO ====================
        self.lbl_thinking = Label(
            text="Procesando consulta mediante el pipeline autónomo...",
            size_hint_y=None,
            height=0,
            font_size=11,
            color=(0.6, 0.6, 0.6, 1)
        )
        main_layout.add_widget(self.lbl_thinking)

        # ==================== 4. FOOTER / ENTRADA ====================
        footer = CanvasBoxLayout(
            bg_color=(0.09, 0.12, 0.18, 1), 
            orientation='horizontal', 
            size_hint_y=None, 
            height=dp(70), 
            padding=dp(10), 
            spacing=dp(10)
        )

        self.input_text = TextInput(
            hint_text="Escribe tu consulta aquí...",
            multiline=False,
            background_color=(0.06, 0.09, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.6, 1, 1),
            disabled=(self.orquestador is None)
        )
        self.input_text.bind(on_text_validate=self.enviar_mensaje)

        self.btn_send = Button(
            text="➤ Enviar",
            size_hint_x=None,
            width=dp(90),
            background_normal='',
            background_color=(0.14, 0.38, 0.92, 1),
            bold=True,
            disabled=(self.orquestador is None)
        )
        self.btn_send.bind(on_release=self.enviar_mensaje)

        footer.add_widget(self.input_text)
        footer.add_widget(self.btn_send)
        main_layout.add_widget(footer)

        return main_layout

    def limpiar_chat(self, instance):
        self.chat_box.clear_widgets()
        self.agregar_mensaje_bot("🤖 DraymSystem Bot", "Chat limpiado. Listo para nuevas consultas.")

    def agregar_mensaje_usuario(self, texto):
        msg = ChatMessage(sender="Tú", text=texto, is_user=True)
        self.chat_box.add_widget(msg)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)

    def agregar_mensaje_bot(self, sender, texto, details=None):
        msg = ChatMessage(sender=sender, text=texto, is_user=False, details=details)
        self.chat_box.add_widget(msg)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)

    def enviar_mensaje(self, instance):
        texto = self.input_text.text.strip()
        if not texto or not self.orquestador:
            return

        self.agregar_mensaje_usuario(texto)
        self.input_text.text = ""
        self.input_text.disabled = True
        self.btn_send.disabled = True
        self.lbl_thinking.height = dp(25)

        threading.Thread(target=self._procesar_en_hilo, args=(texto,), daemon=True).start()

    def _procesar_en_hilo(self, prompt):
        respuesta = ""
        detalles = {}
        start_time = time.time()
        
        try:
            if hasattr(self.orquestador, 'procesar'):
                try:
                    res = self.orquestador.procesar(prompt, devolver_detalles=True)
                    if isinstance(res, dict):
                        respuesta = res.get('respuesta', str(res))
                        detalles = res
                    else:
                        respuesta = str(res)
                        detalles = {"modo": "individual", "agentes_utilizados": ["Orquestador"]}
                except TypeError:
                    respuesta = self.orquestador.procesar(prompt)
                    detalles = {"modo": "individual", "agentes_utilizados": ["Orquestador"]}
            else:
                respuesta = "El orquestador no cuenta con el método procesar."
        except Exception as e:
            respuesta = f"Error al procesar consulta: {str(e)}"
            detalles = {"modo": "error", "errores": str(e)}
        
        duracion = time.time() - start_time
        if isinstance(detalles, dict) and 'duracion' not in detas: # safe check or fallback
            pass
        if isinstance(detalles, dict) and 'duracion' not in detalles:
            detalles['duracion'] = f"{duracion:.2f}s"

        Clock.schedule_once(lambda dt: self._actualizar_gui(respuesta, detalles), 0)

    def _actualizar_gui(self, respuesta, detalles):
        self.agregar_mensaje_bot("🤖 DraymSystem", respuesta, details=detalles)
        self.lbl_thinking.height = 0
        self.input_text.disabled = False
        self.btn_send.disabled = False
        self.input_text.focus = True


if __name__ == "__main__":
    DraymSystemApp().run()
