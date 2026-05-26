"""Neighborhood Cleanup: a more detailed MVP for the serious game idea.


The player cleans abandoned buildings, meets friends, earns money, and unlocks
small upgrades that make the neighborhood feel more alive.
"""


from __future__ import annotations


import random
import math
import traceback


import arcade


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Neighborhood Cleanup: South Block"


QUEST_TIME = 4.0
MAX_UPGRADES = 3
MAX_INTERIOR_UPGRADES = 3
TRASH_SCORE = 4
BUILDING_STAGES = 3
BALL_SPEED = 220
BALL_RADIUS = 16
COLLECT_DISTANCE = 70
TRASH_CLICK_RADIUS = 30
FRIEND_DISTANCE = 65
ENTRANCE_X = 720
ENTRANCE_Y = 300
ENTRANCE_WIDTH = 55
ENTRANCE_HEIGHT = 120
HOUSE_SPACING = 240  # Distance between house centers
HOUSE_BASE_Y = 120  # Base Y position for all houses
FRIEND_NAMES = ["Jane", "Billy Bob", "Max"]
HOUSE_WIDTHS = [140, 170, 120]  # Different widths for variety
HOUSE_HEIGHTS = [220, 235, 195]  # Different heights for variety
RIDDLE_QUESTIONS = [
    {
        "question": "I shine at night and guide travelers home. What am I?",
        "answer": "moon",
        "letter": "m",
    },
    {
        "question": "I have pages and stories, and I help you learn. What am I?",
        "answer": "book",
        "letter": "b",
    },
    {
        "question": "I grow tall and have leaves and branches. What am I?",
        "answer": "tree",
        "letter": "t",
    },
    {
        "question": "I can open doors and solve puzzles. What am I?",
        "answer": "key",
        "letter": "k",
    },
]
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
            "Because doing real work together—hammering, planning, deciding—creates genuine friendship and purpose faster than anything else",
            "Because kids should work free and feel grateful for the opportunity",
            "Because it doesn't really matter who does it as long as the work gets done",
        ],
        "correct": 0,
        "fact": "Belonging comes through shared meaningful work. When isolated people work TOGETHER on something real, they go from invisible to valued. The work becomes theirs. The neighborhood becomes theirs.",
    },
    {
        "question": "Some teens live in homes where no one really talks to them. What can a restored community space do?",
        "answers": [
            "Give them a place to be heard, be seen, and find at least one adult or peer who cares about who they really are",
            "Force them to socialize if they don't want to",
            "Replace their family—a building can never be as important as home",
        ],
        "correct": 0,
        "fact": "Many isolated teens don't lack social skills—they lack safe places and caring adults who notice them. A restored house can be the place where that notice happens. One caring adult can change a teen's entire trajectory.",
    },
    {
        "question": "An old building stays abandoned. Over years, what REALLY happens to the teens growing up nearby?",
        "answers": [
            "They internalize the decay—the broken building becomes a symbol that nobody cares about this place or them, deepening their loneliness and hopelessness",
            "It has no effect on them at all—buildings don't matter",
            "They automatically organize and fix it themselves without help",
        ],
        "correct": 0,
        "fact": "Environment shapes psychology. Abandoned buildings signal abandonment to the people living near them. Fixing the building says: 'This place matters. You matter. Someone cares.' This is powerful medicine for lonely teens.",
    },
    {
        "question": "Why do some teens stay silent about feeling alone instead of asking for help?",
        "answers": [
            "They fear judgment, believe no one will understand, or think their pain isn't 'real' enough to bother adults with",
            "They're just lazy and don't care about having friends",
            "Loneliness isn't a real problem—it's just something they'll grow out of",
        ],
        "correct": 0,
        "fact": "Teen silence about loneliness is a survival strategy—they've learned that talking about pain often brings shame instead of help. Safe spaces and trusted adults who ask repeatedly break this silence and save lives.",
    },
    {
        "question": "What's the connection between an abandoned neighborhood and a teen feeling invisible at school?",
        "answers": [
            "Both send the same message: 'You don't matter. Nobody's paying attention. Nobody's coming to help.' Broken places breed broken feelings",
            "They're completely unrelated—environment has nothing to do with how kids feel",
            "Lonely teens just need to move to a nicer neighborhood to feel better",
        ],
        "correct": 0,
        "fact": "Place and psychology are linked. Abandoned buildings and invisible teens exist in the same ecosystem. Healing one—restoring the building—signals to everyone (especially isolated kids) that we care. That we're paying attention.",
    },
    {
        "question": "A group of lonely teens fix up an old house together. What's the most important thing that happens?",
        "answers": [
            "They realize they're not the only ones who feel alone, they become known by each other, and they matter to the people who chose to work beside them",
            "They get paid a lot of money for their work",
            "They become famous on social media for their cleanup efforts",
        ],
        "correct": 0,
        "fact": "Isolation ends when at least one person sees you and says 'I need you. I choose you.' Shared work toward something real is how invisible people become visible. This is how loneliness breaks.",
    },
]




class TrashSpot:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.radius = 18
        self.trash_type = random.choice(["can", "bag", "box", "rubble"])
        self.rotation = random.uniform(0, 360)




class RepairSpot:
    def __init__(self, x: float, y: float, label: str, color, cost: int) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        self.cost = cost
        self.radius = 24
        self.fixed = False


class PipeMinigame:
    """Color rotation puzzle - cycle wall patch colors to match the target."""
    def __init__(self, difficulty: int = 1) -> None:
        self.difficulty = min(difficulty, 3)
        self.grid_size = 3 + self.difficulty
        self.cell_size = 76
        self.start_x = 133
        self.start_y = 110
        self.colors = [
            (176, 106, 82),
            (96, 147, 196),
            (146, 182, 96),
            (214, 173, 89),
            (157, 118, 178),
        ]
        self.target_color = random.choice(self.colors)
        self.grid = self._generate_grid()
        self.time_left = 35
        self.completed = False

    def _generate_grid(self) -> dict:
        """Generate a scrambled starting pattern that can be cycled to one target color."""
        grid = {}
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rng = random.Random(f"pipe_{row}_{col}_{self.difficulty}")
                grid[(row, col)] = rng.choice(self.colors)
        return grid

    def click_pipe(self, x: float, y: float) -> None:
        """Handle a color tile click to cycle it forward."""
        col = max(0, min(self.grid_size - 1, int((x - self.start_x) / self.cell_size)))
        nearest_row = int(round((y - self.start_y - self.cell_size / 2) / self.cell_size))
        row = max(0, min(self.grid_size - 1, nearest_row))

        px = self.start_x + col * self.cell_size
        py = self.start_y + row * self.cell_size
        center_x = px + self.cell_size / 2
        center_y = py + self.cell_size / 2
        y_padding = 36 if row == self.grid_size - 1 else 16
        top_edge_bonus = 12 if row == self.grid_size - 1 else 0
        if abs(x - center_x) > self.cell_size / 2 + 16 or abs(y - center_y) > self.cell_size / 2 + y_padding + top_edge_bonus:
            return

        color = self.grid[(row, col)]
        current_index = self.colors.index(color)
        self.grid[(row, col)] = self.colors[(current_index + 1) % len(self.colors)]
        self.check_completion()

    def check_completion(self) -> bool:
        """Check if the current grid matches the single target color."""
        if all(color == self.target_color for color in self.grid.values()):
            self.completed = True
            return True
        return False

    def update(self, delta_time: float) -> None:
        self.time_left -= delta_time

    def draw(self) -> None:
        arcade.draw_lrbt_rectangle_filled(100, 700, 60, 470, (34, 31, 38))
        arcade.draw_lrbt_rectangle_outline(100, 700, 60, 470, arcade.color.WHITE, 3)

        # Right-side instruction panel
        arcade.draw_lrbt_rectangle_filled(520, 690, 80, 450, (24, 22, 30))
        arcade.draw_lrbt_rectangle_outline(520, 690, 80, 450, arcade.color.WHITE, 2)
        arcade.draw_text("Target color", 605, 418, arcade.color.GOLD, 18, anchor_x="center")
        arcade.draw_circle_filled(605, 394, 10, self.target_color)
        arcade.draw_circle_outline(605, 394, 10, arcade.color.BLACK, 1)
        arcade.draw_text(
            "Click the left grid until every square matches this color.",
            605,
            370,
            arcade.color.LIGHT_GRAY,
            11,
            anchor_x="center",
            width=150,
            align="center",
            multiline=True,
        )
        arcade.draw_text("ESC returns you to the house.", 605, 304, arcade.color.LIGHT_GRAY, 10, anchor_x="center")
        arcade.draw_text(f"Time: {self.time_left:.1f}s", 605, 276, arcade.color.WHITE, 14, anchor_x="center")

        arcade.draw_lrbt_rectangle_outline(self.start_x - 4, self.start_x + self.grid_size * self.cell_size + 4, self.start_y - 4, self.start_y + self.grid_size * self.cell_size + 4, arcade.color.WHITE, 2)
        for (row, col), color in self.grid.items():
            px = self.start_x + col * self.cell_size
            py = self.start_y + row * self.cell_size

            border_color = arcade.color.GOLD if self.grid[(row, col)] == self.target_color else arcade.color.DARK_GRAY
            arcade.draw_lrbt_rectangle_filled(px + 2, px + self.cell_size - 2, py + 2, py + self.cell_size - 2, color)
            arcade.draw_lrbt_rectangle_outline(px, px + self.cell_size, py, py + self.cell_size, border_color, 2)
            arcade.draw_circle_outline(px + self.cell_size / 2, py + self.cell_size / 2, 10, arcade.color.BLACK, 2)
            if self.grid[(row, col)] != self.target_color:
                arcade.draw_line(px + 12, py + 12, px + self.cell_size - 12, py + self.cell_size - 12, arcade.color.BLACK, 2)
                arcade.draw_line(px + 12, py + self.cell_size - 12, px + self.cell_size - 12, py + 12, arcade.color.BLACK, 2)

        if self.completed:
            arcade.draw_text("WALL FIXED!", 205, 52, arcade.color.LIGHT_GREEN, 24, anchor_x="center")
        if self.time_left <= 0 and not self.completed:
            arcade.draw_text("FAILED", 205, 88, arcade.color.RED, 30, anchor_x="center")


class BlockBlastMinigame:
    """Block matching puzzle - clear blocks by clicking groups."""
    def __init__(self, difficulty: int = 1) -> None:
        self.difficulty = min(difficulty, 3)
        self.grid_width = 5
        self.grid_height = 5
        self.cell_size = 70
        self.start_x = 150
        self.start_y = 120
        self.grid = self._generate_grid()
        self.selected_blocks: set = set()
        self.time_left = 30
        self.completed = False
        self.score = 0

    def _generate_grid(self) -> dict:
        """Generate random block grid."""
        colors = [(255, 100, 100), (100, 150, 255), (100, 255, 150), (255, 200, 100)]
        grid = {}

        for row in range(self.grid_height):
            for col in range(self.grid_width):
                rng = random.Random(f"block_{row}_{col}_{self.difficulty}")
                grid[(row, col)] = {"color": colors[(row + col + self.difficulty) % len(colors)], "active": True}

        # Seed a few guaranteed matching clusters so there is always a valid move.
        guaranteed_clusters = [
            [(0, 0), (0, 1)],
            [(2, 2), (2, 3), (3, 2)],
            [(4, 0), (4, 1)],
        ]
        for cluster in guaranteed_clusters:
            cluster_color = colors[random.Random(f"cluster_{cluster[0]}_{self.difficulty}").randrange(len(colors))]
            for pos in cluster:
                if pos in grid:
                    grid[pos]["color"] = cluster_color

        return grid

    def click_block(self, x: float, y: float) -> None:
        """Handle block click to select matching blocks."""
        for (row, col), block in self.grid.items():
            if not block["active"]:
                continue

            bx = self.start_x + col * self.cell_size
            by = self.start_y + row * self.cell_size

            if bx < x < bx + self.cell_size and by < y < by + self.cell_size:
                # Find all connected blocks of same color
                self.selected_blocks = self._find_connected(row, col, block["color"])

                if len(self.selected_blocks) >= 2:
                    # Clear blocks
                    for r, c in self.selected_blocks:
                        self.grid[(r, c)]["active"] = False

                    self.score += len(self.selected_blocks) ** 2
                    self.selected_blocks = set()

                    if self.score >= 15:
                        self.completed = True
                break

    def _find_connected(self, row: int, col: int, color: tuple) -> set:
        """Find all connected blocks of the same color."""
        connected = set()
        visited = set()
        stack = [(row, col)]

        while stack:
            r, c = stack.pop()
            if (r, c) in visited or r < 0 or r >= self.grid_height or c < 0 or c >= self.grid_width:
                continue

            if not self.grid[(r, c)]["active"] or self.grid[(r, c)]["color"] != color:
                continue

            visited.add((r, c))
            connected.add((r, c))

            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((r + dr, c + dc))

        return connected

    def update(self, delta_time: float) -> None:
        self.time_left -= delta_time

    def draw(self) -> None:
        arcade.draw_lrbt_rectangle_filled(100, 700, 80, 500, (30, 30, 40))
        arcade.draw_lrbt_rectangle_outline(100, 700, 80, 500, arcade.color.WHITE, 3)

        arcade.draw_text("Clear the blocks!", 400, 475, arcade.color.GOLD, 18, anchor_x="center")
        arcade.draw_text("Click a group of 2 or more matching colors to clear them.", 400, 448, arcade.color.LIGHT_GRAY, 11, anchor_x="center", width=520, multiline=True)
        arcade.draw_text("ESC returns you to the house.", 400, 425, arcade.color.LIGHT_GRAY, 10, anchor_x="center")
        arcade.draw_text(f"Score: {self.score} | Time: {self.time_left:.1f}s", 400, 410, arcade.color.WHITE, 12, anchor_x="center")

        for (row, col), block in self.grid.items():
            if not block["active"]:
                continue

            bx = self.start_x + col * self.cell_size
            by = self.start_y + row * self.cell_size

            color = block["color"]
            if (row, col) in self.selected_blocks:
                # Brighten selected
                color = tuple(min(c + 80, 255) for c in color)

            arcade.draw_lrbt_rectangle_filled(bx, bx + self.cell_size, by, by + self.cell_size, color)
            arcade.draw_lrbt_rectangle_outline(bx, bx + self.cell_size, by, by + self.cell_size, arcade.color.BLACK, 2)

        if self.completed:
            arcade.draw_text("SUCCESS!", 400, 50, arcade.color.LIGHT_GREEN, 24, anchor_x="center")




class FriendNPC:
    def __init__(self, name: str, x: float, y: float) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.mood = random.choice(["curious", "hopeful", "quiet", "encouraging"])
        self.line = random.choice(
            [
                "I didn't think anyone would come back here.",
                "This place used to feel different.",
                "You're making it easier to stay.",
                "Maybe we can turn this around.",
            ]
        )


class PipePuzzle:
    """Mini-game: Rotate pipes to connect them and fix the house."""
    def __init__(self, difficulty: int = 1) -> None:
        self.grid_size = 3 + difficulty  # 3x3 to 5x5 depending on difficulty
        self.cell_size = 60
        self.pipes: dict[tuple[int, int], int] = {}  # (x, y) -> rotation (0, 90, 180, 270)
        self.start_pos = (0, difficulty // 2)
        self.end_pos = (self.grid_size - 1, difficulty // 2)
        self.moves = 0
        self.max_moves = 15 + (difficulty * 3)
        self.generate_puzzle()

    def generate_puzzle(self) -> None:
        """Generate random pipe layout."""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Start and end pieces are fixed
                if (x, y) == self.start_pos:
                    self.pipes[(x, y)] = 0  # Horizontal entrance
                elif (x, y) == self.end_pos:
                    self.pipes[(x, y)] = 0  # Horizontal exit
                else:
                    # Random rotation for other pipes
                    self.pipes[(x, y)] = random.choice([0, 90, 180, 270])

    def rotate_pipe(self, x: int, y: int) -> None:
        """Rotate a pipe 90 degrees clockwise."""
        if (x, y) not in self.pipes:
            return
        # Don't allow rotating start/end pieces
        if (x, y) in [self.start_pos, self.end_pos]:
            return
        self.pipes[(x, y)] = (self.pipes[(x, y)] + 90) % 360
        self.moves += 1

    def is_solved(self) -> bool:
        """Check if pipes connect from start to end."""
        visited = set()
        current = self.start_pos
        direction = 0  # 0=right, 90=down, 180=left, 270=up

        # Trace path from start
        while current != self.end_pos:
            if current in visited:
                return False  # Loop detected
            visited.add(current)

            x, y = current
            if (x, y) not in self.pipes:
                return False

            pipe_rotation = self.pipes[(x, y)]

            # Determine which directions this pipe connects
            # Pipe at 0° connects left-right, at 90° connects top-bottom, etc.
            # Move in current direction and see if next pipe connects back

            # Calculate next position based on current direction
            if direction == 0:  # Moving right
                next_x, next_y = x + 1, y
            elif direction == 90:  # Moving down
                next_x, next_y = x, y + 1
            elif direction == 180:  # Moving left
                next_x, next_y = x - 1, y
            else:  # Moving up
                next_x, next_y = x, y - 1

            # Check bounds
            if not (0 <= next_x < self.grid_size and 0 <= next_y < self.grid_size):
                return False

            # Simple connection check - pipes must align
            # This is a simplified version; real implementation would be more complex
            if (next_x, next_y) == self.end_pos:
                return True

            current = (next_x, next_y)
            if len(visited) > self.grid_size * self.grid_size:  # Prevent infinite loops
                return False

        return True

    def draw(self, offset_x: float = 150, offset_y: float = 150) -> None:
        """Draw the puzzle grid and pipes."""
        # Draw grid background
        arcade.draw_lrbt_rectangle_filled(
            offset_x, offset_x + self.grid_size * self.cell_size,
            offset_y, offset_y + self.grid_size * self.cell_size,
            (40, 40, 60)
        )
        arcade.draw_lrbt_rectangle_outline(
            offset_x, offset_x + self.grid_size * self.cell_size,
            offset_y, offset_y + self.grid_size * self.cell_size,
            arcade.color.WHITE, 2
        )

        # Draw grid lines
        for i in range(self.grid_size + 1):
            # Vertical lines
            x = offset_x + i * self.cell_size
            arcade.draw_line(x, offset_y, x, offset_y + self.grid_size * self.cell_size, (80, 80, 100), 1)
            # Horizontal lines
            y = offset_y + i * self.cell_size
            arcade.draw_line(offset_x, y, offset_x + self.grid_size * self.cell_size, y, (80, 80, 100), 1)

        # Draw pipes
        for (x, y), rotation in self.pipes.items():
            center_x = offset_x + x * self.cell_size + self.cell_size / 2
            center_y = offset_y + y * self.cell_size + self.cell_size / 2

            # Color for start/end pieces
            if (x, y) == self.start_pos:
                color = arcade.color.GREEN
                arcade.draw_circle_filled(center_x, center_y, 8, color)
                arcade.draw_text("IN", center_x - 8, center_y - 4, arcade.color.WHITE, 8, anchor_x="center")
            elif (x, y) == self.end_pos:
                color = arcade.color.GOLD
                arcade.draw_circle_filled(center_x, center_y, 8, color)
                arcade.draw_text("OUT", center_x - 8, center_y - 4, arcade.color.WHITE, 8, anchor_x="center")
            else:
                color = (100, 150, 200)
                # Draw pipe based on rotation
                if rotation == 0 or rotation == 180:  # Horizontal
                    arcade.draw_line(center_x - 15, center_y, center_x + 15, center_y, color, 4)
                else:  # Vertical
                    arcade.draw_line(center_x, center_y - 15, center_x, center_y + 15, color, 4)

                # Draw rotation indicator
                arcade.draw_circle_outline(center_x, center_y, 12, arcade.color.WHITE, 1)

        # Draw UI
        arcade.draw_text(f"Moves: {self.moves}/{self.max_moves}", offset_x, offset_y - 40, arcade.color.WHITE, 12)
        if self.moves > self.max_moves:
            arcade.draw_text("MOVES EXCEEDED", offset_x + 100, offset_y - 40, arcade.color.RED, 12)

    def get_pipe_at_coords(self, mouse_x: float, mouse_y: float, offset_x: float = 150, offset_y: float = 150) -> tuple[int, int] | None:
        """Get pipe grid coordinates from mouse position."""
        x = int((mouse_x - offset_x) / self.cell_size)
        y = int((mouse_y - offset_y) / self.cell_size)

        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return (x, y)
        return None




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
        self.sky_time = 0.0
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.intro_walk_x = 85.0
        self.intro_time = 0.0
        self.start_countdown = 0.0
        self.keys_down: set[int] = set()
        self.menu_open = False
        self.hud_collapsed = False
        self.quiz_friend: FriendNPC | None = None
        self.guess_friend: FriendNPC | None = None
        self.name_guess = ""
        self.name_riddle_index = 0
        self.name_riddle_progress = ""
        self.name_riddle_tries_left = 3
        self.unlocked_riddle_hints: list[str] = []
        self.quiz_question = QUIZ_OPTIONS[0]
        self.quiz_tries_left = 2
        self.game_over_ready = False
        self.show_instructions = False
        self.door_cooldown = 0.0
        self.exit_spawn_x = 400.0
        self.exit_spawn_y = 300.0
        self.minigame_fail_fade: float | None = None
        # Infinite world state
        self.world_offset_x = 0  # Track camera position in world
        self.house_rng = random.Random(42)  # Seeded for consistent generation
        self.generated_houses: dict[int, tuple[float, float, int, int, tuple, tuple]] = {}  # index -> (left, right, base_y, height, roof_color, wall_color)
        # Mini-game state
        self.active_minigame = None  # None, PipeMinigame, or BlockBlastMinigame
        self.minigame_target_spot = None  # Which repair spot is being worked on
        self.minigame_return_screen = None
        self.minigame_parent_screen = None
        self.configure_camera()


    def get_building_name(self, building_index: int) -> str:
        """Generate a building name based on its index."""
        name_parts = ["North", "South", "East", "West", "Old", "New", "Grand", "Sunny"]
        name_types = ["House", "Building", "Lot", "Flat", "Tower", "Hall"]
        part = name_parts[building_index % len(name_parts)]
        name_type = name_types[(building_index // len(name_parts)) % len(name_types)]
        return f"{part} {name_type}"


    def get_house_position(self, building_index: int) -> tuple[float, float, int, int]:
        """Generate consistent house position and dimensions for given building index."""
        if building_index in self.generated_houses:
            left, right, base_y, height, _, _ = self.generated_houses[building_index]
            return left, right, base_y, height

        # Procedurally generate based on index
        rng = random.Random(f"house_{building_index}")
        center_x = building_index * HOUSE_SPACING + 150
        width = rng.choice(HOUSE_WIDTHS)
        height = rng.choice(HOUSE_HEIGHTS)
        left = center_x - width / 2
        right = center_x + width / 2
        base_y = HOUSE_BASE_Y

        # Roof and wall colors from style options
        style_idx = building_index % 3
        _, roof_color, wall_color = self.style_options[style_idx]

        self.generated_houses[building_index] = (left, right, base_y, height, roof_color, wall_color)
        return left, right, base_y, height


    def get_house_colors(self, building_index: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """Get roof and wall colors for a building."""
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
        self.message = "Click trash piles to clean the building."
        self.hint = "Move the ball close to trash with WASD or arrows, then click to pick it up."
        self.trash_spots = []
        self.friends = []

        # Generate trash for current building
        left, right, base_y, height = self.get_house_position(self.current_building)
        building_center_x = (left + right) / 2

        # Trash positions relative to building center
        relative_positions = [(-45, -40), (-10, -50), (35, -35), (50, -10), (0, 10), (30, 15)]
        for rel_x, rel_y in relative_positions:
            self.trash_spots.append(TrashSpot(building_center_x + rel_x, HOUSE_BASE_Y + 16 + rel_y * 0.15))

        # Place one friend by each house in the block
        self.friends = []
        for building_index, friend_name in enumerate(FRIEND_NAMES):
            house_left, house_right, house_base_y, _ = self.get_house_position(building_index)
            friend_x = house_right + 26
            friend_y = house_base_y + 26
            self.friends.append(FriendNPC(friend_name, friend_x, friend_y))

        # Start at building entrance
        self.ball_x = building_center_x
        self.ball_y = base_y + 50
        self.screen = "playing"
        self.round_started = True


    def door_index_near_player(self) -> int | None:
        # Check buildings within reasonable range of player
        player_building_idx = int(self.ball_x / HOUSE_SPACING)
        for offset in range(-2, 3):  # Check nearby buildings
            index = player_building_idx + offset
            left, right, base_y, _ = self.get_house_position(index)
            door_center = (left + right) / 2
            if abs(self.ball_x - door_center) <= 45 and abs(self.ball_y - (base_y + 34)) <= 62:
                return index
        return None


    def interior_door_near_player(self) -> bool:
        """Return True when the player is close enough to the interior doorway to leave."""
        door_left = 360
        door_right = 440
        door_bottom = 120
        door_top = 260
        padding = 30
        return (
            door_left - padding <= self.ball_x <= door_right + padding
            and door_bottom - padding <= self.ball_y <= door_top + padding
        )


    def enter_house(self) -> None:
        # Generate repair spots procedurally
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
        self.exit_spawn_x = self.ball_x
        self.exit_spawn_y = self.ball_y
        self.time_left = QUEST_TIME
        self.inside_building = self.current_building
        self.screen = "repair"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You enter {self.get_building_name(self.current_building)}. Click each repair spot."
        self.hint = "Repair the damaged wall, floor, window, and doorway details to finish this house."
        self.interior_spots = []


    def visit_house(self, building_index: int) -> None:
        self.time_left = QUEST_TIME
        self.exit_spawn_x = self.ball_x
        self.exit_spawn_y = self.ball_y
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
                for x, y, label, color, cost in INTERIOR_REPAIR_SETS[building_index]
            ]
        self.screen = "visit"
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = f"You went back inside {self.get_building_name(building_index)}."
        if repaired:
            if self.interior_spots:
                self.hint = "Click the upgrade spots to improve the inside, or press F by the door to go back outside."
            else:
                self.hint = "This house is fully upgraded. Press F by the door to go back outside."
        else:
            self.hint = "Click the inside repair spots to fix the room, or press F by the door to go back outside."


    def leave_house(self) -> None:
        if self.menu_open or self.active_minigame is not None:
            return
        self.active_minigame = None
        self.minigame_target_spot = None
        self.minigame_return_screen = None
        self.keys_down.clear()
        self.door_cooldown = 0.9
        self.ball_x = self.exit_spawn_x
        self.ball_y = self.exit_spawn_y
        self.screen = "playing"
        self.round_started = True
        self.message = "You step back outside."
        if self.trash_spots:
            self.hint = "Keep cleaning trash, or visit another finished house."
        else:
            self.hint = "Press F near the current door when you are ready to go inside."


    def cancel_house_minigame(self) -> None:
        """Close the active house mini-game and return to the house interior."""
        self.active_minigame = None
        self.minigame_target_spot = None
        self.minigame_parent_screen = None
        self.minigame_return_screen = None
        self.round_started = False
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.keys_down.clear()
        self.message = "Mini-game closed."
        self.hint = "Pick another repair spot when you're ready."


    def finish_interior_repair(self) -> None:
        self.inside_repaired_buildings.add(self.inside_building)
        self.interior_upgrade_levels.setdefault(self.inside_building, 0)
        self.interior_spots = []
        self.message = f"The inside of {self.get_building_name(self.inside_building)} is fixed."
        # Just continue to decorate screen - no limit on buildings
        self.hint = "Press F by the door to go back outside, then revisit later for interior upgrades."


    def finish_interior_upgrade(self) -> None:
        current_level = self.interior_upgrade_levels.get(self.inside_building, 0)
        next_level = min(MAX_INTERIOR_UPGRADES, current_level + 1)
        self.interior_upgrade_levels[self.inside_building] = next_level
        self.message = f"{self.get_building_name(self.inside_building)} reached interior upgrade tier {next_level}."
        if next_level < MAX_INTERIOR_UPGRADES:
            self.interior_spots = [
                RepairSpot(x, y, label, color, cost)
                for x, y, label, color, cost in INTERIOR_UPGRADE_SETS[next_level]
            ]
            self.hint = "Keep upgrading the inside, or press F by the door to go back outside."
        else:
            self.interior_spots = []
            self.hint = "This house is fully upgraded. Press F by the door to go back outside."


    def can_finish_current_house(self) -> bool:
        return self.current_building in self.lesson_completed_buildings


    def current_target_friend_name(self) -> str:
        return FRIEND_NAMES[self.current_building % len(FRIEND_NAMES)]


    def known_name_letters(self, name: str) -> int:
        return min(len(name), self.friend_name_hints.get(name, 0))


    def name_hint_pattern(self, name: str) -> str:
        return self.scrambled_name_hint(name)


    def scrambled_name_hint(self, name: str) -> str:
        known_letters = self.known_name_letters(name)
        if known_letters <= 0:
            return "".join(" " if char == " " else "_" for char in name)

        letter_positions = [index for index, char in enumerate(name) if char != " "]
        letters = [char for char in name if char != " "]
        rng = random.Random(f"{name}:{known_letters}")
        revealed_letters = letters[:known_letters]
        rng.shuffle(revealed_letters)
        scrambled = [" " if char == " " else "_" for char in name]
        for position, letter in zip(rng.sample(letter_positions, k=min(known_letters, len(letter_positions))), revealed_letters):
            scrambled[position] = letter
        return "".join(scrambled)


    def friend_display_name(self, friend: FriendNPC) -> str:
        if friend.name in self.guessed_friend_names or friend.name in self.befriended_friends:
            return friend.name
        return "???"


    def display_name_from_hint(self, name: str) -> str:
        return self.scrambled_name_hint(name)


    def friend_action_hint(self) -> str:
        if self.screen != "playing":
            return ""
        target_name = self.current_target_friend_name()
        if self.trash_spots:
            return "Clean trash first to reveal riddle clues."
        return "Move close to the next friend and press T to solve the riddles."


    def friend_label_text(self, friend: FriendNPC) -> str:
        if friend.name in self.befriended_friends:
            return "friend"
        if friend.name != self.current_target_friend_name():
            return "not yet"
        if self.known_name_letters(friend.name) < len(friend.name):
            return "find clues"
        if friend.name in self.guessed_friend_names:
            return "quiz time"
        return "Talk"


    def letter_clue(self, letter: str, position: int) -> str:
        if letter == " ":
            return f"spot {position} is a space between two words"


        clue_words = {
            "a": "apple",
            "b": "ball",
            "e": "empty",
            "i": "inside",
            "j": "jump",
            "l": "light",
            "m": "money",
            "n": "neighbor",
            "o": "open",
            "x": "exit",
            "y": "yard",
        }
        word = clue_words.get(letter.lower(), letter.upper())
        return f"letter {position} is the first letter in '{word}'"


    def reveal_friend_name_hint(self) -> str:
        name = self.current_target_friend_name()
        if name not in self.friend_name_hints:
            self.friend_name_hints[name] = 0

        if self.name_riddle_index < len(RIDDLE_QUESTIONS):
            riddle = RIDDLE_QUESTIONS[self.name_riddle_index]
            return f"Riddle clue unlocked: {riddle['question']}"

        return f"All riddle clues are ready for {name}. Move close and press T, or click the friend, to answer them."


    def next_building(self) -> None:
        finished_building = self.get_building_name(self.current_building)
        self.current_building += 1  # Just keep incrementing for infinite houses
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
        self.hint = "Press 1, 2, or 3 to pick a style. The next cleanup starts after your choice."


    def choose_house_style(self, style_index: int) -> None:
        _, roof_color, wall_color = self.style_options[style_index]
        self.house_styles[self.current_building] = (roof_color, wall_color)
        self.next_building()


    def finish_neighborhood(self) -> None:
        self.screen = "conclusion"
        self.round_started = False
        self.keys_down.clear()
        self.ball_x = 400.0
        self.ball_y = 155.0
        self.message = "The neighborhood comes together in one shared home."
        self.hint = "Press SPACE to play again, or ESC to quit."


    def start_game_countdown(self) -> None:
        self.screen = "countdown"
        self.round_started = False
        self.keys_down.clear()
        self.start_countdown = 3.0
        self.message = "Get ready."
        self.hint = "The game starts when the countdown reaches zero."


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
        self.inside_building = self.current_building
        self.message = f"You and {friend.name} are inside the house. Answer their question."
        self.hint = "You get 2 tries. Read the choices carefully before you pick one."


    def start_name_guess(self, friend: FriendNPC) -> None:
        self.guess_friend = friend
        self.name_guess = ""
        self.name_riddle_index = 0
        self.name_riddle_progress = ""
        self.unlocked_riddle_hints = []
        self.screen = "name_guess"
        self.message = f"Riddle 1 of 4 for {friend.name}."
        self.hint = "Answer each riddle to reveal one letter. Press ESC to cancel and go back."


    def cancel_name_guess(self) -> None:
        if self.guess_friend is None:
            return

        friend_name = self.guess_friend.name
        self.guess_friend = None
        self.name_guess = ""
        self.name_riddle_index = 0
        self.name_riddle_progress = ""
        self.screen = "playing"
        self.message = f"You stepped away from {friend_name}'s riddles."
        self.hint = "You can talk to them again when you're ready."


    def submit_name_riddle(self) -> None:
        if self.guess_friend is None:
            return

        riddle = RIDDLE_QUESTIONS[self.name_riddle_index % len(RIDDLE_QUESTIONS)]
        if self.name_guess.strip().lower() == riddle["answer"]:
            self.name_riddle_progress += riddle["letter"]
            self.name_riddle_index += 1
            if riddle["question"] not in self.unlocked_riddle_hints:
                self.unlocked_riddle_hints.append(riddle["question"])
            self.name_guess = ""
            if self.name_riddle_index >= 4:
                friend = self.guess_friend
                self.guessed_friend_names.add(friend.name)
                self.message = f"You revealed {friend.name}."
                self.hint = f"All 4 riddles are complete. {friend.name} is the full name."
                self.guess_friend = None
                self.start_friend_quiz(friend)
                return

            next_riddle = RIDDLE_QUESTIONS[self.name_riddle_index % len(RIDDLE_QUESTIONS)]
            self.message = f"Correct. Letter revealed: {self.name_riddle_progress.upper()}."
            self.hint = f"Riddle {self.name_riddle_index + 1} of 4: {next_riddle['question']}"
            return

        self.name_guess = ""
        self.message = "Not quite. Try that riddle again."
        self.hint = f"Clue: {riddle['question']}"


    def answer_quiz(self, answer_index: int) -> None:
        if self.quiz_friend is None:
            return


        if answer_index == self.quiz_question["correct"]:
            self.friendship += 1
            self.befriended_friends.add(self.quiz_friend.name)
            self.lesson_completed_buildings.add(self.current_building)
            self.friend_inside_by_building[self.current_building] = self.quiz_friend.name
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
                if friend.name not in self.guessed_friend_names:
                    self.start_name_guess(friend)
                    return True


                self.start_friend_quiz(friend)
                return True


        if x is None and y is None:
            self.message = "Move closer to the NPC and press T."
            self.hint = "Pick up trash for hints, then use those hints near other friends."
            return True


        return False


    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            if self.active_minigame is not None:
                self.cancel_house_minigame()
                return
            if self.menu_open:
                self.menu_open = False
                return
            if self.window is not None:
                if self.screen in {"intro", "countdown", "game_over", "trash_game_over", "conclusion"}:
                    self.window.close()
                else:
                    self.menu_open = True
                    self.keys_down.clear()
                    self.message = "Menu opened."
                    self.hint = "Choose restart, intro, or quit."
            return

        if self.menu_open:
            return

        if key == arcade.key.P:
            if self.screen not in {"intro", "countdown", "game_over", "trash_game_over", "conclusion"} and self.active_minigame is None:
                self.menu_open = not self.menu_open
                if self.menu_open:
                    self.keys_down.clear()
                    self.message = "Menu opened."
                    self.hint = "Choose restart, intro, or quit."
            return


        if self.screen == "name_guess":
            if key == arcade.key.ENTER:
                self.submit_name_riddle()
                return
            if key == arcade.key.BACKSPACE:
                self.name_guess = self.name_guess[:-1]
                return
            if key == arcade.key.ESCAPE:
                self.cancel_name_guess()
                return
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


        if key == arcade.key.F:
            if self.door_cooldown > 0:
                return
            if self.screen in {"repair", "visit"}:
                try:
                    self.leave_house()
                except Exception as exc:
                    self.active_minigame = None
                    self.minigame_target_spot = None
                    self.keys_down.clear()
                    self.screen = "playing"
                    self.round_started = True
                    self.message = "You step back outside."
                    self.hint = "The exit glitched, but you are back outside now."
                    print(f"leave_house error: {exc}")
                return
            if self.screen == "playing":
                door_index = self.door_index_near_player()
                if door_index is not None and door_index in self.house_styles:
                    self.visit_house(door_index)
                    return
                if door_index == self.current_building and not self.trash_spots:
                    self.enter_house()
                    return
                self.message = "Stand near the door to enter the house."
                self.hint = "Clear the trash first, then press F by the door."
                return


        if key == arcade.key.T:
            if self.screen == "playing":
                if self.try_befriend():
                    return
                self.message = "Move closer to the NPC to talk."
                self.hint = "Press T near a friend to start the dialogue."
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
            if self.screen in {"complete", "failed", "trash_game_over", "conclusion", "minigame_game_over"}:
                self.reset_round()
            elif self.screen == "intro":
                self.start_game_countdown()
            elif self.screen == "playing" and not self.round_started:
                self.reset_round()
        except Exception as exc:
            self.screen = "failed"
            self.message = f"Start error: {exc!r}"
            raise


    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_down.discard(key)


    def on_text(self, text: str) -> None:
        if self.screen == "name_guess" and text.isalpha() and len(self.name_guess) < 16:
            self.name_guess += text.lower()


    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        screen_x = x
        screen_y = y
        if self.camera is not None:
            world_position = self.camera.unproject((x, y))
            x = world_position.x
            y = world_position.y

        if self.menu_open:
            if 540 <= x <= 720 and 352 <= y <= 400:
                self.reset_round()
                self.menu_open = False
                return
            if 540 <= x <= 720 and 302 <= y <= 348:
                self.menu_open = False
                self.screen = "intro"
                self.intro_time = 0.0
                self.intro_walk_x = 85.0
                self.message = "Press SPACE to begin."
                self.hint = "Clear every trash pile to move to the next building."
                return
            if 540 <= x <= 720 and 252 <= y <= 298:
                if self.window is not None:
                    self.window.close()
                return
            return

        if 10 <= x <= 45 and 18 <= y <= 53:
            self.show_instructions = not self.show_instructions
            return

        if 748 <= x <= 790 and 558 <= y <= 590:
            self.hud_collapsed = not self.hud_collapsed
            return

        if 10 <= x <= 45 and 518 <= y <= 553:
            self.show_instructions = not self.show_instructions
            return

        # Handle mini-game clicks
        if self.active_minigame is not None:
            self.active_minigame.click_pipe(x, y) if isinstance(self.active_minigame, PipeMinigame) else self.active_minigame.click_block(x, y)

            if self.active_minigame.completed:
                # Mini-game won!
                spot = self.minigame_target_spot
                if spot is not None:
                    spot.fixed = True
                    self.money -= spot.cost
                    self.message = f"Repaired: {spot.label}!"
                    self.hint = "Great work! Continue with the other repairs."
                else:
                    self.message = "Repair complete."
                    self.hint = "Great work! Continue with the other repairs."

                self.active_minigame = None
                self.minigame_target_spot = None
                self.minigame_parent_screen = None

                # Check if all repairs done
                if self.screen == "repair" and all(repair.fixed for repair in self.repair_spots):
                    self.finish_repair()
                elif self.screen == "visit" and all(interior.fixed for interior in self.interior_spots):
                    if self.interior_mode == "repair":
                        self.finish_interior_repair()
                    else:
                        self.finish_interior_upgrade()

            return

        if screen_y >= 492:
            return


        if self.screen == "intro":
            if 310 <= x <= 490 and 135 <= y <= 190:
                self.start_game_countdown()
            return


        if self.screen == "countdown":
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


        if self.screen == "name_guess":
            return


        if self.screen == "repair":
            for spot in self.repair_spots:
                if spot.fixed:
                    continue
                if (x - spot.x) ** 2 + (y - spot.y) ** 2 <= spot.radius ** 2:
                    is_final_repair = all(repair.fixed or repair is spot for repair in self.repair_spots)
                    if is_final_repair and not self.can_finish_current_house():
                        self.message = "Before finishing the house, answer a friend's question correctly."
                        self.hint = f"Press F to go outside, then press T near {FRIEND_NAMES[0]} to learn the lesson."
                        return
                    if self.money < spot.cost:
                        self.message = f"Need ${spot.cost} to {spot.label}. You have ${self.money}."
                        self.hint = "Trash gives you repair money. Clean outside piles before fixing everything."
                        return

                    # Launch mini-game instead of instant completion
                    self.minigame_target_spot = spot
                    self.minigame_return_screen = "repair"
                    self.minigame_parent_screen = "repair"
                    repair_type = spot.label.lower()

                    # Choose mini-game based on repair type
                    self.active_minigame = PipeMinigame(difficulty=self.current_building // 5 + 1)
                    self.message = "Match the wall colors to repair the hole!"
                    self.hint = "Click any tile to cycle its color until the whole patch matches."

                    self.hint = "Complete the mini-game to finish this repair!"
                    return
            return


        if self.screen == "visit":
            for spot in self.interior_spots:
                if spot.fixed:
                    continue
                if (x - spot.x) ** 2 + (y - spot.y) ** 2 <= spot.radius ** 2:
                    try:
                        if self.money < spot.cost:
                            self.message = f"Need ${spot.cost} to {spot.label}. You have ${self.money}."
                            self.hint = "Clean more trash outside to earn repair money."
                            return

                        # Launch mini-game for interior work too
                        self.minigame_target_spot = spot
                        self.minigame_return_screen = "visit"
                        self.minigame_parent_screen = "visit"
                        self.active_minigame = PipeMinigame(difficulty=self.current_building // 5 + 1)
                        self.message = "Match the wall colors to repair the inside!"
                        self.hint = "Click any tile to cycle its color until the whole patch matches."
                        return
                    except Exception as exc:
                        self.active_minigame = None
                        self.minigame_target_spot = None
                        self.minigame_return_screen = None
                        self.message = "That spot glitched instead of opening."
                        self.hint = "Try another spot, or press F to leave and come back."
                        print(f"Interior click error on {spot.label}: {exc}")
                        return
            return


        if self.screen in {"repair", "visit"}:
            if 360 <= x <= 440 and 120 <= y <= 260:
                self.leave_house()
                return
            return


        if self.screen != "playing":
            return


        if self.try_befriend(x, y):
            return


        for trash in list(self.trash_spots):
            if (x - trash.x) ** 2 + (y - trash.y) ** 2 <= TRASH_CLICK_RADIUS ** 2:
                if (self.ball_x - trash.x) ** 2 + (self.ball_y - trash.y) ** 2 > COLLECT_DISTANCE ** 2:
                    self.message = "Move the ball closer to pick that up."
                    self.hint = "Use WASD or arrow keys to get near the trash, then click it."
                    return


                self.trash_spots.remove(trash)
                self.cleaned += 1
                self.money += TRASH_SCORE + self.upgrades
                self.message = self.reveal_friend_name_hint()
                self.hint = "Each trash pickup unlocks another riddle clue."
                if self.cleaned % 2 == 0:
                    self.neighborhood_state = min(BUILDING_STAGES - 1, self.neighborhood_state + 1)
                if not self.trash_spots:
                    target_name = self.current_target_friend_name()
                    if self.known_name_letters(target_name) >= len(target_name):
                        self.message = "The outside is clear, and the name clues are complete."
                        self.hint = "Move close to the person and press T, or click them, then type the full name."
                    else:
                        self.message = "The outside is clear. Press F to open the door."
                        self.hint = "You can open the door, but you need the full friend name before the quiz."
                break


    def get_player_color(self) -> tuple[int, int, int]:
        """Calculate player color based on friendship level (blue when lonely, bright yellow when connected)."""
        # Friendship ranges from 0 to ~9 (3 friends * 3 interactions each)
        # Map friendship to a color gradient: blue -> cyan -> green -> yellow -> bright yellow
        friendship_ratio = min(self.friendship / 9.0, 1.0)  # Normalize to 0-1

        if friendship_ratio < 0.25:
            # Dark blue to cyan
            t = friendship_ratio / 0.25
            r = int(30 + (100 - 30) * t)
            g = int(80 + (150 - 80) * t)
            b = int(150 + (180 - 150) * t)
        elif friendship_ratio < 0.5:
            # Cyan to green
            t = (friendship_ratio - 0.25) / 0.25
            r = int(100 + (50 - 100) * t)
            g = int(150 + (180 - 150) * t)
            b = int(180 + (80 - 180) * t)
        elif friendship_ratio < 0.75:
            # Green to yellow
            t = (friendship_ratio - 0.5) / 0.25
            r = int(50 + (220 - 50) * t)
            g = int(180 + (200 - 180) * t)
            b = int(80 + (40 - 80) * t)
        else:
            # Yellow to bright golden yellow
            t = (friendship_ratio - 0.75) / 0.25
            r = int(220 + (255 - 220) * t)
            g = int(200 + (235 - 200) * t)
            b = int(40 + (80 - 40) * t)

        return (r, g, b)


    def draw_ball(self) -> None:
        """Draw stick figure player that changes color with friendship."""
        if self.screen == "playing":
            arcade.draw_circle_outline(self.ball_x, self.ball_y, COLLECT_DISTANCE, (128, 133, 140), 1)

        player_color = self.get_player_color()
        shadow_color = (15, 18, 25, 120)

        # Shadow
        arcade.draw_ellipse_filled(self.ball_x, self.ball_y - 18, 28, 6, shadow_color)

        # Head
        arcade.draw_circle_filled(self.ball_x, self.ball_y + 8, 7, player_color)
        arcade.draw_circle_outline(self.ball_x, self.ball_y + 8, 7, arcade.color.BLACK, 1.5)

        # Body (vertical line)
        arcade.draw_line(self.ball_x, self.ball_y, self.ball_x, self.ball_y - 10, player_color, 3)

        # Left arm
        arcade.draw_line(self.ball_x, self.ball_y - 2, self.ball_x - 8, self.ball_y + 2, player_color, 2.5)

        # Right arm
        arcade.draw_line(self.ball_x, self.ball_y - 2, self.ball_x + 8, self.ball_y + 2, player_color, 2.5)

        # Left leg
        arcade.draw_line(self.ball_x, self.ball_y - 10, self.ball_x - 5, self.ball_y - 20, player_color, 2.5)

        # Right leg
        arcade.draw_line(self.ball_x, self.ball_y - 10, self.ball_x + 5, self.ball_y - 20, player_color, 2.5)

        # Eyes (simple dots)
        eye_offset_x = 2
        eye_offset_y = 2
        arcade.draw_circle_filled(self.ball_x - eye_offset_x, self.ball_y + 10, 1.5, arcade.color.BLACK)
        arcade.draw_circle_filled(self.ball_x + eye_offset_x, self.ball_y + 10, 1.5, arcade.color.BLACK)


    def draw_trash(self, trash: TrashSpot) -> None:
        """Draw detailed trash objects instead of simple circles."""
        x, y = trash.x, trash.y
        glow_color = (255, 240, 170, 35)
        arcade.draw_circle_filled(x, y, 24, glow_color)

        if trash.trash_type == "can":
            # Draw a trash can
            arcade.draw_lrbt_rectangle_filled(x - 10, x + 10, y - 14, y + 8, (120, 120, 120))
            arcade.draw_lrbt_rectangle_outline(x - 10, x + 10, y - 14, y + 8, arcade.color.BLACK, 2)
            # Lid
            arcade.draw_circle_filled(x, y + 10, 11, (100, 100, 100))
            arcade.draw_circle_outline(x, y + 10, 11, arcade.color.BLACK, 1)
            # Dents
            arcade.draw_circle_outline(x - 6, y - 2, 3, arcade.color.BLACK, 1)
            arcade.draw_circle_outline(x + 5, y + 2, 3, arcade.color.BLACK, 1)

        elif trash.trash_type == "bag":
            # Draw a garbage bag
            points = [
                (x - 12, y - 16),
                (x + 12, y - 16),
                (x + 14, y + 6),
                (x, y + 10),
                (x - 14, y + 6),
            ]
            arcade.draw_polygon_filled(points, (80, 80, 80))
            arcade.draw_polygon_outline(points, arcade.color.BLACK, 2)
            # Wrinkles in bag
            arcade.draw_line(x - 8, y - 10, x - 6, y + 4, (60, 60, 60), 1)
            arcade.draw_line(x + 4, y - 12, x + 6, y + 2, (60, 60, 60), 1)
            arcade.draw_line(x - 2, y - 14, x, y + 3, (60, 60, 60), 1)

        elif trash.trash_type == "box":
            # Draw a cardboard box
            arcade.draw_lrbt_rectangle_filled(x - 12, x + 12, y - 10, y + 10, (180, 140, 100))
            arcade.draw_lrbt_rectangle_outline(x - 12, x + 12, y - 10, y + 10, arcade.color.BLACK, 2)
            # Tape
            arcade.draw_line(x - 12, y + 2, x + 12, y + 2, (180, 50, 50), 3)
            # Flaps
            arcade.draw_line(x - 12, y + 10, x, y + 15, arcade.color.BLACK, 1)
            arcade.draw_line(x + 12, y + 10, x, y + 15, arcade.color.BLACK, 1)

        elif trash.trash_type == "rubble":
            # Draw scattered rubble/debris
            arcade.draw_polygon_filled(
                [(x - 14, y - 6), (x - 8, y - 12), (x - 2, y - 8), (x - 8, y)],
                (100, 90, 80)
            )
            arcade.draw_polygon_filled(
                [(x + 4, y - 10), (x + 12, y - 8), (x + 10, y + 2), (x + 2, y + 1)],
                (110, 100, 90)
            )
            arcade.draw_polygon_filled(
                [(x - 4, y + 4), (x + 6, y + 2), (x + 8, y + 10), (x, y + 12)],
                (95, 85, 75)
            )
            # Cracks
            arcade.draw_line(x - 8, y - 2, x + 4, y + 4, (60, 50, 40), 1)


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
        try:
            self.sky_time += delta_time
            if self.door_cooldown > 0:
                self.door_cooldown = max(0.0, self.door_cooldown - delta_time)

            if self.minigame_fail_fade is not None:
                self.minigame_fail_fade = max(0.0, self.minigame_fail_fade - delta_time * 0.9)
                if self.minigame_fail_fade <= 0:
                    self.minigame_fail_fade = None
                    self.screen = "minigame_game_over"
                    self.keys_down.clear()
                    self.message = "FAILED"
                    self.hint = "You ran out of time. Press SPACE to try again."
                return

            if self.menu_open and self.screen not in {"intro", "countdown"}:
                return

            # Handle mini-game updates
            if self.active_minigame is not None:
                self.active_minigame.update(delta_time)

                # Check if mini-game timed out
                if self.active_minigame.time_left <= 0:
                    self.message = "FAILED"
                    self.hint = "Time ran out."
                    self.active_minigame = None
                    self.minigame_target_spot = None
                    self.minigame_return_screen = None
                    self.minigame_parent_screen = None
                    self.minigame_fail_fade = 1.0
                return

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
                    self.start_countdown = 0
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


            if not self.trash_spots:
                return


            self.time_left -= delta_time
            if self.time_left <= 0:
                self.time_left = 0
                self.fail_round()
        except Exception:
            traceback.print_exc()
            self.active_minigame = None
            self.minigame_target_spot = None
            self.message = "A game error happened, but the window stayed open."
            self.hint = "Check the terminal traceback, then click again or press ESC."


    def draw_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (18, 22, 32))
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 120, (31, 38, 36))

        self.draw_clouds()

        arcade.draw_circle_filled(95, 525, 34, (132, 126, 108))
        arcade.draw_circle_filled(140, 535, 24, (112, 108, 98))
        arcade.draw_circle_filled(700, 525, 22, (76, 86, 102))
        arcade.draw_circle_filled(735, 545, 30, (92, 96, 104))
        arcade.draw_line(0, 120, 800, 120, (49, 58, 55), 2)


    def draw_clouds(self) -> None:
        cloud_sets = [
            (100, 555, 0.0, 1.15),
            (340, 565, 1.7, 1.0),
            (600, 548, 3.2, 1.1),
            (760, 560, 4.6, 0.9),
        ]
        for base_x, base_y, phase, scale in cloud_sets:
            drift_x = (self.sky_time * 10 * scale + phase * 40) % 920 - 60
            x = base_x + drift_x
            y = base_y
            cloud_color = (244, 246, 250, 140)
            shadow_color = (244, 246, 250, 80)
            arcade.draw_circle_filled(x, y, 22 * scale, cloud_color)
            arcade.draw_circle_filled(x + 18 * scale, y + 8, 28 * scale, cloud_color)
            arcade.draw_circle_filled(x + 40 * scale, y + 2, 20 * scale, cloud_color)
            arcade.draw_ellipse_filled(x + 20 * scale, y - 5, 68 * scale, 20 * scale, shadow_color)


    def draw_friend_character(
        self,
        friend: FriendNPC,
        x: float,
        y: float,
        highlight: bool = False,
        show_line: bool = True,
        name_override: str | None = None,
        line_override: str | None = None,
    ) -> None:
        friend_color = (118, 139, 129) if friend.name in self.befriended_friends else (86, 104, 123)
        if highlight:
            friend_color = (214, 181, 95)
            arcade.draw_circle_filled(x, y + 36, 22, (255, 235, 150, 90))
            arcade.draw_circle_outline(x, y + 36, 24, arcade.color.GOLD, 3)

        arcade.draw_ellipse_filled(x, y - 16, 28, 7, (15, 18, 25, 120))
        arcade.draw_line(x, y + 28, x, y - 2, arcade.color.BLACK, 5)
        arcade.draw_line(x + 8, y + 13, x + 24, y + 31, arcade.color.BLACK, 3)
        arcade.draw_line(x, y + 13, x - 12, y - 2, arcade.color.BLACK, 3)
        arcade.draw_line(x, y - 2, x - 10, y - 18, arcade.color.BLACK, 3)
        arcade.draw_line(x, y - 2, x + 10, y - 18, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(x, y + 32, 16, friend_color)
        arcade.draw_circle_outline(x, y + 32, 16, arcade.color.BLACK, 2)
        if highlight:
            arcade.draw_circle_outline(x, y + 32, 18, arcade.color.GOLD, 2)
        arcade.draw_text(name_override or friend.name, x, y + 58, arcade.color.WHITE, 11, anchor_x="center")
        if show_line:
            arcade.draw_text(
                line_override or friend.line,
                x,
                y - 42,
                arcade.color.LIGHT_GRAY,
                9,
                width=120,
                align="center",
                anchor_x="center",
            )


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

        # Draw visible buildings (determine which ones are on screen)
        player_building_idx = int(self.ball_x / HOUSE_SPACING)

        # Draw buildings in a range around the player
        for building_idx in range(player_building_idx - 3, player_building_idx + 4):
            left, right, base_y, height = self.get_house_position(building_idx)
            roof_color, wall_color = self.get_house_colors(building_idx)
            repaired = building_idx in self.house_styles

            self.draw_building(left, right, base_y, height, roof_color, wall_color, repaired)

            # Draw vines and overgrowth on unrepaired buildings
            if not repaired:
                self.draw_building_decay(left, right, base_y, height)

            # Draw door
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
                arcade.draw_lrbt_rectangle_filled(door_left - 5, door_right + 5, base_y + 8, base_y + 15, (31, 30, 32))

            if building_idx in self.house_styles:
                door_label = "Press F to go inside"
            elif building_idx == self.current_building and not self.trash_spots:
                door_label = "Press F to open door"
            else:
                door_label = ""
            if door_label:
                arcade.draw_text(door_label, door_center, base_y + door_height + 10, (222, 222, 214), 10, anchor_x="center")

        # Draw ground
        arcade.draw_lrbt_rectangle_filled(0, 10000, 0, HOUSE_BASE_Y, (31, 38, 36))
        arcade.draw_line(0, HOUSE_BASE_Y, 10000, HOUSE_BASE_Y, (49, 58, 55), 2)

        # Draw trash
        for trash in self.trash_spots:
            self.draw_trash(trash)

        # Draw friends
        for friend in self.friends:
            is_highlighted = self.quiz_friend is not None and friend.name == self.quiz_friend.name
            self.draw_friend_character(
                friend, friend.x, friend.y,
                highlight=is_highlighted,
                name_override=self.friend_display_name(friend),
                line_override=self.friend_label_text(friend),
            )

        self.draw_ball()


    def draw_building_decay(self, left: float, right: float, base_y: float, height: float) -> None:
        """Draw vines, overgrowth, and decay on unrepaired buildings."""
        rng = random.Random(f"decay_{int(left)}_{int(right)}")
        top = base_y + height

        # Random vines on left side
        vine_x_start = left + 10
        num_vines = rng.randint(2, 4)
        for i in range(num_vines):
            vine_y = top - rng.randint(20, height - 40)
            vine_length = rng.randint(40, 100)
            # Draw vine as wavy line
            current_y = vine_y
            current_x = vine_x_start
            for _ in range(int(vine_length / 5)):
                next_x = current_x + rng.randint(-3, 8)
                next_y = current_y - rng.randint(3, 8)
                arcade.draw_line(current_x, current_y, next_x, next_y, (60, 100, 40), 2)
                current_x = next_x
                current_y = next_y

        # Random vines on right side
        vine_x_start = right - 10
        num_vines = rng.randint(2, 4)
        for i in range(num_vines):
            vine_y = top - rng.randint(20, height - 40)
            vine_length = rng.randint(40, 100)
            current_y = vine_y
            current_x = vine_x_start
            for _ in range(int(vine_length / 5)):
                next_x = current_x + rng.randint(-8, 3)
                next_y = current_y - rng.randint(3, 8)
                arcade.draw_line(current_x, current_y, next_x, next_y, (60, 100, 40), 2)
                current_x = next_x
                current_y = next_y

        # Dead leaves/debris at base
        for _ in range(rng.randint(5, 12)):
            leaf_x = left + rng.randint(0, int(right - left))
            leaf_y = base_y + rng.randint(0, 30)
            leaf_size = rng.randint(2, 5)
            arcade.draw_polygon_filled(
                [(leaf_x, leaf_y), (leaf_x + leaf_size, leaf_y + leaf_size), (leaf_x + leaf_size * 2, leaf_y), (leaf_x + leaf_size, leaf_y - leaf_size)],
                (95, 120, 45)
            )


    def draw_house_interior(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (25, 24, 31))
        self.draw_clouds()
        repaired_inside = self.inside_building in self.inside_repaired_buildings
        upgrade_level = self.interior_upgrade_levels.get(self.inside_building, 0)
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


        room_friend_name = self.friend_inside_by_building.get(self.inside_building)
        if room_friend_name is not None:
            room_friend = next((friend for friend in self.friends if friend.name == room_friend_name), None)
            if room_friend is not None:
                self.draw_friend_character(
                    room_friend,
                    625,
                    292,
                    highlight=False,
                    show_line=False,
                    name_override=room_friend.name,
                )


        if repaired_inside:
            arcade.draw_lrbt_rectangle_filled(130, 710, 410, 426, (222, 222, 214))
            arcade.draw_lrbt_rectangle_filled(115, 165, 120, 132, (54, 88, 60))
            arcade.draw_lrbt_rectangle_filled(630, 685, 120, 132, (54, 88, 60))
            arcade.draw_circle_filled(140, 140, 8, (185, 148, 84))
            arcade.draw_circle_filled(660, 140, 8, (185, 148, 84))
            if upgrade_level >= 1:
                arcade.draw_lrbt_rectangle_filled(140, 230, 150, 182, (92, 74, 61))
                arcade.draw_lrbt_rectangle_outline(140, 230, 150, 182, arcade.color.BLACK, 2)
                arcade.draw_circle_filled(175, 190, 13, (154, 186, 120))
            if upgrade_level >= 2:
                arcade.draw_lrbt_rectangle_filled(520, 650, 155, 210, (58, 76, 88))
                arcade.draw_lrbt_rectangle_outline(520, 650, 155, 210, arcade.color.BLACK, 2)
                arcade.draw_lrbt_rectangle_filled(545, 620, 148, 155, (219, 206, 170))
                arcade.draw_line(545, 155, 545, 148, arcade.color.BLACK, 2)
                arcade.draw_line(590, 155, 590, 148, arcade.color.BLACK, 2)
            if upgrade_level >= 3:
                arcade.draw_lrbt_rectangle_filled(320, 485, 280, 304, (206, 192, 164))
                arcade.draw_lrbt_rectangle_outline(320, 485, 280, 304, arcade.color.BLACK, 2)
                arcade.draw_line(343, 304, 462, 304, arcade.color.BLACK, 2)
                arcade.draw_circle_filled(355, 318, 7, arcade.color.GOLD)
                arcade.draw_circle_filled(450, 318, 7, arcade.color.GOLD)
        else:
            arcade.draw_line(145, 285, 188, 260, arcade.color.BLACK, 2)
            arcade.draw_line(188, 260, 177, 235, arcade.color.BLACK, 2)
            arcade.draw_line(500, 285, 540, 260, arcade.color.BLACK, 2)
            arcade.draw_line(540, 260, 560, 290, arcade.color.BLACK, 2)
            arcade.draw_line(245, 121, 305, 105, arcade.color.BLACK, 2)
            arcade.draw_line(305, 105, 358, 118, arcade.color.BLACK, 2)
            arcade.draw_line(460, 116, 520, 101, arcade.color.BLACK, 2)
            arcade.draw_line(358, 284, 383, 266, arcade.color.BLACK, 2)
            arcade.draw_line(383, 266, 405, 275, arcade.color.BLACK, 2)
            arcade.draw_line(405, 275, 432, 252, arcade.color.BLACK, 2)
            arcade.draw_line(432, 252, 461, 260, arcade.color.BLACK, 2)
            arcade.draw_line(461, 260, 486, 238, arcade.color.BLACK, 2)
            arcade.draw_line(392, 308, 414, 292, arcade.color.BLACK, 2)
            arcade.draw_line(414, 292, 442, 298, arcade.color.BLACK, 2)


        if self.screen == "visit":
            if repaired_inside:
                if upgrade_level < MAX_INTERIOR_UPGRADES:
                    arcade.draw_text(
                        f"Upgrade tier {upgrade_level}/{MAX_INTERIOR_UPGRADES}. Click the glow spots to improve it.",
                        400,
                        458,
                        arcade.color.LIGHT_GRAY,
                        12,
                        anchor_x="center",
                    )
                else:
                    arcade.draw_text("The inside is fully upgraded.", 400, 458, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
            else:
                arcade.draw_text("Click the inside repair spots to finish this room.", 400, 458, arcade.color.LIGHT_GRAY, 12, anchor_x="center")


        interior_spots = self.interior_spots if self.screen == "visit" else self.repair_spots
        for spot in interior_spots:
            if spot.fixed:
                arcade.draw_circle_filled(spot.x, spot.y, spot.radius + 1, wall_color)
                arcade.draw_circle_outline(spot.x, spot.y, spot.radius + 1, wall_color, 2)
                continue

            arcade.draw_circle_filled(spot.x, spot.y, spot.radius + 2, (194, 191, 177, 120))
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius + 2, spot.color, 3)
            arcade.draw_circle_outline(spot.x, spot.y, spot.radius + 5, arcade.color.WHITE, 1)
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
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (20, 20, 30))

        # Overlay panel
        arcade.draw_lrbt_rectangle_filled(80, 720, 120, 540, (25, 25, 40))
        arcade.draw_lrbt_rectangle_outline(80, 720, 120, 540, arcade.color.WHITE, 3)

        arcade.draw_text("Community Question", 400, 500, arcade.color.GOLD, 24, anchor_x="center")
        arcade.draw_text(f"Tries left: {self.quiz_tries_left}", 400, 475, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        arcade.draw_text("Answer carefully.", 400, 455, arcade.color.LIGHT_GRAY, 11, anchor_x="center")


        arcade.draw_text(
            self.quiz_question["question"],
            400,
            400,
            arcade.color.WHITE,
            16,
            width=560,
            multiline=True,
            anchor_x="center",
        )


        for index, answer in enumerate(self.quiz_question["answers"]):
            top = 330 - index * 62
            bottom = top - 46
            # Answer button background
            arcade.draw_lrbt_rectangle_filled(130, 670, bottom, top, (40, 50, 65))
            arcade.draw_lrbt_rectangle_outline(130, 670, bottom, top, arcade.color.WHITE, 2)
            arcade.draw_text(f"{index + 1}. {answer}", 150, bottom + 15, arcade.color.WHITE, 13, width=500)


    def draw_name_guess(self) -> None:
        self.draw_background()

        arcade.draw_lrbt_rectangle_filled(120, 680, 180, 430, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(120, 680, 180, 430, arcade.color.WHITE, 3)
        arcade.draw_text("Riddle Name Challenge", 400, 382, arcade.color.GOLD, 26, anchor_x="center")
        if self.guess_friend is not None:
            riddle = RIDDLE_QUESTIONS[self.name_riddle_index % len(RIDDLE_QUESTIONS)]
            arcade.draw_text(f"Riddle {self.name_riddle_index + 1} of 4:", 400, 326, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
            arcade.draw_text(riddle["question"], 400, 302, arcade.color.LIGHT_GRAY, 12, anchor_x="center", width=500, multiline=True)
        arcade.draw_lrbt_rectangle_filled(210, 590, 265, 315, (40, 50, 65))
        arcade.draw_lrbt_rectangle_outline(210, 590, 265, 315, arcade.color.LIGHT_GRAY, 2)
        arcade.draw_text(self.name_guess or "type your answer here", 400, 282, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text(f"Letters found: {self.name_riddle_progress.upper() or '-'}", 400, 244, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        arcade.draw_text("ENTER submits     BACKSPACE erases     ESC backs out", 400, 220, arcade.color.LIGHT_GRAY, 12, anchor_x="center")
        arcade.draw_text(f"Hint: {self.hint}", 400, 200, arcade.color.LIGHT_GRAY, 10, anchor_x="center", width=500, multiline=True)
        arcade.draw_text("Solve 4 riddles to reveal the name.", 400, 196, arcade.color.LIGHT_GRAY, 11, anchor_x="center")

        arcade.draw_lrbt_rectangle_filled(620, 760, 180, 430, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(620, 760, 180, 430, arcade.color.WHITE, 3)
        arcade.draw_text("Unlocked Hints", 690, 382, arcade.color.GOLD, 18, anchor_x="center")
        if self.trash_spots:
            arcade.draw_text("Clear all trash to unlock the hint list.", 690, 345, arcade.color.LIGHT_GRAY, 11, width=118, multiline=True, anchor_x="center")
        else:
            if self.unlocked_riddle_hints:
                y = 340
                for i, clue in enumerate(self.unlocked_riddle_hints[-4:]):
                    arcade.draw_text(f"{i + 1}. {clue}", 632, y, arcade.color.LIGHT_GRAY, 10, width=110, multiline=True)
                    y -= 58
            else:
                arcade.draw_text("No hints unlocked yet.", 690, 330, arcade.color.LIGHT_GRAY, 11, anchor_x="center")


    def draw_decorate(self) -> None:
        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(80, 720, 120, 540, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(80, 720, 120, 540, arcade.color.WHITE, 3)

        arcade.draw_text("Choose a finished look", 400, 455, (222, 222, 214), 28, anchor_x="center")
        arcade.draw_text(
            self.get_building_name(self.current_building),
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
        arcade.draw_text("Alone", 400, 505, (222, 222, 214), 36, anchor_x="center", font_name="Georgia")


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
        arcade.draw_line(person_x, 134, person_x, 104, arcade.color.BLACK, 5)
        if arrived:
            arcade.draw_line(person_x + 8, 119, person_x + 28, 144 + wave, arcade.color.BLACK, 3)
            arcade.draw_circle_filled(person_x + 31, 147 + wave, 4, (177, 154, 82))
            arcade.draw_text("Press START", person_x + 80, 214, (222, 222, 214), 13, anchor_x="center")
        else:
            arcade.draw_line(person_x + 8, 119, person_x + 20, 104, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x - 11, 88, arcade.color.BLACK, 3)
        arcade.draw_line(person_x, 104, person_x + 12, 89, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(person_x, 150, 16, (177, 154, 82))
        arcade.draw_circle_outline(person_x, 150, 16, arcade.color.BLACK, 2)


        arcade.draw_lrbt_rectangle_filled(310, 490, 135, 190, (174, 151, 82))
        arcade.draw_lrbt_rectangle_outline(310, 490, 135, 190, arcade.color.BLACK, 3)
        arcade.draw_text("START", 400, 153, arcade.color.BLACK, 22, anchor_x="center")


    def draw_countdown(self) -> None:
        self.draw_intro()
        arcade.draw_lrbt_rectangle_filled(225, 575, 210, 390, (15, 18, 25, 220))
        arcade.draw_lrbt_rectangle_outline(225, 575, 210, 390, arcade.color.WHITE, 3)
        arcade.draw_text("Starting in", 400, 350, arcade.color.LIGHT_GRAY, 18, anchor_x="center")
        arcade.draw_text(f"{math.ceil(self.start_countdown)}", 400, 272, arcade.color.GOLD, 72, anchor_x="center")
        arcade.draw_text("Get ready to clean the block.", 400, 228, arcade.color.WHITE, 14, anchor_x="center")


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
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (20, 20, 30))
        arcade.draw_lrbt_rectangle_filled(150, 650, 180, 450, (20, 20, 30))
        arcade.draw_lrbt_rectangle_outline(150, 650, 180, 450, arcade.color.WHITE, 3)
        arcade.draw_text("GAME OVER", 400, 380, arcade.color.GOLD, 64, anchor_x="center")
        arcade.draw_text("You ran out of time picking up trash.", 400, 310, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Press SPACE to try again or ESC to quit.", 400, 260, arcade.color.LIGHT_GRAY, 14, anchor_x="center")


    def draw_conclusion(self) -> None:
        self.draw_background()
        arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (26, 38, 33))
        arcade.draw_circle_filled(105, 520, 46, (168, 198, 142, 120))
        arcade.draw_circle_filled(705, 525, 38, (148, 186, 163, 110))
        arcade.draw_circle_filled(400, 548, 64, (216, 224, 170, 80))
        arcade.draw_circle_filled(388, 540, 14, (255, 232, 148, 140))


        arcade.draw_text("One Big House", 400, 510, (242, 242, 232), 34, anchor_x="center")
        arcade.draw_text(
            "All of the friends are together in one home, celebrating what they built.",
            400,
            475,
            (218, 223, 214),
            15,
            anchor_x="center",
        )


        house_left = 105
        house_right = 695
        house_base = 108
        house_top = 442
        roof_peak_x = 400
        roof_peak_y = 540
        wall_color = (93, 102, 100)
        roof_color = (61, 48, 42)
        arcade.draw_lrbt_rectangle_filled(house_left, house_right, house_base, house_top, wall_color)
        arcade.draw_lrbt_rectangle_outline(house_left, house_right, house_base, house_top, arcade.color.BLACK, 3)
        arcade.draw_triangle_filled(house_left - 20, house_top, house_right + 20, house_top, roof_peak_x, roof_peak_y, roof_color)
        arcade.draw_triangle_outline(house_left - 20, house_top, house_right + 20, house_top, roof_peak_x, roof_peak_y, arcade.color.BLACK)
        arcade.draw_line(house_left + 14, house_top - 10, house_right - 14, house_top - 10, (222, 222, 214), 3)


        arcade.draw_lrbt_rectangle_filled(305, 495, 108, 238, (71, 52, 41))
        arcade.draw_lrbt_rectangle_outline(305, 495, 108, 238, arcade.color.BLACK, 3)
        arcade.draw_circle_filled(470, 178, 4, (185, 148, 84))
        arcade.draw_lrbt_rectangle_filled(333, 467, 126, 208, (222, 222, 214))
        arcade.draw_lrbt_rectangle_outline(333, 467, 126, 208, arcade.color.BLACK, 2)
        arcade.draw_line(400, 126, 400, 208, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(456, 168, 3, (185, 148, 84))
        arcade.draw_circle_filled(344, 168, 3, (185, 148, 84))


        room_color = (184, 165, 128)
        floor_color = (110, 79, 58)
        arcade.draw_lrbt_rectangle_filled(128, 672, 114, 180, floor_color)
        arcade.draw_lrbt_rectangle_filled(128, 672, 180, 424, room_color)
        arcade.draw_lrbt_rectangle_outline(128, 672, 114, 424, arcade.color.BLACK, 2)
        arcade.draw_line(128, 180, 672, 180, arcade.color.BLACK, 2)
        arcade.draw_line(400, 114, 400, 180, arcade.color.BLACK, 2)


        arcade.draw_lrbt_rectangle_filled(160, 275, 250, 372, (74, 86, 97))
        arcade.draw_lrbt_rectangle_outline(160, 275, 250, 372, arcade.color.BLACK, 2)
        arcade.draw_text("shared table", 217, 214, arcade.color.LIGHT_GRAY, 10, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(525, 620, 244, 312, (156, 176, 188))
        arcade.draw_lrbt_rectangle_outline(525, 620, 244, 312, arcade.color.BLACK, 2)
        arcade.draw_text("music", 572, 210, arcade.color.LIGHT_GRAY, 10, anchor_x="center")
        arcade.draw_lrbt_rectangle_filled(310, 490, 258, 290, (214, 200, 152))
        arcade.draw_lrbt_rectangle_outline(310, 490, 258, 290, arcade.color.BLACK, 2)
        arcade.draw_text("snacks", 400, 297, arcade.color.BLACK, 10, anchor_x="center")


        celebration_positions = [(210, 210), (400, 225), (590, 205)]
        celebration_lines = [
            "We fixed it together.",
            "This place feels like home.",
            "Everybody belongs here.",
        ]
        for index, name in enumerate(FRIEND_NAMES):
            fx, fy = celebration_positions[index]
            friend_color = (118, 139, 129)
            arcade.draw_ellipse_filled(fx, fy - 16, 32, 8, (15, 18, 25, 120))
            arcade.draw_line(fx, fy + 32, fx, fy + 2, arcade.color.BLACK, 5)
            arcade.draw_line(fx + 8, fy + 17, fx + 24, fy + 34, arcade.color.BLACK, 3)
            arcade.draw_line(fx, fy + 17, fx - 12, fy + 2, arcade.color.BLACK, 3)
            arcade.draw_line(fx, fy + 2, fx - 10, fy - 16, arcade.color.BLACK, 3)
            arcade.draw_line(fx, fy + 2, fx + 10, fy - 16, arcade.color.BLACK, 3)
            arcade.draw_circle_filled(fx, fy + 36, 16, friend_color)
            arcade.draw_circle_outline(fx, fy + 36, 16, arcade.color.BLACK, 2)
            arcade.draw_text(name, fx, fy + 60, arcade.color.WHITE, 11, anchor_x="center")
            arcade.draw_text(celebration_lines[index], fx, fy - 46, arcade.color.LIGHT_GRAY, 9, width=140, align="center", anchor_x="center")
            arcade.draw_line(fx - 10, fy + 48, fx + 10, fy + 60, arcade.color.GOLD, 2)
            arcade.draw_line(fx - 8, fy + 58, fx + 12, fy + 66, arcade.color.GOLD, 2)


        confetti = [
            (180, 468, arcade.color.GOLD),
            (250, 492, arcade.color.LIGHT_BLUE),
            (322, 455, arcade.color.DARK_SEA_GREEN),
            (407, 500, arcade.color.CORAL),
            (478, 472, arcade.color.LIGHT_STEEL_BLUE),
            (565, 487, arcade.color.YELLOW_ORANGE),
            (625, 458, arcade.color.PASTEL_PINK),
        ]
        for x, y, color in confetti:
            arcade.draw_circle_filled(x, y, 4, color)
            arcade.draw_line(x - 3, y - 5, x + 3, y + 5, color, 2)


        arcade.draw_lrbt_rectangle_filled(130, 670, 68, 104, (18, 22, 31, 225))
        arcade.draw_lrbt_rectangle_outline(130, 670, 68, 104, arcade.color.WHITE, 2)
        arcade.draw_text("One big house. All of the friends together.", 400, 86, arcade.color.WHITE, 13, anchor_x="center")
        arcade.draw_text("Press SPACE to play again or ESC to quit.", 400, 68, arcade.color.LIGHT_GRAY, 11, anchor_x="center")


    def draw_hud(self) -> None:
        if self.hud_collapsed:
            arcade.draw_lrbt_rectangle_filled(728, 790, 548, 590, (14, 17, 24))
            arcade.draw_lrbt_rectangle_outline(728, 790, 548, 590, (126, 132, 142))
            arcade.draw_line(742, 575, 776, 575, (222, 222, 214), 2)
            arcade.draw_line(742, 566, 776, 566, (222, 222, 214), 2)
            arcade.draw_line(742, 557, 776, 557, (222, 222, 214), 2)
            return

        arcade.draw_lrbt_rectangle_filled(10, 790, 492, 590, (14, 17, 24))
        arcade.draw_lrbt_rectangle_outline(10, 790, 492, 590, (126, 132, 142))

        current_house_label = f"{self.get_building_name(self.current_building)}"
        arcade.draw_text(current_house_label, 22, 562, (220, 221, 218), 22)
        arcade.draw_text("ESC quits", 720, 565, (156, 160, 166), 10, anchor_x="center")
        arcade.draw_text(f"Building: {self.get_building_name(self.current_building)}", 22, 538, (156, 160, 166), 12)
        arcade.draw_text(f"Trash: {self.cleaned}", 22, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Money: ${self.money}", 125, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Friendship: {self.friendship}", 240, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Riddles: {self.name_riddle_progress.upper() or '-'}", 390, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Upgrades: {self.upgrades}/{MAX_UPGRADES}", 500, 516, (214, 215, 212), 12)
        arcade.draw_text(f"Time: {self.time_left:0.1f}s", 650, 516, (214, 215, 212), 12)
        fixed_count = sum(1 for repair in self.repair_spots if repair.fixed)
        repair_total = len(self.repair_spots)
        if self.screen == "repair" and repair_total:
            arcade.draw_text(f"Repairs: {fixed_count}/{repair_total}", 260, 538, (156, 160, 166), 12)
        elif self.screen == "visit":
            upgrade_level = self.interior_upgrade_levels.get(self.inside_building, 0)
            arcade.draw_text(
                f"Interior upgrades: {upgrade_level}/{MAX_INTERIOR_UPGRADES}",
                260,
                538,
                (156, 160, 166),
                12,
            )
        else:
            current_house_number = min(self.buildings_cleaned + 1, BUILDING_STAGES)
            arcade.draw_text(
                f"House: {current_house_number}/{BUILDING_STAGES}",
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

        if self.menu_open:
            arcade.draw_lrbt_rectangle_filled(490, 770, 220, 430, (14, 17, 24, 240))
            arcade.draw_lrbt_rectangle_outline(490, 770, 220, 430, (222, 222, 214), 2)
            arcade.draw_text("Menu", 630, 398, arcade.color.GOLD, 24, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(560, 700, 360, 396, (40, 50, 65))
            arcade.draw_lrbt_rectangle_outline(560, 700, 360, 396, arcade.color.WHITE, 2)
            arcade.draw_text("Restart Game", 630, 378, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(560, 700, 310, 346, (40, 50, 65))
            arcade.draw_lrbt_rectangle_outline(560, 700, 310, 346, arcade.color.WHITE, 2)
            arcade.draw_text("Back to Intro", 630, 328, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(560, 700, 260, 296, (40, 50, 65))
            arcade.draw_lrbt_rectangle_outline(560, 700, 260, 296, arcade.color.WHITE, 2)
            arcade.draw_text("Quit Game", 630, 278, arcade.color.WHITE, 14, anchor_x="center")

        if self.show_instructions:
            arcade.draw_lrbt_rectangle_filled(175, 625, 112, 248, (14, 17, 24))
            arcade.draw_lrbt_rectangle_outline(175, 625, 112, 248, (222, 222, 214), 2)
            arcade.draw_text("Instructions", 400, 220, (222, 222, 214), 18, anchor_x="center")
            arcade.draw_text(self.hint, 198, 188, (156, 160, 166), 11, width=404, multiline=True)
            arcade.draw_text(
                "Move: WASD/arrows   Talk: T   Door/leave: F   Menu: ESC   Help: ?",
                400,
                132,
                (156, 160, 166),
                10,
                anchor_x="center",
            )

        if self.menu_open and self.screen not in {"intro", "countdown", "game_over", "trash_game_over", "conclusion"}:
            arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (0, 0, 0, 110))




    def on_draw(self) -> None:
        try:
            self.clear()
            if self.camera is not None:
                self.camera.use()

            # Draw mini-games on top of everything
            if self.active_minigame is not None:
                if isinstance(self.active_minigame, PipeMinigame):
                    self.active_minigame.draw()
                elif isinstance(self.active_minigame, BlockBlastMinigame):
                    self.active_minigame.draw()
                return

            if self.screen == "minigame_game_over":
                self.draw_scene()
                arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (0, 0, 0, 220))
                arcade.draw_text("FAILED", 400, 320, arcade.color.RED, 52, anchor_x="center")
                arcade.draw_text("Press SPACE to try again", 400, 258, arcade.color.WHITE, 18, anchor_x="center")
                return

            if self.minigame_fail_fade is not None:
                self.draw_scene()
                fade_alpha = int(220 * (1.0 - self.minigame_fail_fade))
                arcade.draw_lrbt_rectangle_filled(0, 800, 0, 600, (0, 0, 0, max(0, min(220, fade_alpha))))
                arcade.draw_text("FAILED", 400, 320, arcade.color.RED, 52, anchor_x="center")
                arcade.draw_text("Press SPACE to try again", 400, 258, arcade.color.WHITE, 18, anchor_x="center")
                return

            if self.screen == "intro":
                self.draw_intro()
                return


            if self.screen == "countdown":
                self.draw_countdown()
                return


            if self.screen == "quiz":
                self.draw_quiz()
                return


            if self.screen == "name_guess":
                self.draw_name_guess()
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
        except Exception:
            traceback.print_exc()
            self.active_minigame = None
            self.minigame_target_spot = None




def main() -> None:
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
    view = GameView(window)
    window.show_view(view)
    arcade.run()




if __name__ == "__main__":
    main()
