"""Small MVP for the serious game idea.

Click trash to clean up an abandoned building before the timer ends.
Finish the quest to earn money and friendship, then start a new round.
"""

from __future__ import annotations

import random

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neighborhood Cleanup"

QUEST_TIME = 12.0
TRASH_COUNT = 8

class Trash(arcade.SpriteSolidColor):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(36, 36, center_x=x, center_y=y, color=arcade.color.BROWN_NOSE)


class GameView(arcade.View):
    def __init__(self, window: arcade.Window | None = None) -> None:
        super().__init__(window=window)
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.state = "ready"
        self.time_left = QUEST_TIME
        self.money = 0
        self.friendship = 0
        self.cleaned = 0
        self.message = "Press SPACE to start the cleanup quest."
        self.trash_list: list[Trash] = []

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def start_quest(self) -> None:
        self.time_left = QUEST_TIME
        self.cleaned = 0
        self.state = "playing"
        self.message = "Clean the trash before time runs out."
        self.trash_list = []

        safe_zones = [(120, 150), (250, 430), (430, 170), (610, 360), (680, 150)]
        for _ in range(TRASH_COUNT):
            x, y = random.choice(safe_zones)
            x += random.randint(-35, 35)
            y += random.randint(-35, 35)
            trash = Trash(x, y)
            self.trash_list.append(trash)

    def finish_quest(self, success: bool) -> None:
        self.state = "finished"
        if success:
            self.money += 25
            self.friendship += 1
            self.message = "Quest complete. The space feels more alive."
        else:
            self.message = "Quest failed. Try again to help the neighborhood."

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.SPACE and self.state in {"ready", "finished"}:
            self.start_quest()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.state != "playing" or button != arcade.MOUSE_BUTTON_LEFT:
            return

        for trash in list(self.trash_list):
            if trash.collides_with_point((x, y)):
                trash.remove_from_sprite_lists()
                self.trash_list.remove(trash)
                self.cleaned += 1
                self.money += 3
                self.message = "Trash cleaned. The building gets a little better."
                break

        if not self.trash_list:
            self.finish_quest(True)

    def on_update(self, delta_time: float) -> None:
        if self.state != "playing":
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.finish_quest(False)

    def draw_building(self) -> None:
        arcade.draw_lrbt_rectangle_filled(140, 660, 190, 470, arcade.color.DIM_GRAY)
        arcade.draw_lrbt_rectangle_filled(340, 470, 270, 470, arcade.color.GRAY)
        arcade.draw_lrbt_rectangle_filled(385, 425, 190, 360, arcade.color.DARK_BROWN)
        arcade.draw_lrbt_rectangle_filled(190, 250, 260, 320, arcade.color.LIGHT_GRAY)
        arcade.draw_lrbt_rectangle_filled(550, 610, 260, 320, arcade.color.LIGHT_GRAY)
        arcade.draw_circle_filled(95, 110, 26, arcade.color.GOLD)
        arcade.draw_line(140, 190, 660, 190, arcade.color.BLACK, 3)
        arcade.draw_line(660, 190, 660, 470, arcade.color.BLACK, 3)
        arcade.draw_line(660, 470, 140, 470, arcade.color.BLACK, 3)
        arcade.draw_line(140, 470, 140, 190, arcade.color.BLACK, 3)
        arcade.draw_text("Neighborhood Cleanup", 18, 560, arcade.color.WHITE, 20)

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(12, 788, 515, 582, (20, 24, 34))
        arcade.draw_line(12, 515, 788, 515, arcade.color.WHITE, 2)
        arcade.draw_line(788, 515, 788, 582, arcade.color.WHITE, 2)
        arcade.draw_line(788, 582, 12, 582, arcade.color.WHITE, 2)
        arcade.draw_line(12, 582, 12, 515, arcade.color.WHITE, 2)

        progress = f"Trash cleaned: {self.cleaned}/{TRASH_COUNT}"
        status = f"Money: ${self.money}   Friendship: {self.friendship}"
        timer = f"Time left: {self.time_left:0.1f}s"

        arcade.draw_text(progress, 24, 545, arcade.color.WHITE, 14)
        arcade.draw_text(status, 24, 523, arcade.color.LIGHT_GRAY, 14)
        arcade.draw_text(timer, 640, 545, arcade.color.WHITE, 14, anchor_x="left")
        arcade.draw_text(self.message, 24, 490, arcade.color.AMAZON, 15)

        if self.state == "ready":
            arcade.draw_text(
                "SPACE starts a round. Click each trash pile to clean the space.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )
        elif self.state == "finished":
            arcade.draw_text(
                "Press SPACE for another round.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )

    def on_draw(self) -> None:
        self.clear()
        self.draw_building()

        for trash in self.trash_list:
            trash.draw()
            arcade.draw_text("trash", trash.center_x - 18, trash.center_y - 8, arcade.color.WHITE, 9)

        self.draw_hud()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView(window)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
