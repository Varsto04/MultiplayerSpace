import arcade.gui
from game import *
from client import ClientGame


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None

        self.texture = arcade.load_texture(":resources:images/backgrounds/stars.png")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        sound_button = arcade.Sound(file_name='Sounds/Retro3.wav')

        button_style = {
            "font_size": 30,
            "font_color": arcade.color.AQUA,
            "border_width": 2,
            "border_color": arcade.color.AQUA,
            "bg_color": None,

            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.BLUE,
            "font_color_pressed": arcade.color.BLUE,
        }

        start_button = arcade.gui.UIFlatButton(text="Начать", width=400, height=100, font_size=100, style=button_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        authors_button = arcade.gui.UIFlatButton(text="Авторы", width=400, height=100, style=button_style)
        self.v_box.add(authors_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Выход", width=400, height=100, style=button_style)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        @start_button.event("on_click")
        def on_click_start(event):
            arcade.play_sound(sound_button)
            game_view = EnterView()
            self.window.show_view(game_view)
            self.manager.disable()

        @quit_button.event("on_click")
        def on_click_quit(event):
            arcade.play_sound(sound_button)
            arcade.exit()

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box,)
        )

        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                WINDOW_WIDTH, WINDOW_HEIGHT)
        self.manager.draw()


class EnterView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None

        self.texture = arcade.load_texture(":resources:images/backgrounds/stars.png")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        self.sound_button = arcade.Sound(file_name='Sounds/Retro3.wav')

        button_style = {
            "font_size": 30,
            "font_color": arcade.color.AQUA,
            "border_width": 2,
            "border_color": arcade.color.AQUA,
            "bg_color": None,

            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.BLUE,
            "font_color_pressed": arcade.color.BLUE,
        }

        self.input_field = arcade.gui.UIInputText(text="Введите сюда ваш ник", width=650, height=40, font_size=24,
                                                  text_color=arcade.color.AQUA)
        self.v_box.add(self.input_field)

        self.label = arcade.gui.UILabel(text=f"#Ваш ник: ", width=650, height=40, font_size=16,
                                        text_color=arcade.color.AQUA)
        self.v_box.add(self.label.with_space_around(bottom=0))

        self.label2 = arcade.gui.UILabel(text="", width=650, height=40, font_size=16,
                                         text_color=arcade.color.AQUA)

        submit_button = arcade.gui.UIFlatButton(text="Обновить", width=400, height=40, style=button_style)
        self.v_box.add(submit_button.with_space_around(bottom=10))
        submit_button.on_click = self.on_click

        clear_button = arcade.gui.UIFlatButton(text="Очистить", width=400, height=40, style=button_style)
        self.v_box.add(clear_button.with_space_around(bottom=300))

        start_button = arcade.gui.UIFlatButton(text="Продолжить", width=400, height=100, style=button_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        back_button = arcade.gui.UIFlatButton(text="Назад", width=400, height=100, style=button_style)
        self.v_box.add(back_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box, )
        )

        @clear_button.event("on_click")
        def on_click_start(event):
            arcade.play_sound(self.sound_button)
            self.input_field.text = ''

        @start_button.event("on_click")
        def on_click_start(event):
            arcade.play_sound(self.sound_button)
            if (len(self.input_field.text) <= 20) and (self.input_field.text != 'Введите сюда ваш ник'):
                window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, fullscreen=True)
                game_view = ClientGame()
                window.show_view(game_view)
                self.manager.disable()
            else:
                if len(self.input_field.text) > 20:
                    self.label2.text = '#Ваш ник не должен превышать 20 символов'
                    self.v_box.add(self.label2.with_space_around(bottom=0))
                elif self.input_field.text == 'Введите сюда ваш ник':
                    self.label2.text = '#Вы забыли изменить ник или нажать кнопку "Обновить"'
                    self.v_box.add(self.label2.with_space_around(bottom=0))

        @back_button.event("on_click")
        def on_click_quit(event):
            arcade.play_sound(self.sound_button)
            game_view = StartView()
            self.window.show_view(game_view)
            self.manager.disable()

        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                WINDOW_WIDTH, WINDOW_HEIGHT)
        self.manager.draw()

    def update_text(self):
        self.label.text = f'#Ваш ник: {self.input_field.text}'
        global nickname
        nickname = self.input_field.text

    def on_click(self, event):
        arcade.play_sound(self.sound_button)
        self.update_text()


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, fullscreen=True)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == '__main__':
    main()
