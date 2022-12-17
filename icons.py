import arcade


class IconRocket(arcade.Sprite):
    def __init__(self, position):
        super().__init__("Textures/slice26_2.png")
        self._destination_point = None
        if position == 1:
            self.center_x = 1000
            self.center_y = 500
        elif position == 2:
            self.center_x = 3800
            self.center_y = 2300

    def on_update(self, delta_time: float = 1 / 60):
        super().update()


class IconBullet(arcade.Sprite):
    def __init__(self, position):
        super().__init__("Textures/slice34_2.png")
        self._destination_point = None
        if position == 1:
            self.center_x = 1000
            self.center_y = 2300
        elif position == 2:
            self.center_x = 3800
            self.center_y = 500

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
