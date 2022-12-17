import arcade


class Rocket(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/P03 (1).png", hit_box_algorithm='Detailed')
        self._destination_point = None

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
