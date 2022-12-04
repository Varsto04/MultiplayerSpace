import arcade
from arcade.resources import (image_laser_blue01)


class Bullet(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/fighter3.png", hit_box_algorithm='Detailed')
        self._destination_point = None
        self.speed = 20

    def on_update(self, delta_time: float = 1 / 10):
        super().update()
