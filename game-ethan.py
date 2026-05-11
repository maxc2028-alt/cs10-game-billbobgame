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
TRASH_SCORE = 4
BUILDING_STAGES = 3


class TrashSpot:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.radius = 18
        self.highlight = random.choice(["can", "bag", "box", "rubble"])


class FriendNPC:
    def __init__(self, name: str, x: float, y: float) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.mood = random.choice(["curious", "hopeful", "quiet", "encouraging"])
        self.line = random.choice(
            [
                "I didn’t think anyone would come back here.",
                "This place used to feel different.",
                "You’re making it easier to stay.",
                "Maybe we can turn this around.",
            ]
        )


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
        self.hint = "Clear every trash pile to move to the next building."
        self.trash_spots: list[TrashSpot] = []
        self.friends: list[FriendNPC] = []
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0
        self.neighborhood_state = 0
        self.round_started = False

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def reset_round(self) -> None:
        self.time_left = QUEST_TIME
        self.cleaned = 0
        self.message = "Click trash piles to clean the building."
        self.hint = "Click trash near the broken windows, doors, and sidewalks."
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
        self.round_started = True

    def next_building(self) -> None:
        self.current_building = (self.current_building + 1) % len(self.building_names)
        self.buildings_cleaned += 1
        self.money += 15 + self.upgrades * 3
        self.friendship += 1
        self.upgrades = min(MAX_UPGRADES, self.upgrades + 1)
        self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
        self.message = f"{self.building_names[self.current_building]} is next. The block looks a little brighter."
        self.hint = "Fresh starts open up as you finish one building and move to the next."
        self.screen = "complete"

    def fail_round(self) -> None:
        self.screen = "failed"
        self.message = "The timer ran out. The block stays quiet for now."
        self.round_started = False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key != arcade.key.SPACE:
            return

        try:
            if self.screen in {"title", "complete", "failed"}:
                self.reset_round()
            elif self.screen == "playing" and not self.round_started:
                self.reset_round()
        except Exception as exc:
            self.screen = "failed"
            self.message = f"Start error: {exc!r}"
            raise

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.screen != "playing" or button != arcade.MOUSE_BUTTON_LEFT:
            return

        for trash in list(self.trash_spots):
            if (x - trash.x) ** 2 + (y - trash.y) ** 2 <= trash.radius ** 2:
                self.trash_spots.remove(trash)
                self.cleaned += 1
                self.money += TRASH_SCORE + self.upgrades
                self.message = random.choice(
                    [
                        "A friend nods. The hallway feels less empty.",
                        "Trash cleared. The building breathes a little easier.",
                        "Someone notices the work and starts to smile.",
                        "You clear a path. The entrance feels safer.",
                    ]
                )
                if self.money % 12 == 0 and self.friendship < 5:
                    self.friendship += 1
                if self.cleaned % 2 == 0:
                    self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
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
        arcade.draw_line(0, 120, 800, 120, (70, 80, 70), 2)

    def draw_building(self, left: float, right: float, base_y: float, height: float, roof_color, wall_color) -> None:
        top = base_y + height
        arcade.draw_lrbt_rectangle_filled(left, right, base_y, top, wall_color)
        arcade.draw_lrbt_rectangle_outline(left, right, base_y, top, arcade.color.BLACK)
        roof_mid = (left + right) / 2
        arcade.draw_triangle_filled(left - 8, top, right + 8, top, roof_mid, top + 60, roof_color)
        arcade.draw_triangle_outline(left - 8, top, right + 8, top, roof_mid, top + 60, arcade.color.BLACK)

    def draw_scene(self) -> None:
        self.draw_background()

        building_colors = [
            (arcade.color.SIENNA, arcade.color.DIM_GRAY),
            (arcade.color.MAROON, arcade.color.SLATE_GRAY),
            (arcade.color.OLIVE, arcade.color.GRAY),
        ]
        building_heights = [220, 235, 195]
        building_positions = [(90, 320, 120), (350, 590, 115), (620, 770, 95)]

        for index, (left, right, base_y) in enumerate(building_positions):
            roof_color, wall_color = building_colors[index]
            height = building_heights[index]
            if index < self.neighborhood_state:
                wall_color = arcade.color.DARK_SEA_GREEN
                roof_color = arcade.color.FOREST_GREEN
            self.draw_building(left, right, base_y, height, roof_color, wall_color)

        arcade.draw_lrbt_rectangle_filled(40, 760, 80, 105, (40, 42, 48))
        arcade.draw_line(0, 105, 800, 105, arcade.color.BLACK, 3)

        for i in range(3):
            arcade.draw_rect_filled(205 + i * 70, 205, 28, 42, arcade.color.LIGHT_STEEL_BLUE)
            arcade.draw_rect_filled(520 + i * 60, 200, 28, 42, arcade.color.LIGHT_STEEL_BLUE)
        arcade.draw_rect_filled(700, 170, 32, 48, arcade.color.LIGHT_STEEL_BLUE)
        arcade.draw_text("bus stop", 675, 138, arcade.color.WHITE, 10)

        for trash in self.trash_spots:
            arcade.draw_circle_filled(trash.x, trash.y, trash.radius, arcade.color.BROWN_NOSE)
            arcade.draw_circle_outline(trash.x, trash.y, trash.radius, arcade.color.BLACK, 2)
            arcade.draw_text(trash.highlight, trash.x - 18, trash.y - 7, arcade.color.WHITE, 9)

        for friend in self.friends:
            arcade.draw_circle_filled(friend.x, friend.y, 16, arcade.color.LIGHT_GREEN)
            arcade.draw_circle_outline(friend.x, friend.y, 16, arcade.color.BLACK, 2)
            arcade.draw_text(friend.name, friend.x - 20, friend.y + 22, arcade.color.WHITE, 10)
            arcade.draw_text(friend.mood, friend.x - 26, friend.y - 34, arcade.color.LIGHT_GRAY, 8)
            arcade.draw_text(friend.line, friend.x - 70, friend.y + 38, arcade.color.WHITE, 8, width=140, multiline=True)

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
        arcade.draw_text(f"Neighborhood level: {self.neighborhood_state + 1}/{BUILDING_STAGES}", 640, 476, arcade.color.WHITE, 12)
        arcade.draw_text(self.message, 22, 450, arcade.color.AMAZON, 15)
        arcade.draw_text(self.hint, 22, 424, arcade.color.LIGHT_GRAY, 11, width=720, multiline=True)

        bar_left = 22
        bar_right = 722
        bar_bottom = 395
        bar_top = 410
        arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, arcade.color.DARK_SLATE_GRAY)
        filled = bar_left + (bar_right - bar_left) * max(0, self.time_left) / QUEST_TIME
        arcade.draw_lrbt_rectangle_filled(bar_left, filled, bar_bottom, bar_top, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_outline(bar_left, bar_right, bar_bottom, bar_top, arcade.color.WHITE)

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
            arcade.draw_text(
                "Clearing more trash unlocks more trust and brighter buildings.",
                400,
                48,
                arcade.color.LIGHT_GRAY,
                11,
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
            arcade.draw_text(
                "You are not just cleaning. You are making room for people to belong.",
                400,
                290,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center",
            )
            arcade.draw_text("Press SPACE to start", 400, 250, arcade.color.GOLD, 18, anchor_x="center")
            self.draw_hud()
            return

        if self.screen == "playing" and not self.round_started:
            self.reset_round()

        self.draw_scene()
        self.draw_hud()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView(window)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
