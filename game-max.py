"""Neighborhood Cleanup: a more detailed MVP for the serious game idea."""

from __future__ import annotations

import random
import math

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neighborhood Cleanup: South Block"

QUEST_TIME = 30.0
MAX_UPGRADES = 3
MAX_INTERIOR_UPGRADES = 3
TRASH_SCORE = 4
BUILDING_STAGES = 3
BALL_SPEED = 220
BALL_RADIUS = 16
COLLECT_DISTANCE = 90
TRASH_CLICK_RADIUS = 50
FRIEND_DISTANCE = 75
ENTRANCE_X = 720
ENTRANCE_Y = 300
ENTRANCE_WIDTH = 55
ENTRANCE_HEIGHT = 120
HOUSE_SPACING = 280
HOUSE_BASE_Y = 120
HOUSE_WIDTHS = [140, 170, 120]
HOUSE_HEIGHTS = [220, 235, 195]

# New friend names with meaning-based riddle clues
# Name meanings: Rosa=rose/flower, Leo=lion, Maya=water/illusion
FRIEND_NAMES = ["Rosa", "Leo", "Maya"]

# Riddle clues keyed to name meaning
FRIEND_RIDDLES = {
    "Rosa": {
        "riddle": "I bloom in your garden, red or pink or white.\nI smell so sweet and I have thorns to bite.\nPeople give me on Valentine's Day.\nWhat flower am I? (That's the name — take a guess!)",
        "hint_stages": [
            "Think of a flower that blooms red, pink, or white...",
            "This flower has thorns and a sweet smell...",
            "People give this flower on Valentine's Day. 4 letters. R _ _ _",
        ],
        "answer": "rosa",
        "conversation": [
            ("Rosa", "Hey... you actually stopped. Most people just walk past."),
            ("You", "Of course I stopped. You doing okay?"),
            ("Rosa", "Honestly? Not really. This place used to feel like somewhere. Now it's just... empty."),
            ("You", "What do you miss most about it?"),
            ("Rosa", "My grandma used to grow flowers out front. This whole block smelled different. Better."),
            ("You", "That sounds really beautiful. Maybe it can smell like that again."),
            ("Rosa", "Maybe. Hey — do you wanna hear something? My name means something beautiful too. Can you figure it out?"),
        ],
        "fact": "Loneliness often comes from broken places and broken connections. Restoring neighborhoods restores belonging.",
    },
    "Leo": {
        "riddle": "I'm the king of the jungle, fierce and proud.\nI roar so loud it echoes through the crowd.\nI have a mane around my face so bold.\nWhat am I? (3 letters — my name's been told!)",
        "hint_stages": [
            "Think of an animal that's called the king of the jungle...",
            "This animal has a big mane around its face...",
            "It roars loudly. 3 letters. L _ _",
        ],
        "answer": "leo",
        "conversation": [
            ("Leo", "Oh wow, you're actually cleaning this up. I didn't think anyone cared."),
            ("You", "I care. How long have you been around here?"),
            ("Leo", "My whole life. Watched this block fall apart piece by piece."),
            ("You", "That's hard. Did you ever try to fix things?"),
            ("Leo", "I used to. But fixing things alone feels pointless after a while. You stop trying."),
            ("You", "You're not alone anymore. What's your name?"),
            ("Leo", "Ha — my name's something strong. Like an animal. Can you guess it?"),
        ],
        "fact": "Isolation shrinks our world. When one person shows up, it signals to others that they matter — and that changes everything.",
    },
    "Maya": {
        "riddle": "I fall from the sky and I fill up the sea.\nI flow through the rivers so wild and free.\nPlants drink me up and clouds are made of me.\nWhat am I? (4 letters — what do you see?)",
        "hint_stages": [
            "Think of something that falls from the sky and fills the ocean...",
            "This thing flows in rivers, and clouds are made of it...",
            "Plants drink it. It's essential for life. 4 letters. M _ _ _",
        ],
        "answer": "maya",
        "conversation": [
            ("Maya", "I was watching you from over here. You've been at it a while."),
            ("You", "It's worth it. What's your story?"),
            ("Maya", "I moved here two years ago. Never really found my people."),
            ("You", "What do you mean?"),
            ("Maya", "You know how you can be in a crowded room and feel invisible? That's every day for me here."),
            ("You", "I see you right now. You're not invisible to me."),
            ("Maya", "That's... really nice. My name actually means something essential — something every living thing needs. Guess?"),
        ],
        "fact": "Being seen is one of the most powerful human needs. One moment of genuine recognition can change a person's entire day — or life.",
    },
}

INTERIOR_REPAIR_SETS = [
    [
        (205, 355, "fix the ceiling crack", arcade.color.LIGHT_STEEL_BLUE, 3),
        (405, 250, "repair the table leg", arcade.color.GOLD, 3),
        (600, 175, "replace the loose lamp", arcade.color.DARK_SEA_GREEN, 4),
    ],
    [
        (220, 340, "patch the wall hole", arcade.color.LIGHT_BLUE, 3),
        (405, 245, "tighten the cabinet door", arcade.color.GOLD, 4),
        (585, 175, "fix the broken shelf", arcade.color.LIGHT_STEEL_BLUE, 3),
    ],
    [
        (215, 345, "seal the window gap", arcade.color.LIGHT_BLUE, 3),
        (405, 250, "repair the floor seam", arcade.color.GOLD, 4),
        (590, 175, "straighten the hanging frame", arcade.color.DARK_SEA_GREEN, 4),
    ],
]
INTERIOR_UPGRADE_SETS = [
    [
        (225, 330, "add a reading nook", arcade.color.GOLD, 4),
        (405, 245, "set up a warm lamp", arcade.color.LIGHT_STEEL_BLUE, 4),
        (585, 185, "place a potted plant", arcade.color.DARK_SEA_GREEN, 5),
    ],
    [
        (215, 345, "hang bright curtains", arcade.color.LIGHT_BLUE, 5),
        (405, 250, "bring in a soft rug", arcade.color.GOLD, 5),
        (590, 175, "install a shelf", arcade.color.LIGHT_STEEL_BLUE, 6),
    ],
    [
        (230, 320, "add art to the walls", arcade.color.LIGHT_STEEL_BLUE, 6),
        (405, 240, "upgrade the seating", arcade.color.GOLD, 6),
        (575, 190, "finish the cozy corner", arcade.color.DARK_SEA_GREEN, 7),
    ],
]

QUIZ_OPTIONS = [
    {
        "question": "Abandoned homes can sit empty for years, getting worse. What's ONE real way a restored house helps the community?",
        "answers": [
            "It becomes safe housing, a youth center, or community garden where isolated people can connect",
            "It automatically makes everyone happy and solves all neighborhood problems instantly",
            "It only matters if the neighborhood is rich and has lots of money",
        ],
        "correct": 0,
        "fact": "Empty buildings waste resources and increase loneliness. When fixed and reopened, they become gathering spaces where lonely people find friends, purpose, and belonging.",
    },
    {
        "question": "A teen feels invisible at school—no friends, always alone at lunch. What actually helps them?",
        "answers": [
            "A real person noticing them, inviting them to a safe group activity, or club where others share their interests",
            "Ignoring the feeling because it will go away on its own eventually",
            "Telling them to just be more confident and stop being so quiet",
        ],
        "correct": 0,
        "fact": "Loneliness kills—it's as dangerous as smoking. Real connection happens when one person notices another and creates space for them. Teen loneliness leads to depression and worse. Noticing matters.",
    },
    {
        "question": "A neighborhood cleanup project is starting. Why should the lonely teens and isolated families LEAD it, not just watch?",
        "answers": [
            "Because doing real work together creates genuine friendship and purpose faster than anything else",
            "Because kids should work free and feel grateful for the opportunity",
            "Because it doesn't really matter who does it as long as the work gets done",
        ],
        "correct": 0,
        "fact": "Belonging comes through shared meaningful work. When isolated people work TOGETHER on something real, they go from invisible to valued. The work becomes theirs.",
    },
]


class TrashSpot:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        # Keep trash sitting on the ground instead of floating at arbitrary spawn heights.
        self.y = HOUSE_BASE_Y + 14
        self.radius = 22
        self.trash_type = random.choice(["can", "bag", "box", "rubble"])
        self.rotation = random.uniform(0, 360)
        self.pulse = random.uniform(0, math.pi * 2)  # For glowing animation
        self.collected = False


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
        self.conversation_step = 0
        self.riddle_hint_level = 0


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
        self.interior_upgrade_levels: dict[int, int] = {}
        self.message = "Press SPACE to begin."
        self.hint = "Clear every trash pile to move to the next building."
        self.trash_spots: list[TrashSpot] = []
        self.repair_spots: list[RepairSpot] = []
        self.interior_spots: list[RepairSpot] = []
        self.friends: list[FriendNPC] = []
        self.befriended_friends: set[str] = set()
        self.guessed_friend_names: set[str] = set()
        self.lesson_completed_buildings: set[int] = set()
        self.inside_repaired_buildings: set[int] = set()
        self.friend_inside_by_building: dict[int, str] = {}
        self.buildings_cleaned = 0
        self.building_names = ["North House", "Corner Lot", "Old Flat"]
        self.current_building = 0
        self.inside_building = 0
        self.interior_mode = "repair"
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
        self.start_countdown = 0.0
        self.keys_down: set[int] = set()
        # Friend interaction state
        self.active_conversation_friend: FriendNPC | None = None
        self.conversation_step = 0
        self.in_conversation = False
        self.in_riddle = False
        self.riddle_guess = ""
        self.riddle_hint_shown = 0
        self.quiz_friend: FriendNPC | None = None
        self.quiz_question = QUIZ_OPTIONS[0]
        self.quiz_tries_left = 2
        self.game_over_ready = False
        self.show_instructions = False
        self.pulse_time = 0.0
        # World state
        self.generated_houses: dict[int, tuple[float, float, int, int, tuple, tuple]] = {}
        self.configure_camera()

    def get_building_name(self, building_index: int) -> str:
        name_parts = ["North", "South", "East", "West", "Old", "New", "Grand", "Sunny"]
        name_types = ["House", "Building", "Lot", "Flat", "Tower", "Hall"]
        part = name_parts[building_index % len(name_parts)]
        name_type = name_types[(building_index // len(name_parts)) % len(name_types)]
        return f"{part} {name_type}"

    def get_house_position(self, building_index: int) -> tuple[float, float, int, int]:
        if building_index in self.generated_houses:
            left, right, base_y, height, _, _ = self.generated_houses[building_index]
            return left, right, base_y, height
        rng = random.Random(f"house_{building_index}")
        center_x = building_index * HOUSE_SPACING + 150
        width = rng.choice(HOUSE_WIDTHS)
        height = rng.choice(HOUSE_HEIGHTS)
        left = center_x - width / 2
        right = center_x + width / 2
        base_y = HOUSE_BASE_Y
        style_idx = building_index % 3
        _, roof_color, wall_color = self.style_options[style_idx]
        self.generated_houses[building_index] = (left, right, base_y, height, roof_color, wall_color)
        return left, right, base_y, height

    def get_house_colors(self, building_index: int) -> tuple:
        if building_index not in self.generated_houses:
            self.get_house_position(building_index)
        _, _, _, _, roof_color, wall_color = self.generated_houses[building_index]
        if building_index in self.house_styles:
            roof_color, wall_color = self.house_styles[building_index]
        return roof_color, wall_color

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
        self.message = "Click trash piles to clean the building!"
        self.hint = "Move near trash with WASD/arrows, then click it to pick up. Collect all trash to proceed."
        self.trash_spots = []
        self.friends = []
        self.in_conversation = False
        self.in_riddle = False
        self.active_conversation_friend = None

        left, right, base_y, height = self.get_house_position(self.current_building)
        building_center_x = (left + right) / 2

        # Trash positions — scattered in the street in FRONT of the building
        # base_y is ~120, HUD bottom is ~490. Player min_y ~111. Trash at ~160-220 is reachable.
        relative_positions = [
            (-80, 55), (-40, 65), (0, 50), (50, 70), (85, 55), (25, 60)
        ]
        for rel_x, rel_y in relative_positions:
            self.trash_spots.append(TrashSpot(building_center_x + rel_x, base_y + rel_y))

        # Friends stand at DIFFERENT buildings nearby — one per adjacent house
        for i in range(3):
            friend_name = FRIEND_NAMES[i % len(FRIEND_NAMES)]
            # Each friend is at a different building index around the current one
            building_offset = i - 1  # -1, 0, +1 relative buildings
            target_idx = self.current_building + building_offset
            fl, fr, fb, _ = self.get_house_position(target_idx)
            fx = (fl + fr) / 2
            fy = fb + 50  # Stand just above ground, in front of their building
            f = FriendNPC(friend_name, fx, fy)
            self.friends.append(f)

        self.ball_x = building_center_x
        self.ball_y = base_y + 40
        self.screen = "playing"
        self.round_started = True

    def door_index_near_player(self) -> int | None:
        player_building_idx = int(self.ball_x / HOUSE_SPACING)
        for offset in range(-2, 3):
            index = player_building_idx + offset
            left, right, base_y, _ = self.get_house_position(index)
            door_center = (left + right) / 2
            if abs(self.ball_x - door_center) <= 45 and abs(self.ball_y - (base_y + 34)) <= 62:
                return index
        return None

    def enter_house(self) -> None:
        rng = random.Random(f"repair_{self.current_building}")
        base_repairs = [
            ("patch cracked wall", arcade.color.LIGHT_STEEL_BLUE, 5),
            ("replace loose floorboard", arcade.color.GOLD, 4),
            ("add new glass pane", arcade.color.LIGHT_BLUE, 6),
            ("paint chipped trim", arcade.color.DARK_SEA_GREEN, 4),
        ]
        rng.shuffle(base_repairs)
        self.repair_spots = [
            RepairSpot(250 + i * 100, 295 - (i % 2) * 100, label, color, cost)
            for i, (label, color, cost) in enumerate(base_repairs)
        ]
        self.time_left = QUEST_TIME
        self.inside_building = self.current_building
        self.screen = "repair"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You enter {self.get_building_name(self.current_building)}. Click each repair spot."
        self.hint = "Repair the damaged spots to finish this house."
        self.interior_spots = []

    def visit_house(self, building_index: int) -> None:
        self.time_left = QUEST_TIME
        self.inside_building = building_index
        repaired = building_index in self.inside_repaired_buildings
        self.interior_mode = "upgrade" if repaired else "repair"
        if repaired:
            upgrade_level = self.interior_upgrade_levels.get(building_index, 0)
            if upgrade_level < MAX_INTERIOR_UPGRADES:
                self.interior_spots = [
                    RepairSpot(x, y, label, color, cost)
                    for x, y, label, color, cost in INTERIOR_UPGRADE_SETS[upgrade_level]
                ]
            else:
                self.interior_spots = []
        else:
            self.interior_spots = [
                RepairSpot(x, y, label, color, cost)
                for x, y, label, color, cost in INTERIOR_REPAIR_SETS[building_index % 3]
            ]
        self.screen = "visit"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You went back inside {self.get_building_name(building_index)}."
        self.hint = "Click upgrade spots, or press F by the door to go back outside."

    def leave_house(self) -> None:
        left, right, base_y, _ = self.get_house_position(self.inside_building)
        self.ball_x = (left + right) / 2
        self.ball_y = base_y + 35
        self.screen = "playing"
        self.round_started = True
        self.message = "You step back outside."
        self.hint = "Press F near a repaired door to go back inside."

    def finish_interior_repair(self) -> None:
        self.inside_repaired_buildings.add(self.inside_building)
        self.interior_upgrade_levels.setdefault(self.inside_building, 0)
        self.interior_spots = []
        self.message = f"The inside of {self.get_building_name(self.inside_building)} is fixed."
        self.hint = "Press F by the door to go back outside."

    def finish_interior_upgrade(self) -> None:
        current_level = self.interior_upgrade_levels.get(self.inside_building, 0)
        next_level = min(MAX_INTERIOR_UPGRADES, current_level + 1)
        self.interior_upgrade_levels[self.inside_building] = next_level
        self.message = f"{self.get_building_name(self.inside_building)} reached upgrade tier {next_level}."
        if next_level < MAX_INTERIOR_UPGRADES:
            self.interior_spots = [
                RepairSpot(x, y, label, color, cost)
                for x, y, label, color, cost in INTERIOR_UPGRADE_SETS[next_level]
            ]
            self.hint = "Keep upgrading, or press F to go back outside."
        else:
            self.interior_spots = []
            self.hint = "Fully upgraded! Press F to go back outside."

    def can_finish_current_house(self) -> bool:
        return self.current_building in self.lesson_completed_buildings

    def current_target_friend_name(self) -> str:
        # The target friend is always the one placed at the current building (index 1, offset 0)
        if self.friends:
            return self.friends[1].name
        return FRIEND_NAMES[self.current_building % len(FRIEND_NAMES)]

    def has_uncollected_trash(self) -> bool:
        return any(not trash.collected for trash in self.trash_spots)

    def uncollected_trash_count(self) -> int:
        return sum(1 for trash in self.trash_spots if not trash.collected)

    def friend_display_name(self, friend: FriendNPC) -> str:
        if friend.name in self.befriended_friends or friend.name in self.guessed_friend_names:
            return friend.name
        return "???"

    def friend_label_text(self, friend: FriendNPC) -> str:
        if friend.name in self.befriended_friends:
            return "friend ♥"
        target = self.current_target_friend_name()
        if friend.name != target:
            return "not yet"
        if self.has_uncollected_trash():
            return "clean trash first"
        return "press T to talk"

    def next_building(self) -> None:
        finished_building = self.get_building_name(self.current_building)
        self.current_building += 1
        self.buildings_cleaned += 1
        self.friendship += 1
        self.upgrades = min(MAX_UPGRADES, self.upgrades + 1)
        self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
        self.message = f"{finished_building} is repaired. {self.get_building_name(self.current_building)} is next."
        self.hint = "The next cleanup starts right away."
        self.reset_round()

    def finish_repair(self) -> None:
        self.friendship += 1
        self.screen = "decorate"
        self.round_started = False
        self.keys_down.clear()
        self.message = "Choose how this repaired house should look."
        self.hint = "Press 1, 2, or 3 to pick a style."

    def choose_house_style(self, style_index: int) -> None:
        _, roof_color, wall_color = self.style_options[style_index]
        self.house_styles[self.current_building] = (roof_color, wall_color)
        self.next_building()

    def fail_round(self) -> None:
        self.screen = "trash_game_over"
        self.message = "Game over. The timer ran out."
        self.hint = "You needed to clear the trash before time ran out."
        self.round_started = False

    # ---- Conversation / Riddle system ----

    def start_conversation(self, friend: FriendNPC) -> None:
        """Start the life-conversation with a friend before the riddle."""
        self.active_conversation_friend = friend
        self.conversation_step = 0
        self.in_conversation = True
        self.in_riddle = False
        self.screen = "conversation"

    def advance_conversation(self) -> None:
        """Move through conversation lines; transition to riddle at end."""
        if self.active_conversation_friend is None:
            return
        data = FRIEND_RIDDLES[self.active_conversation_friend.name]
        convo = data["conversation"]
        self.conversation_step += 1
        if self.conversation_step >= len(convo):
            # Move to riddle
            self.in_conversation = False
            self.in_riddle = True
            self.riddle_guess = ""
            self.riddle_hint_shown = 0
            self.screen = "riddle"

    def submit_riddle_guess(self) -> None:
        if self.active_conversation_friend is None:
            return
        data = FRIEND_RIDDLES[self.active_conversation_friend.name]
        if self.riddle_guess.strip().lower() == data["answer"]:
            friend = self.active_conversation_friend
            self.guessed_friend_names.add(friend.name)
            self.in_riddle = False
            self.active_conversation_friend = None
            self.riddle_guess = ""
            # Start quiz
            self.start_friend_quiz(friend)
        else:
            # Show next hint
            if self.riddle_hint_shown < 2:
                self.riddle_hint_shown += 1
                self.message = f"Not quite... Hint: {data['hint_stages'][self.riddle_hint_shown]}"
            else:
                self.message = "Keep trying! Think about what the riddle describes."

    def start_friend_quiz(self, friend: FriendNPC) -> None:
        self.quiz_friend = friend
        self.quiz_question = QUIZ_OPTIONS[(self.current_building + self.friendship) % len(QUIZ_OPTIONS)]
        self.quiz_tries_left = 2
        self.screen = "quiz"
        self.inside_building = self.current_building
        self.message = f"You and {friend.name} are talking. Answer this question."
        self.hint = "You get 2 tries. Read carefully."

    def answer_quiz(self, answer_index: int) -> None:
        if self.quiz_friend is None:
            return
        if answer_index == self.quiz_question["correct"]:
            self.friendship += 1
            self.befriended_friends.add(self.quiz_friend.name)
            self.lesson_completed_buildings.add(self.current_building)
            self.friend_inside_by_building[self.current_building] = self.quiz_friend.name
            self.message = f"Correct! {self.quiz_friend.name} is now your friend."
            self.hint = f"{self.quiz_question['fact']} Now you can finish repairing the house."
            self.quiz_friend = None
            self.screen = "playing"
            return
        self.quiz_tries_left -= 1
        if self.quiz_tries_left > 0:
            self.message = f"Not quite. Try again. Tries left: {self.quiz_tries_left}."
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
            clicked_friend = x is not None and y is not None and (x - friend.x) ** 2 + (y - friend.y) ** 2 <= 28 ** 2
            near_ball = (self.ball_x - friend.x) ** 2 + (self.ball_y - friend.y) ** 2 <= FRIEND_DISTANCE ** 2
            if clicked_friend or (x is None and near_ball):
                if not near_ball:
                    self.message = "Move closer to the person first."
                    return True
                if self.has_uncollected_trash():
                    self.message = "Clean all the trash first before talking to friends."
                    return True
                if friend.name != self.current_target_friend_name():
                    self.message = f"You can't talk to {self.friend_display_name(friend)} yet — focus on the current friend."
                    return True
                self.start_conversation(friend)
                return True
        if x is None and y is None:
            self.message = "Move close to a friend before pressing T."
            return True
        return False

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            if self.screen in {"conversation", "riddle"}:
                self.screen = "playing"
                self.in_conversation = False
                self.in_riddle = False
                self.active_conversation_friend = None
            elif self.window is not None:
                self.window.close()
            return

        if self.screen == "conversation":
            if key == arcade.key.SPACE or key == arcade.key.RETURN:
                self.advance_conversation()
            return

        if self.screen == "riddle":
            if key == arcade.key.RETURN:
                self.submit_riddle_guess()
                return
            if key == arcade.key.BACKSPACE:
                self.riddle_guess = self.riddle_guess[:-1]
                return
            if key == arcade.key.SPACE and len(self.riddle_guess) < 20:
                self.riddle_guess += " "
                return
            if arcade.key.A <= key <= arcade.key.Z and len(self.riddle_guess) < 20:
                self.riddle_guess += chr(key).lower()
                return
            return

        if key in (
            arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D,
            arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT,
        ):
            self.keys_down.add(key)
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
                if door_index == self.current_building and not self.has_uncollected_trash():
                    self.enter_house()
                    return
                self.message = "Stand near a repaired door to go inside."
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

        if self.screen in {"complete", "failed", "trash_game_over", "conclusion"}:
            self.reset_round()
        elif self.screen == "intro":
            self.start_game_countdown()
        elif self.screen == "playing" and not self.round_started:
            self.reset_round()

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
                self.start_game_countdown()
            return

        if self.screen == "countdown":
            return

        if self.screen == "conversation":
            self.advance_conversation()
            return

        if self.screen == "riddle":
            # Check hint button
            if 220 <= x <= 420 and 90 <= y <= 125 and self.riddle_hint_shown < 2:
                self.riddle_hint_shown += 1
                data = FRIEND_RIDDLES[self.active_conversation_friend.name]
                self.message = f"Hint: {data['hint_stages'][self.riddle_hint_shown]}"
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
                    is_final_repair = all(r.fixed or r is spot for r in self.repair_spots)
                    if is_final_repair and not self.can_finish_current_house():
                        self.message = "Before finishing, answer a friend's question correctly."
                        self.hint = "Press F to go outside, then press T near a friend."
                        return
                    if self.money < spot.cost:
                        self.message = f"Need ${spot.cost} to {spot.label}. You have ${self.money}."
                        return
                    spot.fixed = True
                    self.money -= spot.cost
                    self.message = f"Spent ${spot.cost} to {spot.label}."
                    if all(r.fixed for r in self.repair_spots):
                        self.finish_repair()
                    return
            return

        if self.screen == "visit":
            for spot in self.interior_spots:
                if spot.fixed:
                    continue
                if (x - spot.x) ** 2 + (y - spot.y) ** 2 <= spot.radius ** 2:
                    if self.money < spot.cost:
                        self.message = f"Need ${spot.cost} to {spot.label}. You have ${self.money}."
                        return
                    spot.fixed = True
                    self.money -= spot.cost
                    self.message = f"Spent ${spot.cost} to {spot.label}."
                    if all(i.fixed for i in self.interior_spots):
                        if self.interior_mode == "repair":
                            self.finish_interior_repair()
                        else:
                            self.finish_interior_upgrade()
                    return
            return

        if self.screen != "playing":
            return

        if self.try_befriend(x, y):
            return

        for trash in list(self.trash_spots):
            if trash.collected:
                continue
            if (x - trash.x) ** 2 + (y - trash.y) ** 2 <= TRASH_CLICK_RADIUS ** 2:
                if (self.ball_x - trash.x) ** 2 + (self.ball_y - trash.y) ** 2 > COLLECT_DISTANCE ** 2:
                    self.message = "Move the ball closer to pick that up."
                    self.hint = "Use WASD or arrow keys to get near the trash, then click it."
                    return
                self.cleaned += 1
                self.money += TRASH_SCORE + self.upgrades
                self.trash_spots.remove(trash)
                if not self.has_uncollected_trash():
                    self.message = f"Outside is clear! Move close to a friend and press T to talk."
                    self.hint = "Press T when near the glowing friend to start a conversation."
                else:
                    remaining = self.uncollected_trash_count()
                    self.message = f"Good! {remaining} trash pile{'s' if remaining != 1 else ''} left. +${TRASH_SCORE + self.upgrades}"
                    self.hint = "Keep collecting! Move close to trash then click it."
                if self.cleaned % 2 == 0:
                    self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
                break

    def get_player_color(self) -> tuple[int, int, int]:
        friendship_ratio = min(self.friendship / 9.0, 1.0)
        if friendship_ratio < 0.25:
            t = friendship_ratio / 0.25
            r = int(30 + (100 - 30) * t)
            g = int(80 + (150 - 80) * t)
            b = int(150 + (180 - 150) * t)
        elif friendship_ratio < 0.5:
            t = (friendship_ratio - 0.25) / 0.25
            r = int(100 + (50 - 100) * t)
            g = int(150 + (180 - 150) * t)
            b = int(180 + (80 - 180) * t)
        elif friendship_ratio < 0.75:
            t = (friendship_ratio - 0.5) / 0.25
            r = int(50 + (220 - 50) * t)
            g = int(180 + (200 - 180) * t)
            b = int(80 + (40 - 80) * t)
        else:
            t = (friendship_ratio - 0.75) / 0.25
            r = int(220 + (255 - 220) * t)
            g = int(200 + (235 - 200) * t)
            b = int(40 + (80 - 40) * t)
        return (r, g, b)

    def draw_ball(self) -> None:
        if self.screen == "playing":
            arcade.draw_circle_outline(self.ball_x, self.ball_y, COLLECT_DISTANCE, (128, 133, 140), 1)
        player_color = self.get_player_color()
        shadow_color = (15, 18, 25, 120)
        arcade.draw_ellipse_filled(self.ball_x, self.ball_y - 18, 28, 6, shadow_color)
        arcade.draw_circle_filled(self.ball_x, self.ball_y + 8, 7, player_color)
        arcade.draw_circle_outline(self.ball_x, self.ball_y + 8, 7, arcade.color.BLACK, 1.5)
        arcade.draw_line(self.ball_x, self.ball_y, self.ball_x, self.ball_y - 10, player_color, 3)
        arcade.draw_line(self.ball_x, self.ball_y - 2, self.ball_x - 8, self.ball_y + 2, player_color, 2.5)
        arcade.draw_line(self.ball_x, self.ball_y - 2, self.ball_x + 8, self.ball_y + 2, player_color, 2.5)
        arcade.draw_line(self.ball_x, self.ball_y - 10, self.ball_x - 5, self.ball_y - 20, player_color, 2.5)
        arcade.draw_line(self.ball_x, self.ball_y - 10, self.ball_x + 5, self.ball_y - 20, player_color, 2.5)
        arcade.draw_circle_filled(self.ball_x - 2, self.ball_y + 10, 1.5, arcade.color.BLACK)
        arcade.draw_circle_filled(self.ball_x + 2, self.ball_y + 10, 1.5, arcade.color.BLACK)

    def draw_trash(self, trash: TrashSpot, pulse: float = 0.0) -> None:
        """Draw trash with a faint glow so it's visible but not overwhelming."""
        if trash.collected:
            return
        x, y = trash.x, trash.y

        # Faint soft glow — subtle, not distracting
        glow_alpha = int(20 + 10 * math.sin(pulse + trash.pulse))
        if glow_alpha > 0:
            arcade.draw_circle_filled(x, y, 30, (255, 220, 80, glow_alpha))
            arcade.draw_circle_outline(x, y, 26, (255, 200, 60, 60), 2)

        if trash.trash_type == "can":
            arcade.draw_lrbt_rectangle_filled(x - 10, x + 10, y - 12, y + 8, (160, 160, 160))
            arcade.draw_lrbt_rectangle_outline(x - 10, x + 10, y - 12, y + 8, arcade.color.BLACK, 2)
            arcade.draw_ellipse_filled(x, y + 10, 22, 6, (130, 130, 130))
            arcade.draw_ellipse_outline(x, y + 10, 22, 6, arcade.color.BLACK, 2)
            arcade.draw_line(x - 8, y, x + 8, y, (100, 100, 100), 2)
            arcade.draw_line(x - 8, y - 6, x + 8, y - 6, (100, 100, 100), 2)
        elif trash.trash_type == "bag":
            points = [(x-12, y-14), (x+12, y-14), (x+15, y+6), (x, y+12), (x-15, y+6)]
            arcade.draw_polygon_filled(points, (90, 90, 90))
            arcade.draw_polygon_outline(points, arcade.color.BLACK, 2)
            arcade.draw_line(x - 6, y - 8, x - 4, y + 4, (60, 60, 60), 1)
            arcade.draw_line(x + 4, y - 10, x + 5, y + 2, (60, 60, 60), 1)
        elif trash.trash_type == "box":
            arcade.draw_lrbt_rectangle_filled(x - 13, x + 13, y - 10, y + 10, (200, 160, 110))
            arcade.draw_lrbt_rectangle_outline(x - 13, x + 13, y - 10, y + 10, arcade.color.BLACK, 2)
            arcade.draw_line(x - 13, y + 2, x + 13, y + 2, (180, 60, 60), 3)
            arcade.draw_line(x - 13, y + 10, x, y + 16, arcade.color.BLACK, 1)
            arcade.draw_line(x + 13, y + 10, x, y + 16, arcade.color.BLACK, 1)
        elif trash.trash_type == "rubble":
            arcade.draw_polygon_filled([(x-14, y-6), (x-8, y-13), (x-2, y-8), (x-8, y+1)], (110, 100, 88))
            arcade.draw_polygon_filled([(x+4, y-11), (x+13, y-8), (x+11, y+3), (x+2, y+2)], (120, 110, 98))
            arcade.draw_polygon_filled([(x-4, y+4), (x+7, y+2), (x+9, y+11), (x, y+13)], (105, 95, 82))
            arcade.draw_line(x - 8, y - 2, x + 4, y + 5, (70, 60, 50), 2)

        # "TRASH" label below
        arcade.draw_text("TRASH", x, y - 30, (255, 120, 50), 9, anchor_x="center", bold=True)

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
            min_y, max_y = HOUSE_BASE_Y + BALL_RADIUS, 385 - BALL_RADIUS
        self.ball_x = max(min_x, min(max_x, self.ball_x))
        self.ball_y = max(min_y, min(max_y, self.ball_y))

    def on_update(self, delta_time: float) -> None:
        self.pulse_time += delta_time * 3.0

        if self.screen == "intro":
            self.intro_time += delta_time
            self.intro_walk_x += 55 * delta_time
            if self.intro_walk_x > 285:
                self.intro_walk_x = 285
            return
        if self.screen == "countdown":
            self.intro_time += delta_time
            self.start_countdown -= delta_time
            if self.start_countdown <= 0:
                self.reset_round()
            return

        self.update_ball(delta_time)

        if self.screen == "dark" and self.reached_entrance():
            self.screen = "game_over"
            self.game_over_ready = True
            self.keys_down.clear()
            return

        if self.screen != "playing":
            return

        if not self.has_uncollected_trash():
            return

        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.fail_round()

    def start_game_countdown(self) -> None:
        self.screen = "countdown"
        self.round_started = False
        self.keys_down.clear()
        self.start_countdown = 3.0
        self.message = "Get ready."

    def draw_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (18, 22, 32))
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 120, (31, 38, 36))
        arcade.draw_circle_filled(95, 525, 34, (132, 126, 108))
        arcade.draw_circle_filled(140, 535, 24, (112, 108, 98))
        arcade.draw_circle_filled(700, 525, 22, (76, 86, 102))
        arcade.draw_circle_filled(735, 545, 30, (92, 96, 104))
        arcade.draw_line(0, 120, 800, 120, (49, 58, 55), 2)

    def draw_friend_character(self, friend: FriendNPC, x: float, y: float, highlight: bool = False,
                               show_line: bool = True, name_override: str | None = None,
                               line_override: str | None = None) -> None:
        """Draw a grounded stick-figure friend."""
        friend_color = (118, 139, 129) if friend.name in self.befriended_friends else (86, 104, 123)
        if highlight:
            friend_color = (214, 181, 95)
            # Glow rings
            arcade.draw_circle_filled(x, y + 28, 36, (255, 235, 150, 60))
            arcade.draw_circle_outline(x, y + 28, 28, arcade.color.GOLD, 3)

        # Shadow on ground
        arcade.draw_ellipse_filled(x, y - 2, 28, 6, (15, 18, 25, 120))

        # Legs (start from feet at y, go up to body center at y+18)
        arcade.draw_line(x - 5, y, x, y + 18, arcade.color.BLACK, 3)
        arcade.draw_line(x + 5, y, x, y + 18, arcade.color.BLACK, 3)
        # Body
        arcade.draw_line(x, y + 18, x, y + 36, arcade.color.BLACK, 5)
        # Arms
        arcade.draw_line(x, y + 28, x - 12, y + 20, arcade.color.BLACK, 3)
        arcade.draw_line(x, y + 28, x + 12, y + 20, arcade.color.BLACK, 3)
        # Head
        arcade.draw_circle_filled(x, y + 44, 14, friend_color)
        arcade.draw_circle_outline(x, y + 44, 14, arcade.color.BLACK, 2)
        if highlight:
            arcade.draw_circle_outline(x, y + 44, 19, arcade.color.GOLD, 2)

        # Name above head
        arcade.draw_text(name_override or friend.name, x, y + 62, arcade.color.WHITE, 11, anchor_x="center")
        if show_line:
            arcade.draw_text(
                line_override or self.friend_label_text(friend),
                x, y - 22, arcade.color.LIGHT_GRAY, 9,
                width=120, align="center", anchor_x="center",
            )

    def draw_building(self, left: float, right: float, base_y: float, height: float,
                       roof_color, wall_color, repaired: bool = False) -> None:
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
            arcade.draw_lrbt_rectangle_filled(left + 10, left + 24, base_y + 18, top - 20, (35, 36, 42, 110))
            arcade.draw_lrbt_rectangle_filled(right - 34, right - 18, base_y + 35, top - 45, (36, 36, 41, 95))
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
            arcade.draw_lrbt_rectangle_filled(window_left, window_right, window_bottom, window_top, arcade.color.LIGHT_STEEL_BLUE)
            arcade.draw_lrbt_rectangle_outline(window_left, window_right, window_bottom, window_top, arcade.color.BLACK)
            if repaired:
                arcade.draw_line(center_x, window_bottom, center_x, window_top, arcade.color.WHITE, 2)
                arcade.draw_line(window_left, window_bottom + window_height / 2, window_right, window_bottom + window_height / 2, arcade.color.WHITE, 2)

    def draw_building_decay(self, left: float, right: float, base_y: float, height: float) -> None:
        rng = random.Random(f"decay_{int(left)}_{int(right)}")
        top = base_y + height
        vine_x_start = left + 10
        for _ in range(rng.randint(2, 4)):
            vine_y = top - rng.randint(20, height - 40)
            vine_length = rng.randint(40, 100)
            cx, cy = vine_x_start, vine_y
            for _ in range(int(vine_length / 5)):
                nx = cx + rng.randint(-3, 8)
                ny = cy - rng.randint(3, 8)
                arcade.draw_line(cx, cy, nx, ny, (60, 100, 40), 2)
                cx, cy = nx, ny
        vine_x_start = right - 10
        for _ in range(rng.randint(2, 4)):
            vine_y = top - rng.randint(20, height - 40)
            vine_length = rng.randint(40, 100)
            cx, cy = vine_x_start, vine_y
            for _ in range(int(vine_length / 5)):
                nx = cx + rng.randint(-8, 3)
                ny = cy - rng.randint(3, 8)
                arcade.draw_line(cx, cy, nx, ny, (60, 100, 40), 2)
                cx, cy = nx, ny

    def draw_scene(self) -> None:
        self.draw_background()
        player_building_idx = int(self.ball_x / HOUSE_SPACING)
        for building_idx in range(player_building_idx - 3, player_building_idx + 4):
            left, right, base_y, height = self.get_house_position(building_idx)
            roof_color, wall_color = self.get_house_colors(building_idx)
            repaired = building_idx in self.house_styles
            self.draw_building(left, right, base_y, height, roof_color, wall_color, repaired)
            if not repaired:
                self.draw_building_decay(left, right, base_y, height)
            door_width = 34
            door_height = 68
            door_center = (left + right) / 2
            door_left = door_center - door_width / 2
            door_right = door_center + door_width / 2
            door_color = (96, 66, 48) if repaired else (45, 36, 34)
            arcade.draw_lrbt_rectangle_filled(door_left, door_right, base_y, base_y + door_height, door_color)
            arcade.draw_lrbt_rectangle_outline(door_left, door_right, base_y, base_y + door_height, arcade.color.BLACK, 2)
            arcade.draw_circle_filled(door_right - 8, base_y + 34, 3, (150, 132, 82))
            if building_idx in self.house_styles:
                door_label = "F: go inside"
            elif building_idx == self.current_building and not self.has_uncollected_trash():
                door_label = "F: open door"
            else:
                door_label = ""
            if door_label:
                arcade.draw_text(door_label, door_center, base_y + door_height + 10, (222, 222, 214), 10, anchor_x="center")

        # Ground
        arcade.draw_lrbt_rectangle_filled(0, 10000, 0, HOUSE_BASE_Y, (31, 38, 36))
        arcade.draw_line(0, HOUSE_BASE_Y, 10000, HOUSE_BASE_Y, (49, 58, 55), 2)

        # Trash — draw with pulse animation
        for trash in self.trash_spots:
            self.draw_trash(trash, self.pulse_time)

        # Friends — grounded
        target_name = self.current_target_friend_name() if not self.has_uncollected_trash() else ""
        for friend in self.friends:
            is_highlighted = (not self.has_uncollected_trash() and friend.name == target_name
                              and friend.name not in self.befriended_friends)
            self.draw_friend_character(
                friend, friend.x, friend.y,
                highlight=is_highlighted,
                name_override=self.friend_display_name(friend),
            )

        self.draw_ball()

        # "COLLECT TRASH!" sign if trash is left
        if self.has_uncollected_trash():
            arcade.draw_lrbt_rectangle_filled(260, 540, 420, 448, (200, 60, 60, 200))
            arcade.draw_text(f"COLLECT ALL TRASH! ({self.uncollected_trash_count()} left)",
                             400, 426, arcade.color.WHITE, 14, anchor_x="center", bold=True)

    def draw_conversation(self) -> None:
        """Draw the life-conversation between player and friend."""
        if self.active_conversation_friend is None:
            return
        friend = self.active_conversation_friend
        data = FRIEND_RIDDLES[friend.name]
        convo = data["conversation"]
        step = min(self.conversation_step, len(convo) - 1)
        speaker, line = convo[step]

        self.draw_background()
        # Dark panel
        arcade.draw_lrbt_rectangle_filled(60, 740, 90, 500, (15, 18, 28))
        arcade.draw_lrbt_rectangle_outline(60, 740, 90, 500, (180, 160, 100), 3)

        arcade.draw_text("A Conversation", 400, 460, arcade.color.GOLD, 22, anchor_x="center")

        # Draw friend character in scene
        is_player = speaker == "You"
        if is_player:
            arcade.draw_text("[You]", 400, 410, (160, 220, 180), 16, anchor_x="center", bold=True)
        else:
            arcade.draw_text(f"[{friend.name}]", 400, 410, (220, 180, 120), 16, anchor_x="center", bold=True)
            self.draw_friend_character(friend, 200, 200, highlight=False, show_line=False, name_override="???")

        # Speech bubble
        arcade.draw_lrbt_rectangle_filled(120, 680, 240, 380, (30, 35, 50))
        arcade.draw_lrbt_rectangle_outline(120, 680, 240, 380, (180, 160, 100), 2)
        arcade.draw_text(
            f'"{line}"',
            400, 300, arcade.color.WHITE, 15,
            width=520, multiline=True, anchor_x="center", align="center",
        )

        # Progress
        arcade.draw_text(f"({step + 1}/{len(convo)})", 400, 210, (120, 120, 140), 12, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(220, 580, 108, 140, (40, 90, 60))
        arcade.draw_lrbt_rectangle_outline(220, 580, 108, 140, arcade.color.WHITE, 2)
        arcade.draw_text("SPACE or CLICK to continue", 400, 116, arcade.color.WHITE, 14, anchor_x="center")

    def draw_riddle(self) -> None:
        """Draw the name-riddle screen."""
        if self.active_conversation_friend is None:
            return
        friend = self.active_conversation_friend
        data = FRIEND_RIDDLES[friend.name]

        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(60, 740, 60, 540, (15, 18, 28))
        arcade.draw_lrbt_rectangle_outline(60, 740, 60, 540, arcade.color.GOLD, 3)

        arcade.draw_text("Guess My Name!", 400, 498, arcade.color.GOLD, 24, anchor_x="center")
        arcade.draw_text(f"{friend.name[0]}{'_' * (len(friend.name)-1)}  ({len(friend.name)} letters)",
                         400, 468, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

        # Draw friend character
        self.draw_friend_character(friend, 160, 280, highlight=True, show_line=False, name_override="???")

        # Riddle text
        arcade.draw_lrbt_rectangle_filled(220, 700, 290, 450, (25, 28, 42))
        arcade.draw_lrbt_rectangle_outline(220, 700, 290, 450, (120, 120, 160), 2)
        arcade.draw_text(
            data["riddle"],
            460, 430, arcade.color.WHITE, 13,
            width=440, multiline=True, anchor_x="center", align="left",
        )

        # Hint display
        if self.riddle_hint_shown > 0:
            arcade.draw_lrbt_rectangle_filled(220, 700, 240, 290, (40, 50, 30))
            arcade.draw_text(f"Hint: {data['hint_stages'][min(self.riddle_hint_shown, len(data['hint_stages'])-1)]}",
                             460, 258, arcade.color.LIGHT_GREEN, 11, width=440, multiline=True, anchor_x="center")

        # Hint button
        if self.riddle_hint_shown < 2:
            arcade.draw_lrbt_rectangle_filled(220, 420, 90, 128, (60, 50, 30))
            arcade.draw_lrbt_rectangle_outline(220, 420, 90, 128, arcade.color.GOLD, 2)
            arcade.draw_text("Click for Hint", 320, 100, arcade.color.GOLD, 13, anchor_x="center")

        # Input box
        arcade.draw_lrbt_rectangle_filled(430, 700, 90, 128, (35, 45, 60))
        arcade.draw_lrbt_rectangle_outline(430, 700, 90, 128, arcade.color.WHITE, 2)
        display = self.riddle_guess or "type your guess..."
        color = arcade.color.WHITE if self.riddle_guess else (100, 100, 120)
        arcade.draw_text(display, 565, 101, color, 16, anchor_x="center")
        arcade.draw_text("ENTER to guess  |  BACKSPACE to erase", 400, 68, arcade.color.LIGHT_GRAY, 11, anchor_x="center")

        if self.message and "Hint" in self.message:
            arcade.draw_text(self.message, 400, 50, (200, 230, 180), 10, anchor_x="center", width=600)

    def draw_house_interior(self) -> None:
        repaired_inside = self.inside_building in self.inside_repaired_buildings
        upgrade_level = self.interior_upgrade_levels.get(self.inside_building, 0)
        wall_color = (101, 111, 108) if repaired_inside else (68, 65, 76)
        wall_shadow = (79, 86, 84) if repaired_inside else (52, 49, 58)
        floor_color = (98, 76, 54) if repaired_inside else (72, 61, 54)
        rug_color = (142, 96, 78) if repaired_inside else (104, 78, 66)
        wood_color = (96, 66, 48) if repaired_inside else (72, 53, 42)
        accent_color = (222, 222, 214) if repaired_inside else (170, 165, 176)

        # Room backdrop and main shell.
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (22, 21, 29))
        arcade.draw_lrbt_rectangle_filled(90, 710, 120, 470, wall_color)
        arcade.draw_lrbt_rectangle_outline(90, 710, 120, 470, arcade.color.BLACK, 3)
        arcade.draw_lrbt_rectangle_filled(90, 710, 80, 120, floor_color)
        arcade.draw_line(90, 120, 710, 120, arcade.color.BLACK, 3)
        arcade.draw_line(90, 470, 710, 470, wall_shadow, 2)
        arcade.draw_line(90, 120, 90, 470, wall_shadow, 2)
        arcade.draw_line(710, 120, 710, 470, wall_shadow, 2)

        # Ceiling light and warm glow.
        arcade.draw_line(400, 470, 400, 430, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(400, 418, 10, (255, 225, 145))
        arcade.draw_circle_filled(400, 418, 28, (255, 230, 160, 35))
        arcade.draw_circle_filled(400, 418, 58, (255, 240, 190, 14))

        # Window, curtains, and a little outside color.
        arcade.draw_lrbt_rectangle_filled(145, 235, 300, 395, (78, 101, 124))
        arcade.draw_lrbt_rectangle_outline(145, 235, 300, 395, arcade.color.BLACK, 2)
        arcade.draw_line(190, 300, 190, 395, arcade.color.WHITE, 2)
        arcade.draw_line(145, 348, 235, 348, arcade.color.WHITE, 2)
        curtain_color = (112, 58, 65) if repaired_inside else (74, 58, 72)
        arcade.draw_lrbt_rectangle_filled(138, 152, 300, 400, curtain_color)
        arcade.draw_lrbt_rectangle_filled(228, 242, 300, 400, curtain_color)
        arcade.draw_lrbt_rectangle_outline(138, 152, 300, 400, arcade.color.BLACK, 1)
        arcade.draw_lrbt_rectangle_outline(228, 242, 300, 400, arcade.color.BLACK, 1)

        # Main furniture cluster to make the room feel inhabited.
        arcade.draw_lrbt_rectangle_filled(150, 300, 140, 180, rug_color)
        arcade.draw_lrbt_rectangle_outline(150, 300, 140, 180, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(210, 160, 42, (45, 39, 34))
        arcade.draw_circle_filled(208, 166, 34, (171, 144, 108))
        arcade.draw_lrbt_rectangle_filled(165, 255, 180, 222, (104, 78, 60))
        arcade.draw_lrbt_rectangle_outline(165, 255, 180, 222, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(176, 178, 3, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_filled(470, 625, 165, 235, wood_color)
        arcade.draw_lrbt_rectangle_outline(470, 625, 165, 235, arcade.color.BLACK, 2)
        arcade.draw_lrbt_rectangle_filled(490, 530, 235, 285, (92, 62, 46))
        arcade.draw_lrbt_rectangle_outline(490, 530, 235, 285, arcade.color.BLACK, 2)
        arcade.draw_lrbt_rectangle_filled(540, 555, 235, 302, (72, 54, 42))
        arcade.draw_lrbt_rectangle_filled(595, 610, 235, 295, (72, 54, 42))
        arcade.draw_lrbt_rectangle_filled(512, 255, 250, 315, (126, 161, 103))
        arcade.draw_circle_filled(522, 311, 14, (71, 111, 62))
        arcade.draw_circle_filled(533, 325, 10, (83, 128, 71))

        # Wall decor and imperfections.
        arcade.draw_lrbt_rectangle_filled(500, 590, 320, 388, (80, 88, 110))
        arcade.draw_lrbt_rectangle_outline(500, 590, 320, 388, arcade.color.BLACK, 2)
        arcade.draw_line(500, 388, 590, 320, (226, 214, 190), 2)
        arcade.draw_line(500, 320, 590, 388, (226, 214, 190), 2)
        arcade.draw_lrbt_rectangle_filled(630, 682, 300, 372, (102, 78, 62))
        arcade.draw_lrbt_rectangle_outline(630, 682, 300, 372, arcade.color.BLACK, 2)
        arcade.draw_line(642, 360, 670, 360, (170, 150, 120), 2)
        arcade.draw_line(642, 348, 670, 348, (170, 150, 120), 2)
        if not repaired_inside:
            arcade.draw_line(270, 430, 310, 380, arcade.color.BLACK, 3)
            arcade.draw_line(310, 380, 296, 344, arcade.color.BLACK, 2)
            arcade.draw_circle_filled(260, 332, 4, (210, 185, 120))
            arcade.draw_circle_filled(600, 447, 3, (110, 96, 94))
        if upgrade_level >= 1:
            arcade.draw_circle_filled(615, 216, 22, (205, 184, 128))
            arcade.draw_circle_outline(615, 216, 22, arcade.color.BLACK, 2)
            arcade.draw_line(615, 194, 615, 170, arcade.color.BLACK, 2)
        if upgrade_level >= 2:
            arcade.draw_lrbt_rectangle_filled(610, 676, 132, 210, (88, 70, 52))
            arcade.draw_lrbt_rectangle_outline(610, 676, 132, 210, arcade.color.BLACK, 2)
            arcade.draw_line(622, 180, 664, 180, (160, 150, 132), 2)
            arcade.draw_line(622, 164, 664, 164, (160, 150, 132), 2)
        if upgrade_level >= 3 or repaired_inside:
            arcade.draw_lrbt_rectangle_filled(104, 178, 140, 230, (91, 105, 82))
            arcade.draw_circle_filled(118, 168, 8, (74, 118, 64))
            arcade.draw_circle_filled(154, 198, 15, (80, 126, 72))
            arcade.draw_circle_filled(150, 215, 10, (92, 142, 81))
            arcade.draw_lrbt_rectangle_filled(126, 156, 136, 144, (110, 88, 61))
            arcade.draw_lrbt_rectangle_outline(126, 156, 136, 144, arcade.color.BLACK, 1)

        # Ground line and interactive repair targets.
        arcade.draw_circle_filled(425, 195, 4, arcade.color.GOLD)

        interior_spots = self.interior_spots if self.screen == "visit" else self.repair_spots
        for spot in interior_spots:
            if spot.fixed:
                arcade.draw_circle_outline(spot.x, spot.y, 17, arcade.color.DARK_SEA_GREEN, 3)
                arcade.draw_text("fixed", spot.x, spot.y - 5, arcade.color.WHITE, 8, anchor_x="center")
                continue
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius, spot.color, 4)
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius + 3, arcade.color.WHITE, 1)
            arcade.draw_text(f"${spot.cost}", spot.x, spot.y - 5, arcade.color.WHITE, 10, anchor_x="center")
            arcade.draw_text(spot.label, spot.x, spot.y - 20, arcade.color.LIGHT_GRAY, 8, anchor_x="center")

        bname = self.get_building_name(self.inside_building)
        arcade.draw_text(f"Inside {bname}", 400, 488, accent_color, 22, anchor_x="center")
        arcade.draw_text(
            "Cozy details unlock as you repair more of the room.",
            400, 468, arcade.color.LIGHT_GRAY, 10, anchor_x="center",
        )
        self.draw_ball()

    def draw_quiz(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (20, 20, 30))
        arcade.draw_lrbt_rectangle_filled(80, 720, 120, 540, (25, 25, 40))
        arcade.draw_lrbt_rectangle_outline(80, 720, 120, 540, arcade.color.WHITE, 3)
        arcade.draw_text("Community Question", 400, 500, arcade.color.GOLD, 24, anchor_x="center")
        arcade.draw_text(f"Tries left: {self.quiz_tries_left}", 400, 475, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        arcade.draw_text(self.quiz_question["question"], 400, 400, arcade.color.WHITE, 16,
                         width=560, multiline=True, anchor_x="center")
        for index, answer in enumerate(self.quiz_question["answers"]):
            top = 330 - index * 62
            bottom = top - 46
            arcade.draw_lrbt_rectangle_filled(130, 670, bottom, top, (40, 50, 65))
            arcade.draw_lrbt_rectangle_outline(130, 670, bottom, top, arcade.color.WHITE, 2)
            arcade.draw_text(f"{index + 1}. {answer}", 150, bottom + 15, arcade.color.WHITE, 13, width=500)

    def draw_decorate(self) -> None:
        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(80, 720, 120, 540, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(80, 720, 120, 540, arcade.color.WHITE, 3)
        arcade.draw_text("Choose a finished look", 400, 455, (222, 222, 214), 28, anchor_x="center")
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
            arcade.draw_text(f"{index + 1}", mid_x, 365, arcade.color.GOLD, 18, anchor_x="center")
            arcade.draw_text(name, mid_x, 205, (222, 222, 214), 12, anchor_x="center")
        arcade.draw_text("Press 1, 2, or 3", 400, 165, (156, 160, 166), 13, anchor_x="center")

    def draw_intro(self) -> None:
        self.draw_background()
        arcade.draw_text("Neighborhood Cleanup", 400, 505, (222, 222, 214), 32, anchor_x="center", font_name="Georgia")
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
        arcade.draw_ellipse_filled(person_x, 84, 34, 8, (15, 18, 25, 130))
        arcade.draw_line(person_x, 134, person_x, 104, arcade.color.BLACK, 5)
        arcade.draw_line(person_x + 8, 119, person_x + 20, 104, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x - 11, 88, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x + 12, 89, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(person_x, 150, 16, (177, 154, 82))
        arcade.draw_circle_outline(person_x, 150, 16, arcade.color.BLACK, 2)
        if arrived:
            arcade.draw_text("Press START or SPACE", person_x + 60, 214, (222, 222, 214), 13, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(310, 490, 135, 190, (174, 151, 82))
        arcade.draw_lrbt_rectangle_outline(310, 490, 135, 190, arcade.color.BLACK, 3)
        arcade.draw_text("START", 400, 153, arcade.color.BLACK, 22, anchor_x="center")

    def draw_countdown(self) -> None:
        self.draw_intro()
        arcade.draw_lrbt_rectangle_filled(225, 575, 210, 390, (15, 18, 25, 220))
        arcade.draw_lrbt_rectangle_outline(225, 575, 210, 390, arcade.color.WHITE, 3)
        arcade.draw_text("Starting in", 400, 350, arcade.color.LIGHT_GRAY, 18, anchor_x="center")
        arcade.draw_text(f"{math.ceil(self.start_countdown)}", 400, 272, arcade.color.GOLD, 72, anchor_x="center")

    def draw_dark_challenge(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, arcade.color.BLACK)
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 105, (255, 218, 74, 70))
        arcade.draw_circle_filled(self.ball_x, self.ball_y, 58, (255, 226, 91, 115))
        arcade.draw_lrbt_rectangle_filled(
            ENTRANCE_X - ENTRANCE_WIDTH / 2, ENTRANCE_X + ENTRANCE_WIDTH / 2,
            ENTRANCE_Y - ENTRANCE_HEIGHT / 2, ENTRANCE_Y + ENTRANCE_HEIGHT / 2,
            arcade.color.WHITE,
        )
        arcade.draw_text("ENTRANCE", ENTRANCE_X, ENTRANCE_Y - 75, arcade.color.WHITE, 12, anchor_x="center")
        self.draw_ball()
        arcade.draw_text("Find the white entrance.", 400, 548, arcade.color.WHITE, 22, anchor_x="center")

    def draw_game_over(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, arcade.color.BLACK)
        arcade.draw_text("GAME OVER", 400, 330, arcade.color.GOLD, 64, anchor_x="center")
        arcade.draw_text("Press ESC to quit.", 400, 265, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text(self.quiz_question["fact"], 170, 215, arcade.color.LIGHT_GRAY, 13, width=460, multiline=True)

    def draw_trash_game_over(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (20, 20, 30))
        arcade.draw_lrbt_rectangle_filled(150, 650, 180, 450, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(150, 650, 180, 450, arcade.color.WHITE, 3)
        arcade.draw_text("TIME'S UP!", 400, 380, arcade.color.GOLD, 64, anchor_x="center")
        arcade.draw_text("You ran out of time collecting trash.", 400, 310, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Press SPACE to try again or ESC to quit.", 400, 260, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def draw_conclusion(self) -> None:
        self.draw_background()
        arcade.draw_text("One Big House", 400, 510, (242, 242, 232), 34, anchor_x="center")
        arcade.draw_text("All friends together, celebrating what they built.",
                         400, 475, (218, 223, 214), 15, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(105, 695, 108, 442, (93, 102, 100))
        arcade.draw_triangle_filled(85, 442, 715, 442, 400, 540, (61, 48, 42))
        arcade.draw_lrbt_rectangle_filled(305, 495, 108, 238, (71, 52, 41))
        arcade.draw_lrbt_rectangle_outline(305, 495, 108, 238, arcade.color.BLACK, 3)
        celebration_positions = [(210, 190), (400, 205), (590, 185)]
        celebration_lines = ["We fixed it.", "This is home.", "We belong here."]
        for i, name in enumerate(FRIEND_NAMES):
            fx, fy = celebration_positions[i]
            friend_color = (118, 139, 129)
            arcade.draw_ellipse_filled(fx, fy - 2, 26, 6, (15, 18, 25, 120))
            arcade.draw_line(fx - 4, fy, fx, fy + 18, arcade.color.BLACK, 3)
            arcade.draw_line(fx + 4, fy, fx, fy + 18, arcade.color.BLACK, 3)
            arcade.draw_line(fx, fy + 18, fx, fy + 34, arcade.color.BLACK, 5)
            arcade.draw_line(fx, fy + 26, fx - 12, fy + 18, arcade.color.BLACK, 3)
            arcade.draw_line(fx, fy + 26, fx + 12, fy + 18, arcade.color.BLACK, 3)
            arcade.draw_circle_filled(fx, fy + 44, 14, friend_color)
            arcade.draw_circle_outline(fx, fy + 44, 14, arcade.color.BLACK, 2)
            arcade.draw_text(name, fx, fy + 62, arcade.color.WHITE, 11, anchor_x="center")
            arcade.draw_text(celebration_lines[i], fx, fy - 28, arcade.color.LIGHT_GRAY, 9,
                             width=140, align="center", anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(130, 670, 68, 104, (18, 22, 31, 225))
        arcade.draw_text("Press SPACE to play again or ESC to quit.", 400, 78, arcade.color.WHITE, 13, anchor_x="center")

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(10, 790, 492, 590, (14, 17, 24))
        arcade.draw_lrbt_rectangle_outline(10, 790, 492, 590, (126, 132, 142))
        arcade.draw_text("Neighborhood Cleanup", 22, 562, (220, 221, 218), 22)
        arcade.draw_text("ESC quits", 720, 565, (156, 160, 166), 10, anchor_x="center")
        arcade.draw_text(f"Building: {self.get_building_name(self.current_building)}", 22, 538, (156, 160, 166), 12)
        arcade.draw_text(f"Trash: {self.cleaned}", 22, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Money: ${self.money}", 125, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Friendship: {self.friendship}", 240, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Time: {self.time_left:0.1f}s", 650, 516, (214, 215, 212), 12)
        bar_left, bar_right, bar_bottom, bar_top = 22, 778, 500, 508
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
            arcade.draw_text(
                "Move: WASD/arrows  |  Talk to friend: T  |  Enter/leave house: F  |  Quit: ESC\n"
                "Click trash when nearby to collect it. Talk to friends after trash is clear.",
                400, 170, (156, 160, 166), 11, width=420, multiline=True, anchor_x="center"
            )

    def on_draw(self) -> None:
        self.clear()
        if self.camera is not None:
            self.camera.use()

        if self.screen == "intro":
            self.draw_intro()
            return
        if self.screen == "countdown":
            self.draw_countdown()
            return
        if self.screen == "conversation":
            self.draw_conversation()
            return
        if self.screen == "riddle":
            self.draw_riddle()
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
        if self.screen == "conclusion":
            self.draw_conclusion()
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
