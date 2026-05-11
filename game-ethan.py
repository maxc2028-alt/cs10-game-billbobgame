"""Neighborhood Cleanup: a more detailed MVP for the serious game idea.

The player cleans abandoned buildings, meets friends, earns money, and unlocks
small upgrades that make the neighborhood feel more alive.
"""

from __future__ import annotations

import random

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neighborhood Cleanup: South Block"

QUEST_TIME = 20.0
MAX_UPGRADES = 3


class TrashSpot:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.radius = 18


class FriendNPC:
    def __init__(self, name: str, x: float, y: float) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.mood = random.choice(["curious", "hopeful", "quiet", "encouraging"])


class GameView(arcade.View):
    def __init__(self, window: arcade.Window | None = None) -> None:
        super().__init__(window=window)
        self.background_color = arcade.csscolor.DARK_SLATE_BLUE
        self.screen = "title"
        self.time_left = QUEST_TIME
        self.money = 0
        self.friendship = 0
        self.cleaned = 0
        self.upgrades = 0
        self.message = "Press SPACE to begin."
        self.trash_spots: list[TrashSpot] = []
        self.friends: list[FriendNPC] = []
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def reset_round(self) -> None:
        self.time_left = QUEST_TIME
        self.cleaned = 0
        self.message = "Click trash piles to clean the building."
        self.trash_spots = []
        self.friends = []

        building_sets = [
            [(145, 145), (210, 115), (275, 160), (325, 120), (175, 185), (265, 190)],
            [(420, 165), (495, 120), (560, 145), (610, 190), (460, 225), (535, 220)],
            [(650, 120), (705, 165), (715, 245), (640, 225), (690, 190), (755, 120)],
        ]
        friend_positions = [(110, 255), (390, 285), (680, 285)]

        for x, y in building_sets[self.current_building]:
            self.trash_spots.append(TrashSpot(x, y))

        friend_names = ["Maya", "Jordan", "Ari"]
        for i in range(min(self.friendship + 1, 3)):
            fx, fy = friend_positions[i]
            self.friends.append(FriendNPC(friend_names[i], fx, fy))

        self.screen = "playing"

    def next_building(self) -> None:
        self.current_building = (self.current_building + 1) % len(self.building_names)
        self.buildings_cleaned += 1
        self.money += 15
        self.friendship += 1
        self.upgrades = min(MAX_UPGRADES, self.upgrades + 1)
        self.message = f"Neighborhood change spreads. {self.building_names[self.current_building]} is next."
        self.screen = "complete"

    def fail_round(self) -> None:
        self.screen = "failed"
        self.message = "The timer ran out. The block stays quiet for now."

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key != arcade.key.SPACE:
            return

        if self.screen in {"title", "complete", "failed"}:
            self.reset_round()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.screen != "playing" or button != arcade.MOUSE_BUTTON_LEFT:
            return

        for trash in list(self.trash_spots):
            if (x - trash.x) ** 2 + (y - trash.y) ** 2 <= trash.radius ** 2:
                self.trash_spots.remove(trash)
                self.cleaned += 1
                self.money += 4
                self.message = random.choice(
                    [
                        "A friend nods. The hallway feels less empty.",
                        "Trash cleared. The building breathes a little easier.",
                        "Someone notices the work and starts to smile.",
                    ]
                )
                if self.money % 12 == 0 and self.friendship < 5:
                    self.friendship += 1
                break

        if not self.trash_spots:
            self.next_building()

    def on_update(self, delta_time: float) -> None:
        if self.screen != "playing":
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.fail_round()

    def draw_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (31, 38, 57))
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 120, (45, 58, 46))
        arcade.draw_circle_filled(95, 525, 34, arcade.color.GOLD)
        arcade.draw_circle_filled(140, 535, 24, arcade.color.GOLD)
        arcade.draw_circle_filled(700, 525, 22, arcade.color.LIGHT_BLUE)
        arcade.draw_circle_filled(735, 545, 30, arcade.color.WHITE)

    def draw_building(self, left: float, right: float, base_y: float, height: float, roof_color, wall_color) -> None:
        top = base_y + height
        arcade.draw_lrbt_rectangle_filled(left, right, base_y, top, wall_color)
        arcade.draw_lrbt_rectangle_outline(left, right, base_y, top, arcade.color.BLACK)
        roof_mid = (left + right) / 2
        arcade.draw_triangle_filled(left - 8, top, right + 8, top, roof_mid, top + 60, roof_color)
        arcade.draw_triangle_outline(left - 8, top, right + 8, top, roof_mid, top + 60, arcade.color.BLACK)

    def draw_scene(self) -> None:
        self.draw_background()

        self.draw_building(90, 320, 120, 220, arcade.color.SIENNA, arcade.color.DIM_GRAY)
        self.draw_building(350, 590, 115, 235, arcade.color.MAROON, arcade.color.SLATE_GRAY)
        self.draw_building(620, 770, 95, 195, arcade.color.OLIVE, arcade.color.GRAY)

        arcade.draw_lrbt_rectangle_filled(40, 760, 80, 105, (40, 42, 48))
        arcade.draw_line(0, 105, 800, 105, arcade.color.BLACK, 3)

        for i in range(3):
            arcade.draw_rect_filled(205 + i * 70, 205, 28, 42, arcade.color.LIGHT_STEEL_BLUE)
            arcade.draw_rect_filled(520 + i * 60, 200, 28, 42, arcade.color.LIGHT_STEEL_BLUE)
        arcade.draw_rect_filled(700, 170, 32, 48, arcade.color.LIGHT_STEEL_BLUE)

        for trash in self.trash_spots:
            arcade.draw_circle_filled(trash.x, trash.y, trash.radius, arcade.color.BROWN_NOSE)
            arcade.draw_circle_outline(trash.x, trash.y, trash.radius, arcade.color.BLACK, 2)
            arcade.draw_text("trash", trash.x - 18, trash.y - 7, arcade.color.WHITE, 9)

        for friend in self.friends:
            arcade.draw_circle_filled(friend.x, friend.y, 16, arcade.color.LIGHT_GREEN)
            arcade.draw_circle_outline(friend.x, friend.y, 16, arcade.color.BLACK, 2)
            arcade.draw_text(friend.name, friend.x - 20, friend.y + 22, arcade.color.WHITE, 10)
            arcade.draw_text(friend.mood, friend.x - 26, friend.y - 34, arcade.color.LIGHT_GRAY, 8)

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(10, 790, 510, 590, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(10, 790, 510, 590, arcade.color.WHITE)

        arcade.draw_text("Neighborhood Cleanup", 22, 555, arcade.color.WHITE, 22)
        arcade.draw_text(f"Building: {self.building_names[self.current_building]}", 22, 529, arcade.color.LIGHT_GRAY, 13)
        arcade.draw_text(f"Trash cleaned: {self.cleaned}", 22, 500, arcade.color.WHITE, 14)
        arcade.draw_text(f"Money: ${self.money}", 260, 500, arcade.color.WHITE, 14)
        arcade.draw_text(f"Friendship: {self.friendship}", 260, 476, arcade.color.WHITE, 14)
        arcade.draw_text(f"Upgrades: {self.upgrades}/{MAX_UPGRADES}", 420, 500, arcade.color.WHITE, 14)
        arcade.draw_text(f"Time left: {self.time_left:0.1f}s", 640, 500, arcade.color.WHITE, 14)
        arcade.draw_text(self.message, 22, 450, arcade.color.AMAZON, 15)

        if self.screen == "title":
            arcade.draw_text(
                "Press SPACE to begin the first cleanup round.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )
        elif self.screen == "complete":
            arcade.draw_text(
                "Press SPACE to move to the next building.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )
        elif self.screen == "failed":
            arcade.draw_text(
                "Press SPACE to try again with a fresh round.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )
        else:
            arcade.draw_text(
                "Click each trash pile before the timer runs out.",
                400,
                70,
                arcade.color.WHITE,
                16,
                anchor_x="center",
            )

    def on_draw(self) -> None:
        self.clear()

        if self.screen == "title":
            self.draw_background()
            arcade.draw_text("Neighborhood Cleanup", 400, 395, arcade.color.WHITE, 34, anchor_x="center")
            arcade.draw_text(
                "A lonely block becomes a place people want to stay.",
                400,
                350,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
            )
            arcade.draw_text(
                "Clear trash, earn trust, and unlock a better neighborhood.",
                400,
                320,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )
            arcade.draw_text("Press SPACE to start", 400, 250, arcade.color.GOLD, 18, anchor_x="center")
            self.draw_hud()
            return

        self.draw_scene()
        self.draw_hud()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView(window)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
