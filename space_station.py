import arcade


class Station(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/communications.png")

    def on_update(self, delta_time: float = 1 / 60):
        super().update()


class Station2(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/scientists.png")

    def on_update(self, delta_time: float = 1 / 60):
        super().update()


class Station3(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/logistics.png")

    def on_update(self, delta_time: float = 1 / 60):
        super().update()


class Station4(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/government.png")

    def on_update(self, delta_time: float = 1 / 60):
        super().update()


class StationNPC(arcade.Sprite):
    def __init__(self):
        super().__init__("Textures/station.png")

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
