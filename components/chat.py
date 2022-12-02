import arcade.gui

CHAT_LIST_SIZE = 10

window = None


class ChatInputBox(arcade.gui.UIInputText):
    def __init__(self, window):
        window_size = window.get_size()
        super().__init__(width=window_size[0] * .99, height=25, text="Введите сюда ваш ник",
                         font_size=24, text_color=arcade.color.AQUA)
        self.alpha = 0
        self.id = 'chat'


class UIChat(arcade.gui.UIManager):
    def __init__(self, window):
        super().__init__()
        self.window_size = window.get_size()
        self.chat_input = ChatInputBox(window)
        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.chat_input)
        self.message_list = []
        self.message_alpha = 255

    def store_message(self, message):
        if len(self.message_list) == CHAT_LIST_SIZE:
            self.message_list.pop(0)
        self.message_list.append(message)

    def send_message(self, message):
        self.store_message(message)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.T and not self.chat_input.focused:
            self.chat_input.text = ''
            self.focused_element = self.chat_input
        if self.chat_input.focused and symbol == arcade.key.ENTER:
            if self.chat_input.text != '':
                self.send_message(self.chat_input.text)
                self.chat_input.text = ''
                self.focused_element = None
            elif self.chat_input.text == '':
                self.focused_element = None

    def on_update(self, dt):
        super().on_update(dt)
        if not self.chat_input.focused:
            self.chat_input.alpha = 0
        if self.chat_input.focused:
            self.chat_input.alpha = 255

    def on_draw(self):
        super().draw()
        pos_y = self.window_size[1] - 19
        for message in self.message_list:
            arcade.draw_text(
                text=message,
                start_x=5,
                start_y=pos_y,
                color=arcade.csscolor.AQUA,
            )
            pos_y -= 13
