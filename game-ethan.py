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


class RepairSpot:
    def __init__(self, x: float, y: float, label: str, color) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        self.radius = 28
        self.fixed = False


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
        self.camera: arcade.Camera2D | None = None
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
        self.repair_spots: list[RepairSpot] = []
        self.friends: list[FriendNPC] = []
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0
        self.neighborhood_state = 0
        self.round_started = False
        self.configure_camera()

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)
        self.configure_camera()

    def configure_camera(self) -> None:
        if self.window is None:
            return

        self.camera = arcade.Camera2D(
            viewport=arcade.LBWH(0, 0, self.window.width, self.window.height),
            projection=arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            position=(0, 0),
            window=self.window,
        )

    def on_resize(self, width: int, height: int) -> None:
        self.configure_camera()

    def reset_round(self) -> None:
        self.time_left = QUEST_TIME
        self.cleaned = 0
        self.repair_spots = []
        self.message = "Click trash piles to clean the building."
        self.hint = "After the outside is clean, you will go inside and repair the house."
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

    def enter_house(self) -> None:
        repair_sets = [
            [
                (250, 295, "patch wall", arcade.color.LIGHT_STEEL_BLUE),
                (400, 190, "fix floor", arcade.color.GOLD),
                (545, 330, "repair window", arcade.color.LIGHT_BLUE),
                (510, 225, "paint trim", arcade.color.DARK_SEA_GREEN),
            ],
            [
                (230, 325, "repair window", arcade.color.LIGHT_BLUE),
                (350, 200, "fix floor", arcade.color.GOLD),
                (490, 300, "patch wall", arcade.color.LIGHT_STEEL_BLUE),
                (585, 210, "fix door", arcade.color.SIENNA),
            ],
            [
                (230, 215, "fix floor", arcade.color.GOLD),
                (370, 335, "patch wall", arcade.color.LIGHT_STEEL_BLUE),
                (520, 335, "repair window", arcade.color.LIGHT_BLUE),
                (575, 220, "paint trim", arcade.color.DARK_SEA_GREEN),
            ],
        ]

        self.repair_spots = [
            RepairSpot(x, y, label, color)
            for x, y, label, color in repair_sets[self.current_building]
        ]
        self.screen = "repair"
        self.round_started = False
        self.message = f"You enter {self.building_names[self.current_building]}. Click each repair spot."
        self.hint = "Fix the wall, floor, windows, and door to finish this house."

    def next_building(self) -> None:
        finished_building = self.building_names[self.current_building]
        self.current_building = (self.current_building + 1) % len(self.building_names)
        self.buildings_cleaned += 1
        self.money += 15 + self.upgrades * 3
        self.friendship += 1
        self.upgrades = min(MAX_UPGRADES, self.upgrades + 1)
        self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
        self.message = f"{finished_building} is repaired. {self.building_names[self.current_building]} is next."
        self.hint = "Fresh starts open up as you finish one building and move to the next."
        self.screen = "complete"

    def finish_repair(self) -> None:
        self.money += 10 + self.upgrades * 2
        self.friendship += 1
        self.next_building()

    def fail_round(self) -> None:
        self.screen = "failed"
        self.message = "The timer ran out. The block stays quiet for now."
        self.round_started = False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            if self.window is not None:
                self.window.close()
            return

        if key == arcade.key.E and self.screen == "playing" and not self.trash_spots:
            self.enter_house()
            return

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
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.camera is not None:
            world_position = self.camera.unproject((x, y))
            x = world_position.x
            y = world_position.y

        if self.screen == "repair":
            for spot in self.repair_spots:
                if spot.fixed:
                    continue
                if (x - spot.x) ** 2 + (y - spot.y) ** 2 <= spot.radius ** 2:
                    spot.fixed = True
                    self.money += 3 + self.upgrades
                    self.message = f"Fixed: {spot.label}."
                    self.hint = "Keep repairing the marked spots until the house is ready."
                    if all(repair.fixed for repair in self.repair_spots):
                        self.finish_repair()
                    return
            return

        if self.screen != "playing":
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
            self.enter_house()

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

        window_width = min(32, max(22, (right - left) / 5))
        window_height = min(42, max(30, height / 5))
        window_bottom = base_y + min(82, height - window_height - 24)
        window_top = window_bottom + window_height
        window_count = 2 if right - left < 180 else 3
        gap = (right - left) / (window_count + 1)

        for i in range(window_count):
            center_x = left + gap * (i + 1)
            window_left = center_x - window_width / 2
            window_right = center_x + window_width / 2
            arcade.draw_lrbt_rectangle_filled(
                window_left,
                window_right,
                window_bottom,
                window_top,
                arcade.color.LIGHT_STEEL_BLUE,
            )
            arcade.draw_lrbt_rectangle_outline(window_left, window_right, window_bottom, window_top, arcade.color.BLACK)

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

        arcade.draw_text("bus stop", 675, 138, arcade.color.WHITE, 10)

        for trash in self.trash_spots:
            arcade.draw_circle_filled(trash.x, trash.y, trash.radius, arcade.color.BROWN_NOSE)
            arcade.draw_circle_outline(trash.x, trash.y, trash.radius, arcade.color.BLACK, 2)
            arcade.draw_text(trash.highlight, trash.x, trash.y - 5, arcade.color.WHITE, 8, anchor_x="center")

        for friend in self.friends:
            arcade.draw_circle_filled(friend.x, friend.y, 16, arcade.color.LIGHT_GREEN)
            arcade.draw_circle_outline(friend.x, friend.y, 16, arcade.color.BLACK, 2)
            arcade.draw_text(friend.name, friend.x, friend.y + 24, arcade.color.WHITE, 10, anchor_x="center")
            arcade.draw_text(friend.mood, friend.x, friend.y - 34, arcade.color.LIGHT_GRAY, 8, anchor_x="center")

    def draw_house_interior(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (34, 30, 40))
        arcade.draw_lrbt_rectangle_filled(90, 710, 120, 470, (84, 75, 88))
        arcade.draw_lrbt_rectangle_outline(90, 710, 120, 470, arcade.color.BLACK, 3)
        arcade.draw_lrbt_rectangle_filled(90, 710, 80, 120, (96, 76, 55))
        arcade.draw_line(90, 120, 710, 120, arcade.color.BLACK, 3)

        arcade.draw_lrbt_rectangle_filled(165, 245, 315, 405, arcade.color.DARK_SLATE_BLUE)
        arcade.draw_lrbt_rectangle_outline(165, 245, 315, 405, arcade.color.BLACK, 2)
        arcade.draw_line(205, 315, 205, 405, arcade.color.BLACK, 2)
        arcade.draw_line(165, 360, 245, 360, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(540, 620, 315, 405, arcade.color.DARK_SLATE_BLUE)
        arcade.draw_lrbt_rectangle_outline(540, 620, 315, 405, arcade.color.BLACK, 2)
        arcade.draw_line(580, 315, 580, 405, arcade.color.BLACK, 2)
        arcade.draw_line(540, 360, 620, 360, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(360, 440, 120, 260, (83, 58, 42))
        arcade.draw_lrbt_rectangle_outline(360, 440, 120, 260, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(425, 195, 4, arcade.color.GOLD)

        arcade.draw_text(
            f"Inside {self.building_names[self.current_building]}",
            400,
            485,
            arcade.color.WHITE,
            22,
            anchor_x="center",
        )

        for spot in self.repair_spots:
            if spot.fixed:
                arcade.draw_circle_filled(spot.x, spot.y, 16, arcade.color.DARK_SEA_GREEN)
                arcade.draw_text("fixed", spot.x, spot.y - 5, arcade.color.WHITE, 8, anchor_x="center")
                continue

            arcade.draw_circle_filled(spot.x, spot.y, spot.radius, spot.color)
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius, arcade.color.WHITE, 3)
            arcade.draw_text(spot.label, spot.x, spot.y - 5, arcade.color.BLACK, 8, anchor_x="center")

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(10, 790, 388, 590, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(10, 790, 388, 590, arcade.color.WHITE)

        arcade.draw_text("Neighborhood Cleanup", 22, 562, arcade.color.WHITE, 22)
        arcade.draw_text(f"Building: {self.building_names[self.current_building]}", 22, 536, arcade.color.LIGHT_GRAY, 13)
        arcade.draw_text(f"Trash: {self.cleaned}", 22, 510, arcade.color.WHITE, 13)
        arcade.draw_text(f"Money: ${self.money}", 150, 510, arcade.color.WHITE, 13)
        arcade.draw_text(f"Friendship: {self.friendship}", 280, 510, arcade.color.WHITE, 13)
        arcade.draw_text(f"Upgrades: {self.upgrades}/{MAX_UPGRADES}", 430, 510, arcade.color.WHITE, 13)
        arcade.draw_text(f"Time: {self.time_left:0.1f}s", 640, 510, arcade.color.WHITE, 13)
        fixed_count = sum(1 for repair in self.repair_spots if repair.fixed)
        repair_total = len(self.repair_spots)
        if self.screen == "repair" and repair_total:
            arcade.draw_text(f"Repairs: {fixed_count}/{repair_total}", 22, 490, arcade.color.LIGHT_GRAY, 12)
        else:
            arcade.draw_text(f"Neighborhood level: {self.neighborhood_state + 1}/{BUILDING_STAGES}", 22, 490, arcade.color.LIGHT_GRAY, 12)

        bar_left = 22
        bar_right = 778
        bar_bottom = 462
        bar_top = 476
        arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, arcade.color.DARK_SLATE_GRAY)
        filled = bar_left + (bar_right - bar_left) * max(0, self.time_left) / QUEST_TIME
        arcade.draw_lrbt_rectangle_filled(bar_left, filled, bar_bottom, bar_top, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_outline(bar_left, bar_right, bar_bottom, bar_top, arcade.color.WHITE)

        arcade.draw_text(self.message, 22, 436, arcade.color.AMAZON, 14, width=745, multiline=True)
        arcade.draw_text(self.hint, 22, 410, arcade.color.LIGHT_GRAY, 11, width=745, multiline=True)

        arcade.draw_lrbt_rectangle_filled(140, 660, 34, 86, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(140, 660, 34, 86, arcade.color.WHITE)

        if self.screen == "title":
            arcade.draw_text(
                "Press SPACE to begin the first cleanup round.",
                400,
                63,
                arcade.color.WHITE,
                14,
                anchor_x="center",
            )
        elif self.screen == "complete":
            arcade.draw_text(
                "Press SPACE to move to the next building.",
                400,
                63,
                arcade.color.WHITE,
                14,
                anchor_x="center",
            )
        elif self.screen == "failed":
            arcade.draw_text(
                "Press SPACE to try again with a fresh round.",
                400,
                63,
                arcade.color.WHITE,
                14,
                anchor_x="center",
            )
        elif self.screen == "repair":
            arcade.draw_text(
                "Click the marked repair spots to fix this house.",
                400,
                63,
                arcade.color.WHITE,
                14,
                anchor_x="center",
            )
            arcade.draw_text(
                "When every repair is finished, the next building unlocks.",
                400,
                44,
                arcade.color.LIGHT_GRAY,
                11,
                anchor_x="center",
            )
        else:
            arcade.draw_text(
                "Click each trash pile before the timer runs out.",
                400,
                63,
                arcade.color.WHITE,
                14,
                anchor_x="center",
            )
            arcade.draw_text(
                "Clearing more trash unlocks more trust and brighter buildings.",
                400,
                44,
                arcade.color.LIGHT_GRAY,
                11,
                anchor_x="center",
            )
        arcade.draw_text("Press ESC to quit.", 400, 24, arcade.color.LIGHT_GRAY, 10, anchor_x="center")

    def on_draw(self) -> None:
        self.clear()
        if self.camera is not None:
            self.camera.use()

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
            arcade.draw_lrbt_rectangle_filled(180, 620, 190, 250, (18, 22, 31))
            arcade.draw_lrbt_rectangle_outline(180, 620, 190, 250, arcade.color.WHITE)
            arcade.draw_text("Press SPACE to start", 400, 222, arcade.color.GOLD, 18, anchor_x="center")
            arcade.draw_text("Press ESC to quit.", 400, 198, arcade.color.LIGHT_GRAY, 10, anchor_x="center")
            return

        if self.screen == "playing" and not self.round_started:
            self.reset_round()

        if self.screen == "repair":
            self.draw_house_interior()
        else:
            self.draw_scene()
        self.draw_hud()


def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
    view = GameView(window)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
