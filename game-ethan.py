"""Neighborhood Cleanup: a more detailed MVP for the serious game idea.

The player cleans abandoned buildings, meets friends, earns money, and unlocks
small upgrades that make the neighborhood feel more alive.
"""

from __future__ import annotations

import random
import math

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neighborhood Cleanup: South Block"

QUEST_TIME = 7.0
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
BUILDING_POSITIONS = [(90, 320, 120), (350, 590, 115), (620, 770, 95)]
QUIZ_OPTIONS = [
    {
        "question": "Which choice best explains why repairing an abandoned home can reduce loneliness?",
        "answers": [
            "It raises property values, which automatically fixes loneliness",
            "It creates a safe shared place where people can meet, help, and feel noticed",
            "It removes every hard feeling as soon as the building looks better",
        ],
        "correct": 1,
        "fact": "Empty homes can become safe housing, community rooms, gardens, or youth spaces when people repair them together.",
    },
    {
        "question": "A teen says they feel invisible in their neighborhood. What is the strongest first response?",
        "answers": [
            "Give quick advice before they explain what is happening",
            "Plan a big event without asking what they need",
            "Listen seriously, connect them with trusted people, and invite them into safe activities",
        ],
        "correct": 2,
        "fact": "Connection matters. Friends, mentors, teams, clubs, and safe community spaces can help teens feel less alone.",
    },
    {
        "question": "Why should a cleanup project include the people who live nearby?",
        "answers": [
            "It keeps the project from needing any rules or planning",
            "They understand what the block needs and feel more ownership when they help decide",
            "It makes the project cheaper because neighbors do all the work",
        ],
        "correct": 1,
        "fact": "Community repair works best when neighbors are included, respected, and trusted to shape the place they share.",
    },
]


class TrashSpot:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.radius = 18
        self.highlight = random.choice(["can", "bag", "box", "rubble"])


class RepairSpot:
    def __init__(self, x: float, y: float, label: str, color, cost: int) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        self.cost = cost
        self.radius = 24
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
        self.screen = "intro"
        self.time_left = QUEST_TIME
        self.money = 0
        self.friendship = 0
        self.friend_hints = 0
        self.friend_name_hints: dict[str, int] = {}
        self.cleaned = 0
        self.upgrades = 0
        self.message = "Press SPACE to begin."
        self.hint = "Clear every trash pile to move to the next building."
        self.trash_spots: list[TrashSpot] = []
        self.repair_spots: list[RepairSpot] = []
        self.friends: list[FriendNPC] = []
        self.befriended_friends: set[str] = set()
        self.lesson_completed_buildings: set[int] = set()
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0
        self.inside_building = 0
        self.house_styles: dict[int, tuple[tuple[int, int, int], tuple[int, int, int]]] = {}
        self.style_options = [
            ("Garden green", (54, 77, 69), (86, 112, 98)),
            ("Warm brick", (89, 52, 48), (121, 76, 65)),
            ("Soft blue", (53, 68, 92), (86, 103, 126)),
        ]
        self.neighborhood_state = 0
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.intro_walk_x = 85.0
        self.intro_time = 0.0
        self.keys_down: set[int] = set()
        self.quiz_friend: FriendNPC | None = None
        self.quiz_question = QUIZ_OPTIONS[0]
        self.quiz_tries_left = 2
        self.game_over_ready = False
        self.show_instructions = False
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
        friend_positions = [(105, 122), (392, 118), (680, 122)]

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

    def door_index_near_player(self) -> int | None:
        for index, (left, right, base_y) in enumerate(BUILDING_POSITIONS):
            door_center = (left + right) / 2
            if abs(self.ball_x - door_center) <= 45 and abs(self.ball_y - (base_y + 34)) <= 62:
                return index
        return None

    def enter_house(self) -> None:
        repair_sets = [
            [
                (250, 295, "patch cracked wall", arcade.color.LIGHT_STEEL_BLUE, 5),
                (400, 190, "replace loose floorboard", arcade.color.GOLD, 4),
                (545, 330, "add new glass pane", arcade.color.LIGHT_BLUE, 6),
                (510, 225, "paint chipped trim", arcade.color.DARK_SEA_GREEN, 4),
            ],
            [
                (230, 325, "seal broken window frame", arcade.color.LIGHT_BLUE, 6),
                (350, 200, "sweep and level floor", arcade.color.GOLD, 4),
                (490, 300, "cover wall holes", arcade.color.LIGHT_STEEL_BLUE, 5),
                (585, 210, "tighten old door hinge", arcade.color.SIENNA, 4),
            ],
            [
                (230, 215, "nail down floor plank", arcade.color.GOLD, 4),
                (370, 335, "smooth damaged wall", arcade.color.LIGHT_STEEL_BLUE, 5),
                (520, 335, "replace cracked window", arcade.color.LIGHT_BLUE, 6),
                (575, 220, "brush fresh trim paint", arcade.color.DARK_SEA_GREEN, 4),
            ],
        ]

        self.repair_spots = [
            RepairSpot(x, y, label, color, cost)
            for x, y, label, color, cost in repair_sets[self.current_building]
        ]
        self.time_left = QUEST_TIME
        self.inside_building = self.current_building
        self.screen = "repair"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You enter {self.building_names[self.current_building]}. Click each repair spot."
        self.hint = "Repair the damaged wall, floor, window, and doorway details to finish this house."

    def visit_house(self, building_index: int) -> None:
        self.time_left = QUEST_TIME
        self.inside_building = building_index
        self.repair_spots = []
        self.screen = "visit"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You went back inside {self.building_names[building_index]}."
        self.hint = "This house is repaired now. Press F by the door to go back outside."

    def leave_house(self) -> None:
        left, right, base_y = BUILDING_POSITIONS[self.inside_building]
        self.ball_x = (left + right) / 2
        self.ball_y = base_y + 35
        self.screen = "playing"
        self.round_started = True
        self.message = "You step back outside."
        if self.trash_spots:
            self.hint = "Keep cleaning trash, or visit another finished house."
        else:
            self.hint = "Press F near the current door when you are ready to go inside."

    def can_finish_current_house(self) -> bool:
        return self.current_building in self.lesson_completed_buildings

    def current_target_friend_name(self) -> str:
        return ["Maya", "Jordan", "Ari"][self.current_building % 3]

    def known_name_letters(self, name: str) -> int:
        return min(len(name), self.friend_name_hints.get(name, 0))

    def friend_display_name(self, friend: FriendNPC) -> str:
        return self.display_name_from_hint(friend.name)

    def display_name_from_hint(self, name: str) -> str:
        known_letters = self.known_name_letters(name)
        if known_letters >= len(name):
            return name
        if known_letters == 0:
            return "???"
        shown = list(name[:known_letters])
        shown.extend("_" for _ in range(len(name) - known_letters))
        return " ".join(shown)

    def reveal_friend_name_hint(self) -> str:
        name = self.current_target_friend_name()
        known_letters = self.known_name_letters(name)
        if known_letters < len(name):
            known_letters += 1
            self.friend_name_hints[name] = known_letters
        if known_letters >= len(name):
            return f"You figured out the name {name}. Press T near them to answer the quiz."
        return f"Name hint found: {self.display_name_from_hint(name)}"

    def next_building(self) -> None:
        finished_building = self.building_names[self.current_building]
        self.current_building = (self.current_building + 1) % len(self.building_names)
        self.buildings_cleaned += 1
        self.friendship += 1
        self.upgrades = min(MAX_UPGRADES, self.upgrades + 1)
        self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
        self.message = f"{finished_building} is repaired. {self.building_names[self.current_building]} is next."
        self.hint = "The next cleanup starts right away."
        self.reset_round()

    def finish_repair(self) -> None:
        self.friendship += 1
        self.screen = "decorate"
        self.round_started = False
        self.keys_down.clear()
        self.message = "Choose how this repaired house should look."
        self.hint = "Press 1, 2, or 3 to pick a style. The next cleanup starts after your choice."

    def choose_house_style(self, style_index: int) -> None:
        _, roof_color, wall_color = self.style_options[style_index]
        self.house_styles[self.current_building] = (roof_color, wall_color)
        self.next_building()

    def fail_round(self) -> None:
        self.screen = "trash_game_over"
        self.message = "Game over. The timer ran out."
        self.hint = "You needed to clear the trash before time ran out."
        self.round_started = False

    def start_friend_quiz(self, friend: FriendNPC) -> None:
        self.quiz_friend = friend
        self.quiz_question = QUIZ_OPTIONS[(self.current_building + self.friendship) % len(QUIZ_OPTIONS)]
        self.quiz_tries_left = 2
        self.screen = "quiz"
        self.message = f"You know {friend.name}'s name. Answer their question."
        self.hint = "You get 2 tries. Think carefully."

    def answer_quiz(self, answer_index: int) -> None:
        if self.quiz_friend is None:
            return

        if answer_index == self.quiz_question["correct"]:
            self.friendship += 1
            self.befriended_friends.add(self.quiz_friend.name)
            self.lesson_completed_buildings.add(self.current_building)
            self.message = f"Correct. {self.quiz_friend.name} became your friend."
            self.hint = f"{self.quiz_question['fact']} Now you can finish repairing the house."
            self.quiz_friend = None
            self.screen = "playing"
            return

        self.quiz_tries_left -= 1
        if self.quiz_tries_left > 0:
            self.message = f"Not quite. Try again. Tries left: {self.quiz_tries_left}."
            self.hint = "Read the answer choices carefully before picking again."
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
            if friend.name in self.befriended_friends and self.current_building in self.lesson_completed_buildings:
                continue

            clicked_friend = x is not None and y is not None and (x - friend.x) ** 2 + (y - friend.y) ** 2 <= 24 ** 2
            near_ball = (self.ball_x - friend.x) ** 2 + (self.ball_y - friend.y) ** 2 <= FRIEND_DISTANCE ** 2

            if clicked_friend or (x is None and near_ball):
                if not near_ball:
                    self.message = "Move closer to the person first."
                    self.hint = "Friend balls can only hear you when your ball is nearby."
                    return True
                if self.known_name_letters(friend.name) < len(friend.name):
                    self.message = "You do not know this person's full name yet."
                    self.hint = "Pick up trash to find name hints, then come back when the name is complete."
                    return True

                self.start_friend_quiz(friend)
                return True

        if x is None and y is None:
            self.message = "Move close to a blue ball before pressing T."
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
            if self.door_index_near_player() == self.current_building:
                self.enter_house()
            else:
                self.message = "Stand by this house's door first."
                self.hint = "After the trash is clear, press F at the door to go inside."
            return

        if key == arcade.key.F:
            if self.screen in {"repair", "visit"}:
                self.leave_house()
                return
            if self.screen == "playing":
                door_index = self.door_index_near_player()
                if door_index is not None and door_index in self.house_styles:
                    self.visit_house(door_index)
                    return
                if door_index == self.current_building and not self.trash_spots:
                    self.enter_house()
                    return
                self.message = "Stand near a repaired door to go back inside."
                self.hint = "The current building opens after you clear the trash."
                return

        if key == arcade.key.T:
            self.try_befriend()
            return

        number_keys = (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3)
        if self.screen == "decorate" and key in number_keys:
            self.choose_house_style({arcade.key.KEY_1: 0, arcade.key.KEY_2: 1, arcade.key.KEY_3: 2}[key])
            return

        if self.screen == "quiz" and key in number_keys:
            self.answer_quiz({arcade.key.KEY_1: 0, arcade.key.KEY_2: 1, arcade.key.KEY_3: 2}[key])
            return

        if key != arcade.key.SPACE:
            return

        try:
            if self.screen in {"complete", "failed", "trash_game_over"}:
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

        if self.screen == "intro":
            if 310 <= x <= 490 and 135 <= y <= 190:
                self.reset_round()
            return

        if 10 <= x <= 45 and 18 <= y <= 53:
            self.show_instructions = not self.show_instructions
            return

        if self.screen == "quiz":
            for index in range(3):
                top = 300 - index * 62
                bottom = top - 46
                if 130 <= x <= 670 and bottom <= y <= top:
                    self.answer_quiz(index)
                    return
            return

        if self.screen == "decorate":
            for index in range(3):
                left = 150 + index * 175
                right = left + 130
                if left <= x <= right and 235 <= y <= 385:
                    self.choose_house_style(index)
                    return
            return

        if self.screen == "repair":
            for spot in self.repair_spots:
                if spot.fixed:
                    continue
                if (x - spot.x) ** 2 + (y - spot.y) ** 2 <= spot.radius ** 2:
                    is_final_repair = all(repair.fixed or repair is spot for repair in self.repair_spots)
                    if is_final_repair and not self.can_finish_current_house():
                        self.message = "Before finishing the house, answer a friend's question correctly."
                        self.hint = "Press F to go outside, then press T near a blue friend to learn the lesson."
                        return
                    if self.money < spot.cost:
                        self.message = f"Need ${spot.cost} to {spot.label}. You have ${self.money}."
                        self.hint = "Trash gives you repair money. Clean outside piles before fixing everything."
                        return
                    spot.fixed = True
                    self.money -= spot.cost
                    self.message = f"Spent ${spot.cost} to {spot.label}."
                    self.hint = "Keep repairing the damaged spots until the house is ready."
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
                self.message = self.reveal_friend_name_hint()
                self.hint = "When the full name is revealed, move near that person and press T for the quiz."
                if self.cleaned % 2 == 0:
                    self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
                if not self.trash_spots:
                    target_name = self.current_target_friend_name()
                    if self.known_name_letters(target_name) >= len(target_name):
                        self.message = f"The outside is clear, and you know {target_name}'s name."
                        self.hint = "Press T near them for the lesson quiz, or press F at the door to go inside."
                    else:
                        self.message = "The outside is clear. Press F to open the door."
                        self.hint = "You can open the door, but you need the full friend name before the quiz."
                break

    def draw_ball(self) -> None:
        if self.screen == "playing":
            arcade.draw_circle_outline(self.ball_x, self.ball_y, COLLECT_DISTANCE, (128, 133, 140), 1)
        arcade.draw_circle_filled(self.ball_x + 4, self.ball_y - 5, BALL_RADIUS, (15, 18, 25, 120))
        arcade.draw_circle_filled(self.ball_x, self.ball_y, BALL_RADIUS, (177, 154, 82))
        arcade.draw_circle_outline(self.ball_x, self.ball_y, BALL_RADIUS, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(self.ball_x - 5, self.ball_y + 5, 5, (222, 222, 214))

    def update_ball(self, delta_time: float) -> None:
        if self.screen not in {"playing", "repair", "visit", "dark"}:
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

        if self.screen in {"repair", "visit"}:
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
        if self.screen == "intro":
            self.intro_time += delta_time
            self.intro_walk_x += 55 * delta_time
            if self.intro_walk_x > 285:
                self.intro_walk_x = 285
            return

        self.update_ball(delta_time)

        if self.screen == "dark" and self.reached_entrance():
            self.screen = "game_over"
            self.game_over_ready = True
            self.keys_down.clear()
            return

        if self.screen != "playing":
            return

        if not self.trash_spots:
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

    def draw_building(
        self,
        left: float,
        right: float,
        base_y: float,
        height: float,
        roof_color,
        wall_color,
        repaired: bool = False,
    ) -> None:
        top = base_y + height
        arcade.draw_lrbt_rectangle_filled(left, right, base_y, top, wall_color)
        arcade.draw_lrbt_rectangle_outline(left, right, base_y, top, arcade.color.BLACK)
        roof_mid = (left + right) / 2
        arcade.draw_triangle_filled(left - 8, top, right + 8, top, roof_mid, top + 60, roof_color)
        arcade.draw_triangle_outline(left - 8, top, right + 8, top, roof_mid, top + 60, arcade.color.BLACK)

        if repaired:
            arcade.draw_line(left + 12, top - 7, right - 12, top - 7, (222, 222, 214), 3)
            arcade.draw_line(left + 12, base_y + 8, right - 12, base_y + 8, (222, 222, 214), 3)
        else:
            arcade.draw_line(left + 18, top - 25, left + 55, top - 62, arcade.color.BLACK, 3)
            arcade.draw_line(left + 55, top - 62, left + 44, top - 105, arcade.color.BLACK, 2)
            arcade.draw_line(right - 28, top - 35, right - 72, top - 78, arcade.color.BLACK, 3)
            arcade.draw_line(right - 72, top - 78, right - 48, top - 120, arcade.color.BLACK, 2)
            arcade.draw_lrbt_rectangle_filled(left + 10, left + 24, base_y + 18, top - 20, (35, 36, 42, 110))
            arcade.draw_lrbt_rectangle_filled(right - 34, right - 18, base_y + 35, top - 45, (36, 36, 41, 95))
            arcade.draw_line(left + 4, top - 12, roof_mid - 10, top + 45, (31, 24, 27), 3)
            arcade.draw_line(roof_mid + 18, top + 40, right - 4, top - 8, (31, 24, 27), 3)

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
            if repaired:
                arcade.draw_line(center_x, window_bottom, center_x, window_top, arcade.color.WHITE, 2)
                arcade.draw_line(window_left, window_bottom + window_height / 2, window_right, window_bottom + window_height / 2, arcade.color.WHITE, 2)
                arcade.draw_lrbt_rectangle_outline(window_left - 3, window_right + 3, window_bottom - 3, window_top + 3, (222, 222, 214), 2)
            else:
                arcade.draw_line(window_left + 7, window_top - 7, center_x - 2, window_bottom + 18, arcade.color.WHITE, 2)
                arcade.draw_line(center_x - 2, window_bottom + 18, window_right - 8, window_bottom + 8, arcade.color.WHITE, 2)
                arcade.draw_line(center_x - 2, window_bottom + 18, center_x + 10, window_top - 12, arcade.color.WHITE, 1)
            if not repaired and i % 2 == 0:
                arcade.draw_lrbt_rectangle_filled(
                    window_left - 4,
                    window_right + 4,
                    window_bottom + 11,
                    window_bottom + 19,
                    (87, 63, 45),
                )
                arcade.draw_lrbt_rectangle_filled(
                    window_left - 4,
                    window_right + 4,
                    window_top - 17,
                    window_top - 9,
                    (75, 55, 42),
                )
                arcade.draw_line(window_left - 3, window_bottom + 14, window_right + 3, window_top - 10, arcade.color.BLACK, 1)

    def draw_scene(self) -> None:
        self.draw_background()

        building_colors = [
            ((73, 52, 48), (58, 62, 70)),
            ((62, 43, 55), (64, 68, 76)),
            ((61, 63, 49), (70, 72, 76)),
        ]
        building_heights = [220, 235, 195]
        for index, (left, right, base_y) in enumerate(BUILDING_POSITIONS):
            roof_color, wall_color = building_colors[index]
            height = building_heights[index]
            repaired = index in self.house_styles
            if index in self.house_styles:
                roof_color, wall_color = self.house_styles[index]
            self.draw_building(left, right, base_y, height, roof_color, wall_color, repaired)
            door_width = 34
            door_height = 68
            door_center = (left + right) / 2
            door_left = door_center - door_width / 2
            door_right = door_center + door_width / 2
            door_color = (96, 66, 48) if repaired else (45, 36, 34)
            arcade.draw_lrbt_rectangle_filled(door_left, door_right, base_y, base_y + door_height, door_color)
            arcade.draw_lrbt_rectangle_outline(door_left, door_right, base_y, base_y + door_height, arcade.color.BLACK, 2)
            arcade.draw_circle_filled(door_right - 8, base_y + 34, 3, (150, 132, 82))
            if repaired:
                arcade.draw_lrbt_rectangle_outline(door_left + 5, door_right - 5, base_y + 8, base_y + door_height - 8, (222, 222, 214), 2)
                arcade.draw_lrbt_rectangle_filled(door_left - 18, door_left - 5, base_y + 4, base_y + 16, (54, 88, 60))
                arcade.draw_lrbt_rectangle_filled(door_right + 5, door_right + 18, base_y + 4, base_y + 16, (54, 88, 60))
                arcade.draw_circle_filled(door_left - 12, base_y + 22, 5, (185, 148, 84))
                arcade.draw_circle_filled(door_right + 12, base_y + 22, 5, (185, 148, 84))
            else:
                arcade.draw_line(door_left + 6, base_y + 58, door_right - 7, base_y + 43, arcade.color.BLACK, 2)
                arcade.draw_line(door_left + 7, base_y + 18, door_right - 10, base_y + 28, arcade.color.BLACK, 2)
                arcade.draw_lrbt_rectangle_filled(
                    door_left - 5,
                    door_right + 5,
                    base_y + 8,
                    base_y + 15,
                    (31, 30, 32),
                )
            if index in self.house_styles:
                door_label = "Press F to go inside"
            elif index == self.current_building and not self.trash_spots:
                door_label = "Press F to open door"
            else:
                door_label = ""
            if door_label:
                arcade.draw_text(
                    door_label,
                    door_center,
                    base_y + door_height + 10,
                    (222, 222, 214),
                    10,
                    anchor_x="center",
                )

        arcade.draw_lrbt_rectangle_filled(40, 760, 80, 105, (30, 32, 38))
        arcade.draw_line(0, 105, 800, 105, arcade.color.BLACK, 3)

        arcade.draw_text("bus stop", 675, 138, arcade.color.WHITE, 10)

        for trash in self.trash_spots:
            arcade.draw_circle_filled(trash.x, trash.y, trash.radius, arcade.color.BROWN_NOSE)
            arcade.draw_circle_outline(trash.x, trash.y, trash.radius, arcade.color.BLACK, 2)
            arcade.draw_text(trash.highlight, trash.x, trash.y - 5, arcade.color.WHITE, 8, anchor_x="center")

        for friend in self.friends:
            friend_color = (118, 139, 129) if friend.name in self.befriended_friends else (86, 104, 123)
            arcade.draw_line(friend.x, friend.y - 16, friend.x, friend.y - 42, arcade.color.BLACK, 4)
            arcade.draw_line(friend.x - 12, friend.y - 28, friend.x + 12, friend.y - 28, arcade.color.BLACK, 3)
            arcade.draw_line(friend.x, friend.y - 42, friend.x - 10, friend.y - 58, arcade.color.BLACK, 3)
            arcade.draw_line(friend.x, friend.y - 42, friend.x + 10, friend.y - 58, arcade.color.BLACK, 3)
            arcade.draw_ellipse_filled(friend.x, friend.y - 60, 28, 7, (15, 18, 25, 120))
            arcade.draw_circle_filled(friend.x, friend.y, 16, friend_color)
            arcade.draw_circle_outline(friend.x, friend.y, 16, arcade.color.BLACK, 2)
            arcade.draw_text(self.friend_display_name(friend), friend.x, friend.y + 24, arcade.color.WHITE, 10, anchor_x="center")
            label = "friend" if friend.name in self.befriended_friends else "press T"
            arcade.draw_text(label, friend.x, friend.y - 34, arcade.color.LIGHT_GRAY, 8, anchor_x="center")

        self.draw_ball()

    def draw_house_interior(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (25, 24, 31))
        repaired_inside = self.inside_building in self.house_styles
        wall_color = (93, 102, 100) if repaired_inside else (68, 65, 76)
        floor_color = (92, 72, 52) if repaired_inside else (72, 61, 54)
        arcade.draw_lrbt_rectangle_filled(90, 710, 120, 470, wall_color)
        arcade.draw_lrbt_rectangle_outline(90, 710, 120, 470, arcade.color.BLACK, 3)
        arcade.draw_lrbt_rectangle_filled(90, 710, 80, 120, floor_color)
        arcade.draw_line(90, 120, 710, 120, arcade.color.BLACK, 3)

        arcade.draw_lrbt_rectangle_filled(116, 285, 122, 165, (54, 64, 70))
        arcade.draw_lrbt_rectangle_outline(116, 285, 122, 165, arcade.color.BLACK, 2)
        arcade.draw_lrbt_rectangle_filled(126, 245, 162, 192, (62, 73, 78))
        arcade.draw_lrbt_rectangle_outline(126, 245, 162, 192, arcade.color.BLACK, 2)
        arcade.draw_line(140, 170, 175, 188, arcade.color.BLACK, 2)
        arcade.draw_line(215, 166, 238, 187, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(300, 366, 135, 178, (73, 54, 43))
        arcade.draw_lrbt_rectangle_outline(300, 366, 135, 178, arcade.color.BLACK, 2)
        arcade.draw_line(310, 135, 310, 113, arcade.color.BLACK, 3)
        arcade.draw_line(356, 135, 356, 113, arcade.color.BLACK, 3)
        arcade.draw_lrbt_rectangle_filled(308, 336, 188, 238, (55, 43, 38))
        arcade.draw_lrbt_rectangle_outline(308, 336, 188, 238, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(625, 686, 120, 232, (58, 44, 35))
        arcade.draw_lrbt_rectangle_outline(625, 686, 120, 232, arcade.color.BLACK, 2)
        arcade.draw_line(625, 158, 686, 158, arcade.color.BLACK, 2)
        arcade.draw_line(625, 196, 686, 196, arcade.color.BLACK, 2)
        arcade.draw_line(651, 120, 651, 232, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(120, 168, 82, 118, (88, 69, 45))
        arcade.draw_lrbt_rectangle_outline(120, 168, 82, 118, arcade.color.BLACK, 2)
        arcade.draw_line(120, 118, 144, 136, arcade.color.BLACK, 2)
        arcade.draw_lrbt_rectangle_filled(555, 608, 83, 118, (82, 64, 43))
        arcade.draw_lrbt_rectangle_outline(555, 608, 83, 118, arcade.color.BLACK, 2)
        arcade.draw_line(555, 118, 582, 134, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(165, 245, 315, 405, (34, 44, 60))
        arcade.draw_lrbt_rectangle_outline(165, 245, 315, 405, arcade.color.BLACK, 2)
        arcade.draw_line(205, 315, 205, 405, arcade.color.BLACK, 2)
        arcade.draw_line(165, 360, 245, 360, arcade.color.BLACK, 2)
        arcade.draw_line(178, 394, 203, 367, arcade.color.WHITE, 2)
        arcade.draw_line(203, 367, 194, 333, arcade.color.WHITE, 2)
        arcade.draw_line(203, 367, 231, 349, arcade.color.WHITE, 1)

        arcade.draw_lrbt_rectangle_filled(540, 620, 315, 405, (34, 44, 60))
        arcade.draw_lrbt_rectangle_outline(540, 620, 315, 405, arcade.color.BLACK, 2)
        arcade.draw_line(580, 315, 580, 405, arcade.color.BLACK, 2)
        arcade.draw_line(540, 360, 620, 360, arcade.color.BLACK, 2)
        arcade.draw_line(552, 326, 579, 354, arcade.color.WHITE, 2)
        arcade.draw_line(579, 354, 608, 390, arcade.color.WHITE, 2)
        arcade.draw_line(579, 354, 565, 384, arcade.color.WHITE, 1)

        arcade.draw_lrbt_rectangle_filled(360, 440, 120, 260, (61, 48, 42))
        arcade.draw_lrbt_rectangle_outline(360, 440, 120, 260, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(425, 195, 4, arcade.color.GOLD)
        arcade.draw_line(362, 252, 393, 228, arcade.color.BLACK, 2)
        arcade.draw_line(393, 228, 386, 201, arcade.color.BLACK, 2)
        arcade.draw_line(438, 126, 407, 151, arcade.color.BLACK, 2)

        if repaired_inside:
            arcade.draw_lrbt_rectangle_filled(130, 710, 410, 426, (222, 222, 214))
            arcade.draw_lrbt_rectangle_filled(115, 165, 120, 132, (54, 88, 60))
            arcade.draw_lrbt_rectangle_filled(630, 685, 120, 132, (54, 88, 60))
            arcade.draw_circle_filled(140, 140, 8, (185, 148, 84))
            arcade.draw_circle_filled(660, 140, 8, (185, 148, 84))
        else:
            arcade.draw_line(145, 285, 188, 260, arcade.color.BLACK, 2)
            arcade.draw_line(188, 260, 177, 235, arcade.color.BLACK, 2)
            arcade.draw_line(500, 285, 540, 260, arcade.color.BLACK, 2)
            arcade.draw_line(540, 260, 560, 290, arcade.color.BLACK, 2)
            arcade.draw_line(245, 121, 305, 105, arcade.color.BLACK, 2)
            arcade.draw_line(305, 105, 358, 118, arcade.color.BLACK, 2)
            arcade.draw_line(460, 116, 520, 101, arcade.color.BLACK, 2)

        arcade.draw_text(
            f"Inside {self.building_names[self.inside_building]}",
            400,
            485,
            arcade.color.WHITE,
            22,
            anchor_x="center",
        )

        for spot in self.repair_spots:
            if spot.fixed:
                arcade.draw_circle_outline(spot.x, spot.y, 17, arcade.color.DARK_SEA_GREEN, 3)
                arcade.draw_text("fixed", spot.x, spot.y - 5, arcade.color.WHITE, 8, anchor_x="center")
                continue

            arcade.draw_circle_outline(spot.x, spot.y, spot.radius, spot.color, 4)
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius + 3, arcade.color.WHITE, 1)
            arcade.draw_text(
                f"${spot.cost}",
                spot.x,
                spot.y - 5,
                arcade.color.WHITE,
                10,
                anchor_x="center",
            )

        self.draw_ball()

    def draw_quiz(self) -> None:
        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(90, 710, 130, 500, (18, 22, 31))
        arcade.draw_lrbt_rectangle_outline(90, 710, 130, 500, arcade.color.WHITE, 3)
        arcade.draw_text("Community Question", 400, 460, arcade.color.GOLD, 24, anchor_x="center")
        arcade.draw_text(f"Tries left: {self.quiz_tries_left}", 400, 438, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        arcade.draw_text(
            self.quiz_question["question"],
            130,
            395,
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

    def draw_decorate(self) -> None:
        self.draw_background()
        arcade.draw_text("Choose a finished look", 400, 455, (222, 222, 214), 28, anchor_x="center")
        arcade.draw_text(
            self.building_names[self.current_building],
            400,
            420,
            (156, 160, 166),
            14,
            anchor_x="center",
        )

        for index, (name, roof_color, wall_color) in enumerate(self.style_options):
            left = 150 + index * 175
            right = left + 130
            base_y = 235
            top = 335
            mid_x = (left + right) / 2
            arcade.draw_lrbt_rectangle_filled(left, right, base_y, top, wall_color)
            arcade.draw_lrbt_rectangle_outline(left, right, base_y, top, arcade.color.BLACK, 2)
            arcade.draw_triangle_filled(left - 8, top, right + 8, top, mid_x, top + 44, roof_color)
            arcade.draw_triangle_outline(left - 8, top, right + 8, top, mid_x, top + 44, arcade.color.BLACK)
            arcade.draw_lrbt_rectangle_filled(mid_x - 14, mid_x + 14, base_y, base_y + 48, (60, 45, 37))
            arcade.draw_lrbt_rectangle_outline(mid_x - 14, mid_x + 14, base_y, base_y + 48, arcade.color.BLACK, 2)
            arcade.draw_lrbt_rectangle_filled(left + 18, left + 42, base_y + 55, base_y + 84, (150, 177, 190))
            arcade.draw_lrbt_rectangle_outline(left + 18, left + 42, base_y + 55, base_y + 84, arcade.color.BLACK, 2)
            arcade.draw_lrbt_rectangle_filled(right - 42, right - 18, base_y + 55, base_y + 84, (150, 177, 190))
            arcade.draw_lrbt_rectangle_outline(right - 42, right - 18, base_y + 55, base_y + 84, arcade.color.BLACK, 2)
            arcade.draw_text(f"{index + 1}", mid_x, 365, arcade.color.GOLD, 18, anchor_x="center")
            arcade.draw_text(name, mid_x, 205, (222, 222, 214), 12, anchor_x="center")

        arcade.draw_text("Press 1, 2, or 3", 400, 165, (156, 160, 166), 13, anchor_x="center")

    def draw_intro(self) -> None:
        self.draw_background()
        arcade.draw_text("Neighborhood Cleanup", 400, 505, (222, 222, 214), 36, anchor_x="center")
        arcade.draw_text(
            "Walk to the homes, learn who lives nearby, and help repair the block.",
            400,
            465,
            (156, 160, 166),
            14,
            anchor_x="center",
        )

        intro_buildings = [
            (430, 525, 185, 150, (73, 52, 48), (58, 62, 70)),
            (540, 650, 175, 170, (62, 43, 55), (64, 68, 76)),
            (665, 745, 190, 135, (61, 63, 49), (70, 72, 76)),
        ]
        for left, right, base_y, height, roof_color, wall_color in intro_buildings:
            self.draw_building(left, right, base_y, height, roof_color, wall_color)

        arcade.draw_lrbt_rectangle_filled(55, 745, 90, 125, (30, 32, 38))
        arcade.draw_line(55, 125, 745, 125, arcade.color.BLACK, 3)

        person_x = self.intro_walk_x
        arrived = person_x >= 285
        wave = math.sin(self.intro_time * 7) * 10 if arrived else 0
        arcade.draw_ellipse_filled(person_x, 84, 34, 8, (15, 18, 25, 130))
        stick_start_x = person_x - 24
        stick_start_y = 160
        stick_end_x = person_x + 62
        stick_end_y = 188
        arcade.draw_line(stick_start_x, stick_start_y, stick_end_x, stick_end_y, (82, 50, 28), 4)
        arcade.draw_line(person_x - 8, 142, stick_start_x + 28, stick_start_y + 10, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(stick_end_x + 7, stick_end_y - 6, 18, (145, 35, 38))
        arcade.draw_circle_outline(stick_end_x + 7, stick_end_y - 6, 18, arcade.color.BLACK, 2)
        arcade.draw_line(stick_end_x - 3, stick_end_y - 3, stick_end_x + 12, stick_end_y + 6, arcade.color.BLACK, 2)
        arcade.draw_line(stick_end_x + 2, stick_end_y + 1, stick_end_x + 17, stick_end_y - 12, arcade.color.BLACK, 2)
        arcade.draw_line(person_x, 134, person_x, 104, arcade.color.BLACK, 5)
        arcade.draw_line(person_x - 14, 120, person_x + 8, 119, arcade.color.BLACK, 3)
        if arrived:
            arcade.draw_line(person_x + 8, 119, person_x + 28, 144 + wave, arcade.color.BLACK, 3)
            arcade.draw_circle_filled(person_x + 31, 147 + wave, 4, (177, 154, 82))
            arcade.draw_text("Press START", person_x + 80, 214, (222, 222, 214), 13, anchor_x="center")
            arcade.draw_text("I am ready.", person_x + 80, 196, (156, 160, 166), 10, anchor_x="center")
        else:
        arcade.draw_line(person_x + 8, 119, person_x + 20, 104, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x - 11, 88, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x + 12, 89, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(person_x, 150, 16, (177, 154, 82))
        arcade.draw_circle_outline(person_x, 150, 16, arcade.color.BLACK, 2)

        arcade.draw_lrbt_rectangle_filled(310, 490, 135, 190, (174, 151, 82))
        arcade.draw_lrbt_rectangle_outline(310, 490, 135, 190, arcade.color.BLACK, 3)
        arcade.draw_text("START", 400, 153, arcade.color.BLACK, 22, anchor_x="center")

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

    def draw_trash_game_over(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, arcade.color.BLACK)
        arcade.draw_text("GAME OVER", 400, 330, arcade.color.GOLD, 64, anchor_x="center")
        arcade.draw_text("You ran out of time picking up trash.", 400, 270, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Press SPACE to try again or ESC to quit.", 400, 230, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(10, 790, 492, 590, (14, 17, 24))
        arcade.draw_lrbt_rectangle_outline(10, 790, 492, 590, (126, 132, 142))

        arcade.draw_text("Neighborhood Cleanup", 22, 562, (220, 221, 218), 22)
        arcade.draw_text("ESC quits", 720, 565, (156, 160, 166), 10, anchor_x="center")
        arcade.draw_text(f"Building: {self.building_names[self.current_building]}", 22, 538, (156, 160, 166), 12)
        arcade.draw_text(f"Trash: {self.cleaned}", 22, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Money: ${self.money}", 125, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Friendship: {self.friendship}", 240, 516, (214, 215, 212), 12)
        target_name = self.current_target_friend_name()
        arcade.draw_text(f"Name: {self.display_name_from_hint(target_name)}", 390, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Upgrades: {self.upgrades}/{MAX_UPGRADES}", 500, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Time: {self.time_left:0.1f}s", 650, 516, (214, 215, 212), 12)
        fixed_count = sum(1 for repair in self.repair_spots if repair.fixed)
        repair_total = len(self.repair_spots)
        if self.screen == "repair" and repair_total:
            arcade.draw_text(f"Repairs: {fixed_count}/{repair_total}", 260, 538, (156, 160, 166), 12)
        else:
            arcade.draw_text(
                f"Neighborhood level: {self.neighborhood_state + 1}/{BUILDING_STAGES}",
                260,
                538,
                (156, 160, 166),
                12,
            )

        bar_left = 22
        bar_right = 778
        bar_bottom = 500
        bar_top = 508
        arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, arcade.color.DARK_SLATE_GRAY)
        filled = bar_left + (bar_right - bar_left) * max(0, self.time_left) / QUEST_TIME
        arcade.draw_lrbt_rectangle_filled(bar_left, filled, bar_bottom, bar_top, (174, 151, 82))
        arcade.draw_lrbt_rectangle_outline(bar_left, bar_right, bar_bottom, bar_top, (126, 132, 142))

        arcade.draw_lrbt_rectangle_filled(105, 695, 16, 50, (14, 17, 24))
        arcade.draw_lrbt_rectangle_outline(105, 695, 16, 50, (126, 132, 142))
        arcade.draw_text(self.message, 122, 29, (117, 147, 135), 11, width=552)

        arcade.draw_circle_filled(28, 35, 17, (14, 17, 24))
        arcade.draw_circle_outline(28, 35, 17, (222, 222, 214), 2)
        arcade.draw_text("?", 28, 25, (222, 222, 214), 18, anchor_x="center")

        if self.show_instructions:
            arcade.draw_lrbt_rectangle_filled(175, 625, 112, 248, (14, 17, 24))
            arcade.draw_lrbt_rectangle_outline(175, 625, 112, 248, (222, 222, 214), 2)
            arcade.draw_text("Instructions", 400, 220, (222, 222, 214), 18, anchor_x="center")
            arcade.draw_text(self.hint, 198, 188, (156, 160, 166), 11, width=404, multiline=True)
            arcade.draw_text(
                "Move: WASD/arrows   Talk: T   Door/leave: F   Quit: ESC",
                400,
                132,
                (156, 160, 166),
                10,
                anchor_x="center",
            )


    def on_draw(self) -> None:
        self.clear()
        if self.camera is not None:
            self.camera.use()

        if self.screen == "intro":
            self.draw_intro()
            return

        if self.screen == "quiz":
            self.draw_quiz()
            return

        if self.screen == "decorate":
            self.draw_decorate()
            return

        if self.screen == "dark":
            self.draw_dark_challenge()
            return

        if self.screen == "game_over":
            self.draw_game_over()
            return

        if self.screen == "trash_game_over":
            self.draw_trash_game_over()
            return

        if self.screen in {"repair", "visit"}:
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
