"""Serious Game Project MVP.

Clean up abandoned buildings, make friends, and earn enough money to build a home.
Run with: python3 game.py
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

import arcade

def _draw_rectangle_filled_compat(x: float, y: float, width: float, height: float, color) -> None:
    arcade.draw_lbwh_rectangle_filled(x - width / 2, y - height / 2, width, height, color)


def _draw_rectangle_outline_compat(x: float, y: float, width: float, height: float, color, border_width: float = 1) -> None:
    arcade.draw_lbwh_rectangle_outline(x - width / 2, y - height / 2, width, height, color, border_width)


arcade.draw_rectangle_filled = _draw_rectangle_filled_compat
arcade.draw_rectangle_outline = _draw_rectangle_outline_compat


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Serious Game Project MVP"

PLAY_LEFT = 0
PLAY_RIGHT = 900
SIDEBAR_LEFT = 920
SIDEBAR_RIGHT = 1260

PLAYER_SPEED = 250
PLAYER_RADIUS = 18
CLICK_RADIUS = 92
COLLECT_RANGE = 165
FRIEND_HELP_RANGE = 150
FRIEND_HELP_DELAY = 2.4

BUILDING_DOOR_X = 430
BUILDING_DOOR_Y = 160
BUILDING_DOOR_WIDTH = 120
BUILDING_DOOR_HEIGHT = 130
BUILDING_INTERIOR_LEFT = 275
BUILDING_INTERIOR_RIGHT = 585
BUILDING_INTERIOR_BOTTOM = 120
BUILDING_INTERIOR_TOP = 475

MAX_MESSAGE_TIME = 2.4
UPGRADE_BASE_COST = 25

SKY_TOP = (29, 45, 70)
SKY_BOTTOM = (119, 177, 190)
STREET = (68, 74, 83)
SIDEWALK = (156, 160, 167)
BUILDING = (92, 84, 98)
BUILDING_DARK = (61, 56, 68)
BUILDING_EDGE = (39, 37, 48)
WINDOW_DARK = (35, 44, 60)
WINDOW_LIT = (255, 217, 116)
DIRT = (118, 93, 71)
TRASH_TAN = (182, 160, 115)
TRASH_BLUE = (96, 145, 174)
TRASH_RED = (203, 94, 86)
TRASH_GREEN = (102, 164, 112)
TEXT_MAIN = (242, 244, 247)
TEXT_MUTED = (207, 214, 222)
ACCENT = (247, 181, 82)
SUCCESS = (107, 212, 128)
FAIL = (233, 104, 104)


@dataclass
class BuildingStage:
    name: str
    description: str
    quest_seconds: float
    trash_count: int
    reward_money: int
    friend_reward: int
    facade_shift: int


@dataclass
class TrashItem:
    x: float
    y: float
    kind: str
    radius: float = 18
    collected: bool = False
    pulse: float = 0.0

    def contains(self, mx: float, my: float) -> bool:
        return math.dist((mx, my), (self.x, self.y)) <= self.radius + CLICK_RADIUS / 3

    def draw(self) -> None:
        if self.collected:
            return

        if self.kind == "bag":
            arcade.draw_ellipse_filled(self.x, self.y, 28, 20, TRASH_TAN)
            arcade.draw_line(self.x - 10, self.y + 8, self.x + 8, self.y + 10, BUILDING_EDGE, 2)
            arcade.draw_triangle_filled(self.x - 4, self.y + 11, self.x + 4, self.y + 11, self.x, self.y + 18, BUILDING_EDGE)
        elif self.kind == "box":
            arcade.draw_rectangle_filled(self.x, self.y, 28, 18, TRASH_BLUE)
            arcade.draw_line(self.x - 12, self.y - 9, self.x + 12, self.y + 9, BUILDING_EDGE, 2)
            arcade.draw_line(self.x - 12, self.y + 9, self.x + 12, self.y - 9, BUILDING_EDGE, 2)
        elif self.kind == "chair":
            arcade.draw_line(self.x - 10, self.y - 10, self.x - 10, self.y + 10, TRASH_RED, 4)
            arcade.draw_line(self.x + 10, self.y - 10, self.x + 10, self.y + 10, TRASH_RED, 4)
            arcade.draw_line(self.x - 12, self.y + 2, self.x + 12, self.y + 2, TRASH_RED, 4)
            arcade.draw_line(self.x - 10, self.y - 10, self.x + 10, self.y - 10, TRASH_RED, 4)
        else:
            arcade.draw_circle_filled(self.x, self.y, 12, TRASH_GREEN)
            arcade.draw_line(self.x - 8, self.y, self.x + 8, self.y, BUILDING_EDGE, 2)

        if self.pulse > 0:
            arcade.draw_circle_outline(self.x, self.y, 18 + 8 * self.pulse, SUCCESS, 2)


@dataclass
class FriendNPC:
    name: str
    x: float
    y: float
    color: tuple[int, int, int]
    phase: float
    base_x: float
    base_y: float
    help_timer: float = 0.0
    help_used: bool = False

    def update(self, delta_time: float) -> None:
        self.phase += delta_time
        self.help_timer += delta_time
        self.x = self.base_x + math.sin(self.phase * 1.1) * 16
        self.y = self.base_y + math.cos(self.phase * 0.9) * 6

    def draw(self) -> None:
        arcade.draw_circle_filled(self.x, self.y + 18, 10, (244, 221, 187))
        arcade.draw_rectangle_filled(self.x, self.y, 18, 24, self.color)
        arcade.draw_line(self.x - 4, self.y - 12, self.x - 7, self.y - 26, BUILDING_EDGE, 3)
        arcade.draw_line(self.x + 4, self.y - 12, self.x + 7, self.y - 26, BUILDING_EDGE, 3)
        arcade.draw_line(self.x - 9, self.y + 2, self.x - 18, self.y - 3, BUILDING_EDGE, 3)
        arcade.draw_line(self.x + 9, self.y + 2, self.x + 18, self.y - 3, BUILDING_EDGE, 3)


@dataclass
class Button:
    label: str
    left: float
    right: float
    bottom: float
    top: float
    enabled: bool = True

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def draw(self) -> None:
        fill = (59, 76, 95) if self.enabled else (42, 48, 57)
        border = ACCENT if self.enabled else (110, 118, 128)
        arcade.draw_rectangle_filled((self.left + self.right) / 2, (self.bottom + self.top) / 2, self.right - self.left, self.top - self.bottom, fill)
        arcade.draw_rectangle_outline((self.left + self.right) / 2, (self.bottom + self.top) / 2, self.right - self.left, self.top - self.bottom, border, 2)
        arcade.draw_text(
            self.label,
            (self.left + self.right) / 2,
            (self.bottom + self.top) / 2 - 9,
            TEXT_MAIN if self.enabled else TEXT_MUTED,
            16,
            anchor_x="center",
        )


class CommunityMvpGame(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.stages = [
            BuildingStage("Corner Laundromat", "Clear the abandoned laundromat before time runs out.", 12.0, 7, 20, 1, 0),
            BuildingStage("Apartment Block", "Clean the empty apartments and make the block feel lived in.", 11.0, 9, 25, 1, 18),
            BuildingStage("Community House", "Finish the last building and make it a place people want to stay.", 10.0, 10, 30, 1, 36),
        ]

        self.player_x = 150.0
        self.player_y = 180.0
        self.keys_down: set[int] = set()

        self.current_stage_index = 0
        self.quest_active = False
        self.quest_complete = False
        self.quest_failed = False
        self.timer_left = self.stages[0].quest_seconds
        self.cleaned = 0
        self.money = 0
        self.friendship = 0
        self.upgrade_level = 0
        self.total_cleaned = 0
        self.completed_buildings = 0
        self.message = "You feel alone in a quiet block. Start a quest to bring people back."
        self.message_timer = 2.0
        self.game_won = False
        self.inside_building = False
        self.mouse_x = 0.0
        self.mouse_y = 0.0

        self.trash_items: list[TrashItem] = []
        self.friends: list[FriendNPC] = []
        self.sparkles: list[TrashItem] = []

        self.start_button = Button("Start Quest", 960, 1220, 590, 640)
        self.upgrade_button = Button("Upgrade", 960, 1220, 520, 570)
        self.next_button = Button("Next Building", 960, 1220, 450, 500, enabled=False)
        self.restart_button = Button("Restart", 960, 1220, 380, 430)

        self.reset_stage(first_time=True)

    @property
    def stage(self) -> BuildingStage:
        return self.stages[self.current_stage_index]

    def refresh_ui_state(self) -> None:
        self.start_button.enabled = not self.quest_active and not self.quest_complete and not self.game_won
        self.upgrade_button.enabled = not self.quest_active and not self.game_won
        self.next_button.enabled = self.quest_complete and self.current_stage_index < len(self.stages) - 1 and not self.game_won
        self.restart_button.enabled = True

    def set_idle_message(self) -> None:
        if self.game_won:
            self.message = "Your home is ready."
        elif self.quest_complete and self.current_stage_index < len(self.stages) - 1:
            self.message = "Quest complete. Click Next Building to keep the community growing."
        elif self.quest_complete:
            self.message = "Quest complete. You built enough trust to get your own home."
        else:
            self.message = "You feel alone in a quiet block. Start a quest to bring people back."
        self.quest_failed = False

    def reset_friend_help(self) -> None:
        for friend in self.friends:
            friend.help_timer = 0.0
            friend.help_used = False

    def try_friend_help(self, friend: FriendNPC) -> None:
        if not self.quest_active or friend.help_used or friend.help_timer < FRIEND_HELP_DELAY + self.current_stage_index * 0.35:
            return

        target_item: TrashItem | None = None
        target_distance = 0.0
        for item in self.trash_items:
            if item.collected:
                continue

            distance = math.dist((friend.x, friend.y), (item.x, item.y))
            if distance <= FRIEND_HELP_RANGE and (target_item is None or distance < target_distance):
                target_item = item
                target_distance = distance

        if target_item is None:
            return

        target_item.collected = True
        target_item.pulse = 1.0
        friend.help_used = True
        self.cleaned += 1
        self.money += 2 + self.upgrade_level
        self.message = f"{friend.name} helped clear some trash."
        self.message_timer = 1.0

        if self.cleaned >= self.stage.trash_count:
            self.quest_complete_action()

    def reset_stage(self, first_time: bool = False) -> None:
        stage = self.stage
        rng = random.Random(100 + self.current_stage_index * 19)

        self.timer_left = stage.quest_seconds + self.upgrade_level * 0.75
        self.cleaned = 0
        self.quest_active = False
        self.quest_complete = False
        self.quest_failed = False
        self.inside_building = False
        self.set_idle_message()
        self.message_timer = 2.0

        self.trash_items = []
        kinds = ["bag", "box", "chair", "can"]
        for index in range(stage.trash_count):
            if index < 3:
                x = rng.uniform(110, 680)
                y = rng.uniform(140, 560)
            elif index < stage.trash_count - 2:
                x = rng.uniform(170, 740)
                y = rng.uniform(130, 470)
            else:
                x = rng.uniform(120, 820)
                y = rng.uniform(110, 200)
            self.trash_items.append(
                TrashItem(
                    x=x,
                    y=y,
                    kind=rng.choice(kinds),
                    radius=rng.uniform(14, 20),
                )
            )

        if first_time:
            self.player_x = 150.0
            self.player_y = 180.0
            self.friends = []
        else:
            self.reset_friend_help()

        self.refresh_ui_state()

    def start_quest(self) -> None:
        if self.game_won:
            return

        if self.quest_active:
            self.message = "The quest is already running."
            self.message_timer = MAX_MESSAGE_TIME
            return

        if self.quest_complete:
            self.message = "This building is already finished. Click Next Building."
            self.message_timer = MAX_MESSAGE_TIME
            return

        self.reset_stage()
        self.quest_active = True
        self.quest_complete = False
        self.quest_failed = False
        self.timer_left = self.stage.quest_seconds + self.upgrade_level * 0.75
        self.message = f"Quest started: {self.stage.description}"
        self.message_timer = MAX_MESSAGE_TIME
        self.refresh_ui_state()

    def quest_complete_action(self) -> None:
        self.quest_active = False
        self.quest_complete = True
        self.quest_failed = False
        self.completed_buildings += 1
        self.total_cleaned += self.stage.trash_count
        self.money += self.stage.reward_money + self.stage.trash_count * 2 + self.upgrade_level
        self.friendship += self.stage.friend_reward

        friend_palette = [
            ("Mia", (165, 115, 214)),
            ("Jay", (81, 169, 214)),
            ("Noah", (224, 128, 97)),
            ("Zoe", (92, 184, 132)),
        ]
        friend_name, color = friend_palette[self.current_stage_index % len(friend_palette)]
        self.friends.append(
            FriendNPC(
                name=friend_name,
                x=220 + len(self.friends) * 70,
                y=120 + len(self.friends) * 18,
                color=color,
                phase=0.0,
                base_x=220 + len(self.friends) * 70,
                base_y=120 + len(self.friends) * 18,
            )
        )

        self.message = f"Quest complete: {friend_name} joins the community at {self.stage.name}."
        self.message_timer = 3.0
        self.refresh_ui_state()

        if self.current_stage_index == len(self.stages) - 1 and self.money >= 75 and self.friendship >= 3:
            self.game_won = True
            self.message = "You built enough trust and money to get your own home."
            self.message_timer = 4.5
            self.refresh_ui_state()

    def fail_quest(self) -> None:
        self.quest_active = False
        self.quest_failed = True
        self.message = "Quest failed. Start again to reset the building."
        self.message_timer = 3.0
        self.refresh_ui_state()

    def next_building(self) -> None:
        if not self.quest_complete or self.current_stage_index >= len(self.stages) - 1:
            return

        self.current_stage_index += 1
        self.reset_stage()
        self.message = f"New building unlocked: {self.stage.name}"
        self.message_timer = 2.8
        self.refresh_ui_state()

    def upgrade_house(self) -> None:
        if self.quest_active:
            self.message = "Finish the quest before upgrading."
            self.message_timer = MAX_MESSAGE_TIME
            return

        cost = UPGRADE_BASE_COST + self.upgrade_level * 15
        if self.money < cost:
            self.message = f"Need ${cost} for the next upgrade."
            self.message_timer = MAX_MESSAGE_TIME
            return

        self.money -= cost
        self.upgrade_level += 1
        self.message = "Upgrade bought: more time and better earnings."
        self.message_timer = 2.8
        self.timer_left = self.stage.quest_seconds + self.upgrade_level * 0.75
        self.refresh_ui_state()

    def restart_game(self) -> None:
        self.current_stage_index = 0
        self.money = 0
        self.friendship = 0
        self.upgrade_level = 0
        self.total_cleaned = 0
        self.completed_buildings = 0
        self.game_won = False
        self.inside_building = False
        self.keys_down.clear()
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.reset_stage(first_time=True)

    def at_building_door(self) -> bool:
        return math.dist((self.player_x, self.player_y), (BUILDING_DOOR_X, BUILDING_DOOR_Y)) <= 70

    def toggle_building_entry(self) -> None:
        if not self.at_building_door():
            self.message = "Get close to the door first."
            self.message_timer = 1.2
            return

        self.inside_building = not self.inside_building
        if self.inside_building:
            self.message = "You step inside the building."
        else:
            self.message = "You step back outside."
        self.message_timer = 1.2

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key in (arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D, arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.keys_down.add(key)
        elif key == arcade.key.SPACE:
            self.start_quest()
        elif key == arcade.key.E:
            self.toggle_building_entry()
        elif key == arcade.key.ESCAPE and self.inside_building:
            self.inside_building = False
            self.message = "You head back outside."
            self.message_timer = 1.0
        elif key == arcade.key.R:
            self.restart_game()

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_down.discard(key)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.start_button.contains(x, y) and self.start_button.enabled:
            self.start_quest()
            return
        if self.upgrade_button.contains(x, y) and self.upgrade_button.enabled:
            self.upgrade_house()
            return
        if self.next_button.contains(x, y) and self.next_button.enabled:
            self.next_building()
            return
        if self.restart_button.contains(x, y) and self.restart_button.enabled:
            self.restart_game()
            return

        if self.at_building_door():
            self.toggle_building_entry()
            return

        if not self.quest_active or self.game_won:
            return

        for item in self.trash_items:
            if item.collected:
                continue
            if item.contains(x, y) and math.dist((self.player_x, self.player_y), (item.x, item.y)) <= COLLECT_RANGE:
                item.collected = True
                item.pulse = 1.0
                self.cleaned += 1
                self.money += 2 + self.upgrade_level
                self.message = "Trash collected."
                self.message_timer = 0.8
                if self.cleaned >= self.stage.trash_count:
                    self.quest_complete_action()
                return

        self.message = "Move closer to clean that up."
        self.message_timer = 1.2

    def on_update(self, delta_time: float) -> None:
        if self.game_won:
            return

        move_x = 0
        move_y = 0
        if arcade.key.A in self.keys_down or arcade.key.LEFT in self.keys_down:
            move_x -= 1
        if arcade.key.D in self.keys_down or arcade.key.RIGHT in self.keys_down:
            move_x += 1
        if arcade.key.W in self.keys_down or arcade.key.UP in self.keys_down:
            move_y += 1
        if arcade.key.S in self.keys_down or arcade.key.DOWN in self.keys_down:
            move_y -= 1

        self.player_x += move_x * PLAYER_SPEED * delta_time
        self.player_y += move_y * PLAYER_SPEED * delta_time
        if self.inside_building:
            self.player_x = max(BUILDING_INTERIOR_LEFT, min(BUILDING_INTERIOR_RIGHT, self.player_x))
            self.player_y = max(BUILDING_INTERIOR_BOTTOM, min(BUILDING_INTERIOR_TOP, self.player_y))
        else:
            self.player_x = max(70, min(850, self.player_x))
            self.player_y = max(90, min(590, self.player_y))

        if self.quest_active:
            self.timer_left -= delta_time
            if self.timer_left <= 0:
                self.timer_left = 0
                self.fail_quest()

        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0 and not self.quest_active and not self.game_won:
                self.set_idle_message()

        for item in self.trash_items:
            if item.pulse > 0:
                item.pulse = max(0.0, item.pulse - delta_time * 3.0)

        for friend in list(self.friends):
            friend.update(delta_time)
            self.try_friend_help(friend)

        self.refresh_ui_state()

    def draw_background(self) -> None:
        band_height = 32
        for y in range(0, SCREEN_HEIGHT, band_height):
            mix = y / SCREEN_HEIGHT
            color = tuple(
                int(SKY_TOP[i] * (1 - mix) + SKY_BOTTOM[i] * mix)
                for i in range(3)
            )
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, y + band_height / 2, SCREEN_WIDTH, band_height, color)

        for star_x, star_y in ((70, 620), (160, 575), (290, 640), (820, 605), (770, 545)):
            arcade.draw_circle_filled(star_x, star_y, 2, (245, 246, 250))

        arcade.draw_rectangle_filled(450, 50, 900, 100, STREET)
        arcade.draw_rectangle_filled(450, 96, 900, 12, SIDEWALK)
        arcade.draw_rectangle_filled(450, 690, 900, 60, (34, 38, 48))

    def draw_building(self) -> None:
        if self.inside_building:
            arcade.draw_rectangle_filled(430, 290, 520, 340, (52, 46, 58))
            arcade.draw_rectangle_filled(430, 200, 520, 160, (72, 63, 53))
            arcade.draw_rectangle_filled(430, 430, 520, 40, (34, 29, 39))
            arcade.draw_rectangle_filled(250, 290, 80, 260, (64, 58, 70))
            arcade.draw_rectangle_filled(610, 290, 80, 260, (64, 58, 70))
            arcade.draw_rectangle_filled(430, 160, 130, 60, (44, 38, 48))
            arcade.draw_rectangle_outline(430, 290, 520, 340, BUILDING_EDGE, 4)
            arcade.draw_rectangle_outline(430, 160, 130, 60, ACCENT, 2)
            arcade.draw_text("Inside the building", 430, 444, TEXT_MAIN, 18, anchor_x="center")
            arcade.draw_text("Press E or Esc to leave", 430, 418, TEXT_MUTED, 12, anchor_x="center")
            arcade.draw_line(320, 260, 540, 260, (96, 83, 70), 4)
            arcade.draw_line(320, 220, 540, 220, (96, 83, 70), 4)
            arcade.draw_circle_filled(390, 305, 18, (168, 142, 112))
            arcade.draw_circle_filled(470, 295, 16, (126, 169, 116))
            arcade.draw_rectangle_filled(430, 170, 42, 78, (87, 63, 49))
            arcade.draw_rectangle_outline(430, 170, 42, 78, BUILDING_EDGE, 2)
            return

        stage = self.stage
        dirt_amount = 0.2 if not self.quest_active and not self.quest_complete else max(0.0, 1.0 - self.cleaned / max(1, stage.trash_count))
        facade_color = tuple(
            int(BUILDING[i] * (1 - 0.18 * dirt_amount) + (158 if i == 0 else 149 if i == 1 else 164) * 0.15)
            for i in range(3)
        )

        arcade.draw_rectangle_filled(430, 315, 520, 420, facade_color)
        arcade.draw_rectangle_filled(430, 315, 534, 432, BUILDING_DARK)
        arcade.draw_rectangle_outline(430, 315, 520, 420, BUILDING_EDGE, 4)

        # Windows and grime
        for row, y in enumerate((430, 360, 290)):
            for col, x in enumerate((250, 350, 450, 550, 650)):
                lit = self.quest_complete or (self.quest_active and self.cleaned > (row + col) % max(1, stage.trash_count // 3))
                color = WINDOW_LIT if lit else WINDOW_DARK
                arcade.draw_rectangle_filled(x, y, 50, 54, color)
                arcade.draw_rectangle_outline(x, y, 50, 54, BUILDING_EDGE, 2)
                arcade.draw_line(x, y - 27, x, y + 27, BUILDING_EDGE, 2)
                arcade.draw_line(x - 25, y, x + 25, y, BUILDING_EDGE, 2)

        # Broken boards that vanish after cleaning.
        if not self.quest_complete:
            for x, y in ((250, 430), (650, 360), (350, 290)):
                arcade.draw_line(x - 20, y - 16, x + 20, y + 16, DIRT, 5)
                arcade.draw_line(x - 20, y + 16, x + 20, y - 16, DIRT, 5)

        # Community glow on later stages.
        if self.current_stage_index > 0 or self.quest_complete:
            arcade.draw_rectangle_filled(700, 180, 80, 90, (232, 190, 122))
            arcade.draw_triangle_filled(670, 135, 730, 135, 700, 95, (241, 222, 134))

        if self.upgrade_level > 0:
            light_colors = [ACCENT, SUCCESS, (110, 169, 214), (244, 221, 187)]
            roof_y = 525
            arcade.draw_line(220, roof_y, 650, roof_y, (92, 76, 58), 3)
            for index, x in enumerate((235, 310, 385, 460, 535, 610)):
                if index >= min(6, 2 + self.upgrade_level):
                    break
                color = light_colors[(index + self.upgrade_level) % len(light_colors)]
                arcade.draw_circle_filled(x, roof_y - (index % 2) * 5, 5 + min(self.upgrade_level, 3), color)

            if self.upgrade_level >= 1:
                for x, y in ((220, 205), (640, 205)):
                    arcade.draw_rectangle_filled(x, y, 26, 12, (82, 123, 86))
                    arcade.draw_circle_filled(x, y + 10, 8, (126, 181, 108))
            if self.upgrade_level >= 2:
                arcade.draw_rectangle_filled(430, 210, 72, 16, (78, 61, 48))
                arcade.draw_rectangle_filled(430, 223, 24, 8, ACCENT)
            if self.upgrade_level >= 3:
                arcade.draw_rectangle_filled(545, 233, 30, 10, (92, 132, 89))
                arcade.draw_circle_filled(545, 244, 10, (127, 188, 117))

        # Side entrance
        arcade.draw_rectangle_filled(430, 160, 76, 110, (52, 44, 58))
        arcade.draw_rectangle_outline(430, 160, 76, 110, BUILDING_EDGE, 2)
        arcade.draw_text("Door: press E to enter", 430, 102, TEXT_MUTED, 12, anchor_x="center")

    def draw_trash(self) -> None:
        for item in self.trash_items:
            item.draw()

    def draw_friends(self) -> None:
        for friend in self.friends:
            friend.draw()
            arcade.draw_text(friend.name, friend.x, friend.y + 44, TEXT_MAIN, 12, anchor_x="center")

    def draw_player(self) -> None:
        arcade.draw_circle_filled(self.player_x, self.player_y + 16, 10, (248, 222, 188))
        arcade.draw_circle_filled(self.player_x - 4, self.player_y + 17, 2, BUILDING_EDGE)
        arcade.draw_circle_filled(self.player_x + 4, self.player_y + 17, 2, BUILDING_EDGE)
        arcade.draw_rectangle_filled(self.player_x, self.player_y, 24, 28, (246, 102, 86))
        arcade.draw_line(self.player_x - 6, self.player_y - 12, self.player_x - 10, self.player_y - 28, BUILDING_EDGE, 3)
        arcade.draw_line(self.player_x + 6, self.player_y - 12, self.player_x + 10, self.player_y - 28, BUILDING_EDGE, 3)
        arcade.draw_line(self.player_x - 10, self.player_y + 2, self.player_x - 20, self.player_y - 2, BUILDING_EDGE, 3)
        arcade.draw_line(self.player_x + 10, self.player_y + 2, self.player_x + 20, self.player_y - 2, BUILDING_EDGE, 3)
        arcade.draw_text("You", self.player_x, self.player_y + 46, TEXT_MAIN, 12, anchor_x="center")

    def draw_sidebar(self) -> None:
        self.refresh_ui_state()
        arcade.draw_rectangle_filled(1090, 360, 340, 720, (34, 40, 53))
        arcade.draw_rectangle_filled(1090, 360, 300, 664, (45, 52, 67))
        arcade.draw_text("Community MVP", 1090, 672, TEXT_MAIN, 24, anchor_x="center")

        arcade.draw_text(f"Building: {self.stage.name}", 960, 630, TEXT_MAIN, 16)
        arcade.draw_text(f"Objective: {self.stage.description}", 960, 602, TEXT_MUTED, 13, width=280, multiline=True)

        total_time = self.stage.quest_seconds + self.upgrade_level * 0.75
        time_ratio = 0 if total_time <= 0 else self.timer_left / total_time
        time_ratio = max(0.0, min(1.0, time_ratio))
        arcade.draw_text("Quest Timer", 960, 560, TEXT_MAIN, 13)
        arcade.draw_rectangle_filled(1090, 548, 260, 16, (52, 58, 73))
        arcade.draw_rectangle_filled(960 + 130 * time_ratio, 548, 260 * time_ratio, 16, SUCCESS if time_ratio > 0.3 else FAIL)
        arcade.draw_text(f"{self.timer_left:0.1f}s", 1225, 543, TEXT_MAIN, 12, anchor_x="right")

        progress_ratio = 0 if self.stage.trash_count <= 0 else self.cleaned / self.stage.trash_count
        arcade.draw_text("Trash Cleaned", 960, 512, TEXT_MAIN, 13)
        arcade.draw_rectangle_filled(1090, 500, 260, 16, (52, 58, 73))
        arcade.draw_rectangle_filled(960 + 130 * progress_ratio, 500, 260 * progress_ratio, 16, ACCENT)
        arcade.draw_text(f"{self.cleaned}/{self.stage.trash_count}", 1225, 495, TEXT_MAIN, 12, anchor_x="right")

        friendship_ratio = max(0.0, min(1.0, self.friendship / 3))
        arcade.draw_text("Friendship", 960, 464, TEXT_MAIN, 13)
        arcade.draw_rectangle_filled(1090, 452, 260, 16, (52, 58, 73))
        arcade.draw_rectangle_filled(960 + 130 * friendship_ratio, 452, 260 * friendship_ratio, 16, (116, 199, 154))
        arcade.draw_text(f"{self.friendship}/3", 1225, 447, TEXT_MAIN, 12, anchor_x="right")

        arcade.draw_text(f"Money: ${self.money}", 960, 416, TEXT_MAIN, 16)
        arcade.draw_text(f"Upgrade level: {self.upgrade_level}", 960, 392, TEXT_MUTED, 13)
        arcade.draw_text(f"Buildings finished: {self.completed_buildings}/{len(self.stages)}", 960, 368, TEXT_MUTED, 13)

        self.start_button.draw()
        self.upgrade_button.draw()
        self.next_button.draw()
        self.restart_button.draw()

        cost = UPGRADE_BASE_COST + self.upgrade_level * 15
        arcade.draw_text(f"Cost: ${cost}", 1230, 527, TEXT_MUTED, 12, anchor_x="right")
        arcade.draw_text("Press Space to start the quest.", 960, 336, TEXT_MUTED, 12)
        arcade.draw_text("Click trash only while the quest is running.", 960, 316, TEXT_MUTED, 12)
        arcade.draw_text("Press R to restart the whole game.", 960, 296, TEXT_MUTED, 12)
        arcade.draw_text("Walk to the door and press E to enter the building.", 960, 276, TEXT_MUTED, 12, width=280, multiline=True)
        if self.inside_building:
            arcade.draw_text("You are inside right now.", 960, 258, SUCCESS, 12)

        if self.message:
            lowered = self.message.lower()
            color = SUCCESS if any(keyword in lowered for keyword in ("complete", "unlocked", "upgrade", "helped", "ready")) else FAIL if "failed" in lowered else TEXT_MAIN
            arcade.draw_text(self.message, 960, 250, color, 14, width=280, multiline=True)

        if self.game_won:
            arcade.draw_rectangle_filled(1090, 135, 320, 180, (16, 20, 30, 210))
            arcade.draw_text("Your home is ready.", 1090, 178, TEXT_MAIN, 24, anchor_x="center")
            arcade.draw_text("The buildings changed because people helped each other.", 1090, 138, TEXT_MUTED, 12, anchor_x="center", width=250, multiline=True)

    def on_draw(self) -> None:
        self.clear()
        self.draw_background()
        self.draw_building()
        self.draw_trash()
        self.draw_friends()
        self.draw_player()
        self.draw_sidebar()

        if self.game_won:
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, (10, 14, 22, 120))
            arcade.draw_text("You earned your own home.", SCREEN_WIDTH / 2, 600, TEXT_MAIN, 28, anchor_x="center")
            arcade.draw_text("Clean the buildings, make friends, and build a place to stay.", SCREEN_WIDTH / 2, 560, TEXT_MUTED, 16, anchor_x="center")


def main() -> None:
    window = CommunityMvpGame()
    arcade.run()


if __name__ == "__main__":
    runpy.run_path(Path(__file__).with_name("game-ethan.py"), run_name="__main__")
