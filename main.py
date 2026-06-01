import os
from kivy.config import Config

# Simula tamanho de celular se rodar no PC
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    WindowManager = autoclass('android.view.WindowManager$LayoutParams')

CAMINHO_FUNDO = os.path.join(os.path.dirname(__file__), "fundo.png")


class TelaInicial(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout_fundo = MDFloatLayout()

        imagem_fundo = Image(
            source=CAMINHO_FUNDO,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        layout_fundo.add_widget(imagem_fundo)

        cartao = MDCard(
            orientation='vertical',
            padding=24,
            spacing=20,
            size_hint=(0.85, 0.6),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            md_bg_color=(0.15, 0.15, 0.18, 0.85),
            elevation=4,
            radius=[24, 24, 24, 24]
        )

        icone_app = MDIconButton(
            icon="lightbulb-outline",
            icon_size="80sp",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1, 1),
            pos_hint={"center_x": 0.5}
        )

        titulo = MDLabel(
            text="Mesa de Luz\nInteligente",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        subtitulo = MDLabel(
            text="Selecione uma imagem para começar o decalque perfeito.",
            halign="center",
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1)
        )

        btn_carregar = MDFillRoundFlatButton(
            text="ABRIR GALERIA",
            font_style="Button",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            md_bg_color=(0.2, 0.6, 1, 1),
            text_color=(1, 1, 1, 1),
            on_release=self.abrir_gerenciador
        )

        cartao.add_widget(icone_app)
        cartao.add_widget(titulo)
        cartao.add_widget(subtitulo)
        cartao.add_widget(btn_carregar)

        layout_fundo.add_widget(cartao)
        self.add_widget(layout_fundo)

        self.file_manager = MDFileManager(
            exit_manager=self.fechar_gerenciador,
            select_path=self.imagem_selecionada,
            preview=True
        )

    def abrir_gerenciador(self, instance):
        path = os.path.expanduser("~")
        self.file_manager.show(path)

    def fechar_gerenciador(self, *args):
        self.file_manager.close()

    def imagem_selecionada(self, path):
        self.fechar_gerenciador()
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):
            tela_desenho = self.manager.get_screen('desenho')
            tela_desenho.carregar_nova_imagem(path)
            self.manager.current = 'desenho'


class TelaDesenho(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bloqueado = False
        Window.bind(on_key_down=self.detectar_tecla)

        self.layout_principal = MDFloatLayout(md_bg_color=(0, 0, 0, 1))

        self.area_zoom = Scatter(
            do_rotation=False,
            do_translation=True,
            do_scale=True,
            auto_bring_to_front=False
        )

        self.imagem = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None)
        )

        self.area_zoom.add_widget(self.imagem)
        self.layout_principal.add_widget(self.area_zoom)

        self.header = MDBoxLayout(
            size_hint=(1, 0.08),
            pos_hint={"x": 0, "y": 0.92},
            md_bg_color=(0.1, 0.1, 0.12, 0.8),
            padding=[10, 0, 10, 0]
        )

        self.btn_voltar = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            pos_hint={"center_y": 0.5},
            on_release=self.voltar_tela
        )

        self.label_titulo = MDLabel(
            text="Ajuste seu Desenho",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="Subtitle1",
            halign="left",
            pos_hint={"center_y": 0.5}
        )

        self.header.add_widget(self.btn_voltar)
        self.header.add_widget(self.label_titulo)
        self.layout_principal.add_widget(self.header)

        self.btn_lock = MDFillRoundFlatButton(
            text="TRAVAR TELA (LOCK)",
            font_style="H6",
            size_hint=(0.85, 0.08),
            pos_hint={"center_x": 0.5, "y": 0.04},
            md_bg_color=(0.12, 0.75, 0.35, 1),
            text_color=(1, 1, 1, 1),
            on_release=self.travar_tela
        )

        self.layout_principal.add_widget(self.btn_lock)
        self.add_widget(self.layout_principal)

    def carregar_nova_imagem(self, caminho_imagem):
        self.imagem.source = caminho_imagem
        self.imagem.texture_update()

        if self.imagem.texture:
            img_w, img_h = self.imagem.texture.size
        else:
            img_w, img_h = Window.width, Window.height

        self.imagem.size = (img_w, img_h)

        escala_w = Window.width / img_w
        escala_h = Window.height / img_h
        escala_inicial = max(escala_w, escala_h)

        self.area_zoom.scale = escala_inicial
        self.area_zoom.pos = (
            (Window.width - (img_w * escala_inicial)) / 2,
            (Window.height - (img_h * escala_inicial)) / 2
        )

    def travar_tela(self, instance):
        self.bloqueado = True
        self.area_zoom.do_translation = False
        self.area_zoom.do_scale = False

        self.header.opacity = 0
        self.btn_voltar.disabled = True

        self.btn_lock.disabled = True
        self.btn_lock.text = "🔒 TELA CONGELADA (Vol + para Sair)"
        self.btn_lock.md_bg_color = (0.85, 0.2, 0.2, 0.4)
        self.btn_lock.text_color = (1, 1, 1, 0.7)

        if platform == 'android':
            activity = PythonActivity.mActivity
            window = activity.getWindow()
            window.addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)

    def destravar_tela(self):
        self.bloqueado = False
        self.area_zoom.do_translation = True
        self.area_zoom.do_scale = True

        self.header.opacity = 1
        self.btn_voltar.disabled = False

        self.btn_lock.disabled = False
        self.btn_lock.text = "TRAVAR TELA (LOCK)"
        self.btn_lock.md_bg_color = (0.12, 0.75, 0.35, 1)
        self.btn_lock.text_color = (1, 1, 1, 1)

    def detectar_tecla(self, window, key, scancode, codepoint, modifier):
        if self.bloqueado and (key == 24 or key in [270, 61] or codepoint == '+'):
            self.destravar_tela()
            return True
        return False

    def on_touch_down(self, touch):
        if self.bloqueado:
            return True
        return super().on_touch_down(touch)

    def voltar_tela(self, instance):
        self.manager.current = 'inicial'


class AppMesaDeLuz(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        sm = MDScreenManager()
        sm.add_widget(TelaInicial(name='inicial'))
        sm.add_widget(TelaDesenho(name='desenho'))
        return sm


if __name__ == "__main__":
    AppMesaDeLuz().run()