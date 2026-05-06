"""
Billy Bob Follows Mouse — Python Arcade 3.x
Make sure billybob.png is in the SAME folder as this script.
Run: python billy_bob_follow_mouse.py
"""
 
import arcade
 
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE  = "Billy Bob Follows Mouse"
 
 
class GameWindow(arcade.Window):
 
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
 
        self.sprite_list = arcade.SpriteList()
 
        self.player = arcade.Sprite("billybob.png", scale=0.3)
        self.player.center_x = SCREEN_WIDTH  // 2
        self.player.center_y = SCREEN_HEIGHT // 2
 
        self.sprite_list.append(self.player)
 
    def on_draw(self) -> None:
        self.clear()
        self.sprite_list.draw()
 
        arcade.draw_text(
            "Move your mouse — Billy Bob follows!",
            10, 10,
            arcade.color.DARK_GRAY,
            font_size=13,
        )
 
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.player.center_x = x
        self.player.center_y = y
 
 
def main() -> None:
    window = GameWindow()
    arcade.run()
 
 
if __name__ == "__main__":
    main()