import arcade
from arcade.resources import (image_laser_blue01)


class Bullet(arcade.Sprite):
    def __init__(self):
        super().__init__(image_laser_blue01, hit_box_algorithm='Detailed')
        self._destination_point = None

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
