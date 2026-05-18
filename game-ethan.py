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
BALL_SPEED = 220
BALL_RADIUS = 16
COLLECT_DISTANCE = 70
FRIEND_DISTANCE = 65
ENTRANCE_X = 720
ENTRANCE_Y = 300
ENTRANCE_WIDTH = 55
ENTRANCE_HEIGHT = 120
QUIZ_OPTIONS = [
    {
        "question": "What is one helpful way an abandoned home could be used?",
        "answers": [
            "Turn it into safe housing or a youth center",
            "Leave it empty so nobody notices it",
            "Break more windows so it looks scary",
        ],
        "correct": 0,
        "fact": "Empty homes can become safe housing, community rooms, gardens, or youth spaces when people repair them together.",
    },
    {
        "question": "What can help teens who feel lonely?",
        "answers": [
            "A trusted friend, mentor, club, or safe place to meet",
            "Being ignored until they stop talking",
            "More empty places with nobody around",
        ],
        "correct": 0,
        "fact": "Connection matters. Friends, mentors, teams, clubs, and safe community spaces can help teens feel less alone.",
    },
]


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
        self.friend_hints = 0
        self.cleaned = 0
        self.upgrades = 0
        self.message = "Press SPACE to begin."
        self.hint = "Clear every trash pile to move to the next building."
        self.trash_spots: list[TrashSpot] = []
        self.repair_spots: list[RepairSpot] = []
        self.friends: list[FriendNPC] = []
        self.befriended_friends: set[str] = set()
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0
        self.neighborhood_state = 0
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.keys_down: set[int] = set()
        self.quiz_friend: FriendNPC | None = None
        self.quiz_question = QUIZ_OPTIONS[0]
        self.game_over_ready = False
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
        self.hint = "Move the ball close to trash with WASD or arrows, then click to pick it up."
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
        for i in range(3):
            fx, fy = friend_positions[i]
            self.friends.append(FriendNPC(friend_names[i], fx, fy))

        self.ball_x = 400.0
        self.ball_y = 155.0
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
        self.ball_x = 400.0
        self.ball_y = 155.0
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

    def start_friend_quiz(self, friend: FriendNPC) -> None:
        self.quiz_friend = friend
        self.quiz_question = QUIZ_OPTIONS[(self.cleaned + self.friendship) % len(QUIZ_OPTIONS)]
        self.screen = "quiz"
        self.message = f"{friend.name} asks a question before becoming your friend."
        self.hint = "Click the answer you think is best."

    def answer_quiz(self, answer_index: int) -> None:
        if self.quiz_friend is None:
            return

        if answer_index == self.quiz_question["correct"]:
            self.friend_hints -= 1
            self.friendship += 1
            self.befriended_friends.add(self.quiz_friend.name)
            self.message = f"Correct. {self.quiz_friend.name} became your friend."
            self.hint = self.quiz_question["fact"]
            self.quiz_friend = None
            self.screen = "playing"
            return

        self.start_dark_game_over()

    def start_dark_game_over(self) -> None:
        self.screen = "dark"
        self.game_over_ready = False
        self.keys_down.clear()
        self.ball_x = 90.0
        self.ball_y = 300.0
        self.message = "Wrong answer. Find the white entrance before the light fades."
        self.hint = self.quiz_question["fact"]

    def reached_entrance(self) -> bool:
        return (
            ENTRANCE_X - ENTRANCE_WIDTH / 2 <= self.ball_x <= ENTRANCE_X + ENTRANCE_WIDTH / 2
            and ENTRANCE_Y - ENTRANCE_HEIGHT / 2 <= self.ball_y <= ENTRANCE_Y + ENTRANCE_HEIGHT / 2
        )

    def try_befriend(self, x: float | None = None, y: float | None = None) -> bool:
        if self.screen != "playing":
            return False

        for friend in self.friends:
            if friend.name in self.befriended_friends:
                continue

            clicked_friend = x is not None and y is not None and (x - friend.x) ** 2 + (y - friend.y) ** 2 <= 24 ** 2
            near_ball = (self.ball_x - friend.x) ** 2 + (self.ball_y - friend.y) ** 2 <= FRIEND_DISTANCE ** 2

            if clicked_friend or (x is None and near_ball):
                if not near_ball:
                    self.message = f"Move closer to {friend.name} first."
                    self.hint = "Friend balls can only hear you when your ball is nearby."
                    return True
                if self.friend_hints <= 0:
                    self.message = f"{friend.name} needs a hint from the cleanup first."
                    self.hint = "Pick up trash to earn friend hints, then come back."
                    return True

                self.start_friend_quiz(friend)
                return True

        if x is None and y is None:
            self.message = "Move close to a blue ball before pressing F."
            self.hint = "Pick up trash for hints, then use those hints near other balls."
            return True

        return False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            if self.window is not None:
                self.window.close()
            return

        if key in (
            arcade.key.W,
            arcade.key.A,
            arcade.key.S,
            arcade.key.D,
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.LEFT,
            arcade.key.RIGHT,
        ):
            self.keys_down.add(key)
            return

        if key == arcade.key.E and self.screen == "playing" and not self.trash_spots:
            self.enter_house()
            return

        if key == arcade.key.F:
            self.try_befriend()
            return

        if self.screen == "quiz" and key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
            self.answer_quiz({arcade.key.KEY_1: 0, arcade.key.KEY_2: 1, arcade.key.KEY_3: 2}[key])
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

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_down.discard(key)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.camera is not None:
            world_position = self.camera.unproject((x, y))
            x = world_position.x
            y = world_position.y

        if self.screen == "quiz":
            for index in range(3):
                top = 300 - index * 62
                bottom = top - 46
                if 130 <= x <= 670 and bottom <= y <= top:
                    self.answer_quiz(index)
                    return
            return

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

        if self.try_befriend(x, y):
            return

        for trash in list(self.trash_spots):
            if (x - trash.x) ** 2 + (y - trash.y) ** 2 <= trash.radius ** 2:
                if (self.ball_x - trash.x) ** 2 + (self.ball_y - trash.y) ** 2 > COLLECT_DISTANCE ** 2:
                    self.message = "Move the ball closer to pick that up."
                    self.hint = "Use WASD or arrow keys to get near the trash, then click it."
                    return

                self.trash_spots.remove(trash)
                self.cleaned += 1
                self.money += TRASH_SCORE + self.upgrades
                self.friend_hints += 1
                self.message = f"You found a friend hint in the cleanup. Hints: {self.friend_hints}."
                self.hint = "Move near another ball and press F or click them to become friends."
                if self.cleaned % 2 == 0:
                    self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
                break

        if not self.trash_spots:
            self.enter_house()

    def draw_ball(self) -> None:
        if self.screen == "playing":
            arcade.draw_circle_outline(self.ball_x, self.ball_y, COLLECT_DISTANCE, arcade.color.LIGHT_GRAY, 1)
        arcade.draw_circle_filled(self.ball_x + 4, self.ball_y - 5, BALL_RADIUS, (15, 18, 25, 120))
        arcade.draw_circle_filled(self.ball_x, self.ball_y, BALL_RADIUS, arcade.color.GOLD)
        arcade.draw_circle_outline(self.ball_x, self.ball_y, BALL_RADIUS, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(self.ball_x - 5, self.ball_y + 5, 5, arcade.color.WHITE)

    def update_ball(self, delta_time: float) -> None:
        if self.screen not in {"playing", "repair", "dark"}:
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

        if move_x and move_y:
            move_x *= 0.707
            move_y *= 0.707

        self.ball_x += move_x * BALL_SPEED * delta_time
        self.ball_y += move_y * BALL_SPEED * delta_time

        if self.screen == "repair":
            min_x, max_x = 90 + BALL_RADIUS, 710 - BALL_RADIUS
            min_y, max_y = 80 + BALL_RADIUS, 470 - BALL_RADIUS
        elif self.screen == "dark":
            min_x, max_x = BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS
            min_y, max_y = BALL_RADIUS, SCREEN_HEIGHT - BALL_RADIUS
        else:
            min_x, max_x = BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS
            min_y, max_y = 95 + BALL_RADIUS, 385 - BALL_RADIUS

        self.ball_x = max(min_x, min(max_x, self.ball_x))
        self.ball_y = max(min_y, min(max_y, self.ball_y))

    def on_update(self, delta_time: float) -> None:
        self.update_ball(delta_time)

        if self.screen == "dark" and self.reached_entrance():
            self.screen = "game_over"
            self.game_over_ready = True
            self.keys_down.clear()
            return

        if self.screen != "playing":
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.fail_round()

    def draw_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (18, 22, 32))
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 120, (31, 38, 36))
        arcade.draw_circle_filled(95, 525, 34, (132, 126, 108))
        arcade.draw_circle_filled(140, 535, 24, (112, 108, 98))
        arcade.draw_circle_filled(700, 525, 22, (76, 86, 102))
        arcade.draw_circle_filled(735, 545, 30, (92, 96, 104))
        arcade.draw_line(0, 120, 800, 120, (49, 58, 55), 2)

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
            ((73, 52, 48), (58, 62, 70)),
            ((62, 43, 55), (64, 68, 76)),
            ((61, 63, 49), (70, 72, 76)),
        ]
        building_heights = [220, 235, 195]
        building_positions = [(90, 320, 120), (350, 590, 115), (620, 770, 95)]

        for index, (left, right, base_y) in enumerate(building_positions):
            roof_color, wall_color = building_colors[index]
            height = building_heights[index]
            if index < self.neighborhood_state:
                wall_color = (76, 91, 86)
                roof_color = (54, 77, 69)
            self.draw_building(left, right, base_y, height, roof_color, wall_color)

        arcade.draw_lrbt_rectangle_filled(40, 760, 80, 105, (30, 32, 38))
        arcade.draw_line(0, 105, 800, 105, arcade.color.BLACK, 3)

        arcade.draw_text("bus stop", 675, 138, arcade.color.WHITE, 10)

        for trash in self.trash_spots:
            arcade.draw_circle_filled(trash.x, trash.y, trash.radius, arcade.color.BROWN_NOSE)
            arcade.draw_circle_outline(trash.x, trash.y, trash.radius, arcade.color.BLACK, 2)
            arcade.draw_text(trash.highlight, trash.x, trash.y - 5, arcade.color.WHITE, 8, anchor_x="center")

        for friend in self.friends:
            friend_color = (118, 139, 129) if friend.name in self.befriended_friends else (86, 104, 123)
            arcade.draw_circle_filled(friend.x, friend.y, 16, friend_color)
            arcade.draw_circle_outline(friend.x, friend.y, 16, arcade.color.BLACK, 2)
            arcade.draw_text(friend.name, friend.x, friend.y + 24, arcade.color.WHITE, 10, anchor_x="center")
            label = "friend" if friend.name in self.befriended_friends else "press F"
            arcade.draw_text(label, friend.x, friend.y - 34, arcade.color.LIGHT_GRAY, 8, anchor_x="center")

        self.draw_ball()

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

        self.draw_ball()

    def draw_quiz(self) -> None:
        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(90, 710, 130, 500, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(90, 710, 130, 500, arcade.color.WHITE, 3)
        arcade.draw_text("Community Question", 400, 460, arcade.color.GOLD, 24, anchor_x="center")
        arcade.draw_text(
            self.quiz_question["question"],
            130,
            405,
            arcade.color.WHITE,
            16,
            width=540,
            multiline=True,
        )

        for index, answer in enumerate(self.quiz_question["answers"]):
            top = 300 - index * 62
            bottom = top - 46
            arcade.draw_lrbt_rectangle_filled(130, 670, bottom, top, (44, 58, 72))
            arcade.draw_lrbt_rectangle_outline(130, 670, bottom, top, arcade.color.LIGHT_GRAY, 2)
            arcade.draw_text(f"{index + 1}. {answer}", 150, bottom + 15, arcade.color.WHITE, 13, width=500)

        arcade.draw_text("Pick carefully. A wrong answer changes the game.", 400, 152, arcade.color.LIGHT_GRAY, 12, anchor_x="center")

    def draw_dark_challenge(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, arcade.color.BLACK)
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 105, (255, 218, 74, 70))
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 58, (255, 226, 91, 115))
        arcade.draw_lrbt_rectangle_filled(
            ENTRANCE_X - ENTRANCE_WIDTH / 2,
            ENTRANCE_X + ENTRANCE_WIDTH / 2,
            ENTRANCE_Y - ENTRANCE_HEIGHT / 2,
            ENTRANCE_Y + ENTRANCE_HEIGHT / 2,
            arcade.color.WHITE,
        )
        arcade.draw_text("ENTRANCE", ENTRANCE_X, ENTRANCE_Y - 75, arcade.color.WHITE, 12, anchor_x="center")
        self.draw_ball()
        arcade.draw_text("Find the white entrance.", 400, 548, arcade.color.WHITE, 22, anchor_x="center")
        arcade.draw_text("Wrong answers can make loneliness feel darker.", 400, 520, arcade.color.LIGHT_GRAY, 12, anchor_x="center")

    def draw_game_over(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, arcade.color.BLACK)
        arcade.draw_text("GAME OVER", 400, 330, arcade.color.GOLD, 64, anchor_x="center")
        arcade.draw_text("Press ESC to quit.", 400, 265, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text(self.quiz_question["fact"], 170, 215, arcade.color.LIGHT_GRAY, 13, width=460, multiline=True)

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(10, 790, 492, 590, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(10, 790, 492, 590, arcade.color.WHITE)

        arcade.draw_text("Neighborhood Cleanup", 22, 562, arcade.color.WHITE, 22)
        arcade.draw_text(f"Building: {self.building_names[self.current_building]}", 22, 538, arcade.color.LIGHT_GRAY, 12)
        arcade.draw_text(f"Trash: {self.cleaned}", 22, 516, arcade.color.WHITE, 12)
        arcade.draw_text(f"Money: ${self.money}", 125, 516, arcade.color.WHITE, 12)
        arcade.draw_text(f"Friendship: {self.friendship}", 240, 516, arcade.color.WHITE, 12)
        arcade.draw_text(f"Hints: {self.friend_hints}", 390, 516, arcade.color.WHITE, 12)
        arcade.draw_text(f"Upgrades: {self.upgrades}/{MAX_UPGRADES}", 500, 516, arcade.color.WHITE, 12)
        arcade.draw_text(f"Time: {self.time_left:0.1f}s", 650, 516, arcade.color.WHITE, 12)
        fixed_count = sum(1 for repair in self.repair_spots if repair.fixed)
        repair_total = len(self.repair_spots)
        if self.screen == "repair" and repair_total:
            arcade.draw_text(f"Repairs: {fixed_count}/{repair_total}", 260, 538, arcade.color.LIGHT_GRAY, 12)
        else:
            arcade.draw_text(
                f"Neighborhood level: {self.neighborhood_state + 1}/{BUILDING_STAGES}",
                260,
                538,
                arcade.color.LIGHT_GRAY,
                12,
            )

        bar_left = 22
        bar_right = 778
        bar_bottom = 500
        bar_top = 508
        arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, arcade.color.DARK_SLATE_GRAY)
        filled = bar_left + (bar_right - bar_left) * max(0, self.time_left) / QUEST_TIME
        arcade.draw_lrbt_rectangle_filled(bar_left, filled, bar_bottom, bar_top, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_outline(bar_left, bar_right, bar_bottom, bar_top, arcade.color.WHITE)

        arcade.draw_lrbt_rectangle_filled(95, 705, 18, 96, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(95, 705, 18, 96, arcade.color.WHITE)
        arcade.draw_text(self.message, 112, 75, arcade.color.AMAZON, 12, width=576, multiline=True)
        arcade.draw_text(self.hint, 112, 55, arcade.color.LIGHT_GRAY, 10, width=576, multiline=True)

        if self.screen == "title":
            arcade.draw_text(
                "Press SPACE to begin the first cleanup round.",
                400,
                35,
                arcade.color.WHITE,
                11,
                anchor_x="center",
            )
        elif self.screen == "complete":
            arcade.draw_text(
                "Press SPACE to move to the next building.",
                400,
                35,
                arcade.color.WHITE,
                11,
                anchor_x="center",
            )
        elif self.screen == "failed":
            arcade.draw_text(
                "Press SPACE to try again with a fresh round.",
                400,
                35,
                arcade.color.WHITE,
                11,
                anchor_x="center",
            )
        elif self.screen == "repair":
            arcade.draw_text(
                "Move with WASD or arrows. Click repair spots to fix this house.",
                400,
                35,
                arcade.color.WHITE,
                11,
                anchor_x="center",
            )
            arcade.draw_text(
                "When every repair is finished, the next building unlocks.",
                400,
                23,
                arcade.color.LIGHT_GRAY,
                9,
                anchor_x="center",
            )
        else:
            arcade.draw_text(
                "Move close to trash and click it. Press F near blue balls to make friends.",
                400,
                35,
                arcade.color.WHITE,
                11,
                anchor_x="center",
            )
            arcade.draw_text(
                "Clearing more trash unlocks more trust and brighter buildings.",
                400,
                23,
                arcade.color.LIGHT_GRAY,
                9,
                anchor_x="center",
            )
        arcade.draw_text("Press ESC to quit.", 400, 10, arcade.color.LIGHT_GRAY, 8, anchor_x="center")

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

        if self.screen == "quiz":
            self.draw_quiz()
            return

        if self.screen == "dark":
            self.draw_dark_challenge()
            return

        if self.screen == "game_over":
            self.draw_game_over()
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
