import arcade
from photo import PlayerSprite

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Happy Face Game"

# Movement speed
MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    """Main application class for sprite movement."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Create a sprite list
        self.sprite_list = arcade.SpriteList()

        # Create our sprite
        self.player_sprite = None

        # Track which keys are currently pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """Set up the game. Call this function to start a new game."""

        # Create the player sprite
        # Replace "myimage.png" with your actual image filename
        self.player_sprite = PlayerSprite("myimage.png", scale=0.5)

        # Set the sprite's starting position
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        # Add sprite to the list
        self.sprite_list.append(self.player_sprite)

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time):
        """Update game logic."""

        # Update sprite position based on pressed keys
        if self.left_pressed:
            self.player_sprite.center_x -= MOVEMENT_SPEED
        if self.right_pressed:
            self.player_sprite.center_x += MOVEMENT_SPEED
        if self.up_pressed:
            self.player_sprite.center_y += MOVEMENT_SPEED
        if self.down_pressed:
            self.player_sprite.center_y -= MOVEMENT_SPEED

        # Keep sprite on screen
        if self.player_sprite.center_x < 0:
            self.player_sprite.center_x = 0
        elif self.player_sprite.center_x > SCREEN_WIDTH:
            self.player_sprite.center_x = SCREEN_WIDTH

        if self.player_sprite.center_y < 0:
            self.player_sprite.center_y = 0
        elif self.player_sprite.center_y > SCREEN_HEIGHT:
            self.player_sprite.center_y = SCREEN_HEIGHT

    def on_key_press(self, key, modifiers):
        """Handle key presses."""
        if key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """Handle key releases."""
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False


def main():
    """Main function to run the game."""
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
