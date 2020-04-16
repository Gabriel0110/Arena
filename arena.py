import arcade
import random
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Arena"

class Arena(arcade.Window):

    def __init__(self, width, height, title):
        """Initialize the game
        """
        super().__init__(width, height, title)

        # Set up the empty sprite lists
        self.enemies_list = arcade.SpriteList()
        self.bullets_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        self.player_velocity = 15

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = True

    def setup(self):
        """Get the game ready to play
        """

        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        self.player = arcade.Sprite("images/player_sprite.png", 0.25)
        self.player.center_y = self.height/2
        self.player.left = self.width/2
        self.all_sprites.append(self.player)

        # Spawn a new enemy every 0.5 seconds
        arcade.schedule(self.add_enemy, 0.5)

    def on_update(self, delta_time: float):
        """Update the positions and statuses of all game objects
        If paused, do nothing

        Arguments:
            delta_time {float} -- Time since the last update
        """

        # If paused, don't update anything
        if self.paused:
            return

        # Did you hit an enemy?
        if self.player.collides_with_list(self.enemies_list):
            if not self.GOD_MODE:
                arcade.close_window()

        # Update everything
        self.all_sprites.update()

        # Keep the player on screen
        if self.player.top > self.height:
            self.player.top = self.height
        if self.player.right > self.width:
            self.player.right = self.width
        if self.player.bottom < 0:
            self.player.bottom = 0
        if self.player.left < 0:
            self.player.left = 0

    def on_draw(self):
        """Draw all game objects
        """
        # Begin rendering (will end automatically after method ends)
        arcade.start_render()

        # Draw scoreboard text
        self.score_text = arcade.draw_text("SCORE: {}".format(str(self.score)), self.width/2 - 75, self.height - 35, arcade.color.BLACK, 18)
        self.level_text = arcade.draw_text("Level: {}".format(str(self.level)), self.width - 175, self.height - 35, arcade.color.BLACK, 18)
        
        # Sanity check to let you know that god mode is active when using it
        if self.GOD_MODE:
            self.godmode_active_text = arcade.draw_text("GOD MODE ACTIVE", self.width*0.02, self.height - 35, arcade.color.BLACK, 20)

        self.all_sprites.draw()

    def add_enemy(self, delta_time: float):
        """Adds a new enemy to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """
        if self.paused:
            return

        # First, create the new enemy sprite
        enemy = EnemySprite("images/enemy_sprite.png", 0.15)

        # Set its position to a random x position and off-screen at the top
        enemy.top = random.randint(self.height, self.height + 80)
        enemy.left = random.randint(10, self.width - 10)

        # FIX ---- Set it to GO TOWARDS PLAYER
        enemy.velocity = self.enemy_velocity

        # Add it to the enemies list and all_sprites list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def add_bullet(self):
        if self.paused:
            return

        bullet = Bullet("images/enemy_sprite.png", 0.05)

        # Position the bullet
        bullet.center_y = enemy.center_y
        bullet.center_x = enemy.center_x

        # Give the bullet a speed
        bullet.velocity = (0, -8)

        # Add the bullet to the appropriate lists
        self.bullets_list.append(bullet)
        self.all_sprites.append(bullet)

    def on_key_press(self, key, modifiers):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause/Unpause the game
        I/J/K/L: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if key == arcade.key.Q:
            # Quit immediately
            arcade.close_window()

        if key == arcade.key.P:
            self.paused = not self.paused


        #if symbol == arcade.key.W or symbol == arcade.key.UP:
        #    self.player.change_y = 15

        #if symbol == arcade.key.S or symbol == arcade.key.DOWN:
        #    self.player.change_y = -15

        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -self.player_velocity
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = self.player_velocity
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = self.player_velocity
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = self.player_velocity

    def on_key_release(self, key: int, modifiers: int):
        """Undo movement vectors when movement keys are released

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if (
            key == arcade.key.W
            or key == arcade.key.S
            or key == arcade.key.UP
            or key == arcade.key.DOWN
        ):
            self.player.change_y = 0

        if (
            key == arcade.key.A
            or key == arcade.key.D
            or key == arcade.key.LEFT
            or key == arcade.key.RIGHT
        ):
            self.player.change_x = 0

class EnemySprite(arcade.Sprite):
    def update(self):
        super().update()

        if self.dead:
            self.remove_from_sprite_lists()

class Bullet(arcade.Sprite):
    def update(self):
        super().update()

        if self.collides_with_list(app.enemies_list):
            self.remove_from_sprite_lists()

if __name__ == "__main__":
    app = Arena(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    app.setup()
    arcade.run()