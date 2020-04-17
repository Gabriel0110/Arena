import arcade
from arcade.gui import *
import random
import time
import Database
from tkinter import *
from functools import partial
import sqlite3
from sqlite3 import Error
import os
import pyautogui
from datetime import datetime

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Arena"
game = None
characterSelected = False
attemptedPlay = False
total_characters = 0
max_characters = 4

def createAlert(text, title, button):
    pyautogui.alert(text=text, title=title, button=button)

class CreateButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Create", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game, total_characters, max_characters
        if total_characters < max_characters:
            game.show_view(CharacterCreation())
        elif total_characters == max_characters:
            print("You have too many characters! Please delete one to create a free slot.")

class StartButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Start", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game, characterSelected, attemptedPlay
        print("CLICKED START")
        attemptedPlay = True
        if characterSelected:
            arena = Arena()
            arena.setup()
            game.show_view(arena)
            attemptedPlay = False
        else:
            print("Please select a character to play. If you don't have any characters, create a new one!")

class PlayButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Play", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game
        #self.pressed = True
        game.show_view(CharacterSelect())

class ExitButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Exit", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        #self.pressed = True
        db.conn.close()
        exit()

class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.theme = Theme()
        self.theme.set_font(24, arcade.color.BLACK)
        normal = "images/Normal.png"
        hover = "images/Hover.png"
        clicked = "images/Clicked.png"
        locked = "images/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

        self.button_list.append(PlayButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.4, 110, 50, theme=self.theme))
        self.button_list.append(ExitButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.4, 110, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("MAIN MENU", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, arcade.color.BLACK, font_size=30, anchor_x="center")
        for button in self.button_list:
            button.draw()

class CharacterSelect(arcade.View):
    def __init__(self):
        super().__init__()

        self.theme = Theme()
        self.theme.set_font(24, arcade.color.BLACK)
        normal = "images/Normal.png"
        hover = "images/Hover.png"
        clicked = "images/Clicked.png"
        locked = "images/Locked.png"
        self.theme.add_button_textures(normal, hover, clicked, locked)

        self.button_list.append(StartButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.15, 110, 50, theme=self.theme))
        self.button_list.append(CreateButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.15, 110, 50, theme=self.theme))
    
    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        global characterSelected, attemptedPlay
        arcade.start_render()
        arcade.draw_text("Character Select", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.8, arcade.color.BLACK, font_size=30, anchor_x="center")
        arcade.draw_text("Choose one of your current characters to\ncontinue playing, or create a new one!", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.7, arcade.color.BLACK, font_size=20, anchor_x="center")
        for button in self.button_list:
            button.draw()

        if attemptedPlay and not characterSelected:
            arcade.draw_text("You must select a character to play.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.03, arcade.color.BLACK, font_size=30, anchor_x="center")

    def on_update(self, delta_time: float):
        pass

class CharacterCreation(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Character Creation", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.8, arcade.color.BLACK, font_size=30, anchor_x="center")

class PauseMenu(arcade.View):
    # For pause and unpause to work, the call to PauseMenu must have self sent with it, so pause = PauseMenu(self), then self.window.show_view(pause)
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("PAUSED", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        character_select = CharacterSelect()
        self.window.show_view(character_select)

class Arena(arcade.View):
    def __init__(self):
        super().__init__()

        # Set up the empty sprite lists
        self.enemies_list = arcade.SpriteList()
        self.bullets_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        self.player_velocity = 15

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = True

    def setup(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        self.player = arcade.Sprite("images/player_sprite.png", 0.25)
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.left = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)

        # Spawn a new enemy every 0.5 seconds
        #arcade.schedule(self.add_enemy, 0.5)

    def on_update(self, delta_time: float):
        # If paused, don't update anything
        #if arcade.paused:
        #    return

        # Did you hit an enemy?
        if self.player.collides_with_list(self.enemies_list):
            if not self.GOD_MODE:
                arcade.close_window()

        # Update everything
        self.all_sprites.update()

        # Keep the player on screen
        if self.player.top > SCREEN_HEIGHT:
            self.player.top = SCREEN_HEIGHT
        elif self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH
        elif self.player.bottom < 0:
            self.player.bottom = 0
        elif self.player.left < 0:
            self.player.left = 0

    def on_draw(self):
        # Begin rendering (will end automatically after method ends)
        arcade.start_render()

        # Draw scoreboard text
        self.score_text = arcade.draw_text("SCORE: {}".format(str(self.score)), SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        self.level_text = arcade.draw_text("Level: {}".format(str(self.level)), SCREEN_WIDTH - 175, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        
        # Sanity check to let you know that god mode is active when using it
        if self.GOD_MODE:
            self.godmode_active_text = arcade.draw_text("GOD MODE ACTIVE", SCREEN_WIDTH*0.02, SCREEN_HEIGHT - 35, arcade.color.BLACK, 20)

        self.all_sprites.draw()

    def add_enemy(self, delta_time: float):
        #if arcade.paused:
        #    return

        # First, create the new enemy sprite
        enemy = EnemySprite("images/enemy_sprite.png", 0.15)

        # Set its position to a random x position and off-screen at the top
        enemy.top = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 80)
        enemy.left = random.randint(10, SCREEN_WIDTH - 10)

        # FIX ---- Set it to GO TOWARDS PLAYER
        enemy.velocity = self.enemy_velocity

        # Add it to the enemies list and all_sprites list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def add_bullet(self):
        #if arcade.paused:
        #    return

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
        if key == arcade.key.Q:
            arcade.close_window()
            db.conn.close()
            root.destroy()
            exit()

        # Have to create a pause menu
        #if key == arcade.key.P:
        #    arcade.paused = not arcade.paused

        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -self.player_velocity
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = self.player_velocity
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = self.player_velocity
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = self.player_velocity

    def on_key_release(self, key: int, modifiers: int):
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


class LoginWindow(Frame):
    def __init__(self, master=None): 
        Frame.__init__(self, master)

        self.master.protocol("WM_DELETE_WINDOW", self.client_exit)
                
        self.master = master
        self.master.geometry("600x400")

        self.game = None

        self.init_window()

    def init_window(self):
        self.master.title("Arena - Login")

        # Initialize window with necessary buttons and labels
        username_label = Label(self, text='Username: ')
        username_label.grid(row=1, column=1, sticky="N", padx=40, pady=20)
        username_entry = Entry(self, width=40)
        username_entry.grid(row=1, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        pass_label = Label(self, text='Password: ')
        pass_label.grid(row=2, column=1, sticky="N", padx=40, pady=20)
        pass_entry = Entry(self, show="*", width=40)
        pass_entry.grid(row=2, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        login_button = Button(self, text='Login', width=20, command=partial(self.processLogin, username_entry, pass_entry))
        login_button.focus_set()
        login_button.grid(row=3, column=2, columnspan=1, padx=10, pady=25)

        create_button = Button(self, text='Create Account', width=20, command=lambda: self.newWindow(CreateAccount))
        create_button.grid(row=4, column=2,pady=25)

        forgot_button = Button(self, text='Forgot Password', width=20)
        forgot_button.grid(row=5, column=2,pady=25)

    def processLogin(self, user, pw):
        username = user.get()
        password = pw.get()

        # Check if they have anything entered
        if not username or not password:
            createAlert("You must enter a username and password.", "Error", "OK")
            return
        
        # Check for valid username & password.  If EITHER are incorrect, say that EITHER are incorrect, not "user incorrect" or "pass incorrect"
        login_info = db.getLoginInfo()

        if username not in login_info.keys() or password not in login_info[username]:
            print("Username or password invalid.")
            createAlert("Username or password invalid.", "Error", "OK")
        elif username in login_info.keys() and password in login_info[username]:
            # If both valid
            createAlert("Login successful!", "Success!", "OK")
            db.CURRENT_USERNAME = username
            CURRENT_USERNAME = username
            user.delete(0, END)
            pw.delete(0, END)
            
            # Start game
            self.launchGame()
            root.withdraw()

            ### DESTROY LOGIN WINDOW SOMEHOW ###

    def newWindow(self, window):
        self.new = Toplevel(self.master)
        window(self.new)
        if window != CreateAccount:
            root.withdraw() # hide the login window on successful login

    def launchGame(self):
        global game
        game = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        main_menu = MainMenu()
        game.show_view(main_menu)
        arcade.run()

    def client_exit(self):
        db.conn.close()
        root.destroy()
        exit()

class CreateAccount(Frame):
    def __init__(self, master): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("750x400")

        self.acct_ids = db.getAcctIds()

        self.acct_id = 0

        # Get a free ID slot by checking against IDs in database
        while True:
            if self.acct_id in self.acct_ids:
                print("Starting ID already found in DB -- incrementing ID")
                self.acct_id += 1
            else:
                break

        self.init_window()

    def init_window(self):
        self.master.title("Arena - Account Creation")
        self.pack(fill=BOTH, expand=1)

        # Initialize window with necessary buttons and labels
        username_label = Label(self, text='Username: ')
        username_label.grid(row=1, column=1, sticky="N", padx=40, pady=20)
        username_entry = Entry(self, width=40)
        username_entry.grid(row=1, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        pass_label = Label(self, text='Password: ')
        pass_label.grid(row=2, column=1, sticky="N", padx=40, pady=20)
        pass_entry = Entry(self, show="*", width=40)
        pass_entry.grid(row=2, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        email_label = Label(self, text='Email: ')
        email_label.grid(row=3, column=1, sticky="N", padx=40, pady=20)
        email_entry = Entry(self, width=40)
        email_entry.grid(row=3, column=2, sticky="N", padx=40, pady=20, columnspan=2)

        create_button = Button(self, text='Create', width=20, command=partial(self.processCreation, username_entry, pass_entry, email_entry))
        create_button.grid(row=4, column=2, padx=10, pady=25, sticky="W")

    def processCreation(self, user, pw, email):
        for item in [user.get(), pw.get(), email.get()]:
            if not item:
                print("Username, password, and email are required!")
                createAlert("Username, password, and email are required!", "Error", "OK")
                return
            
        login_info = db.getLoginInfo()
        if user.get() in login_info.keys():
            print("Username already taken.")
            createAlert("Username already taken.", "Error", "OK")
            return
        elif any(email.get() in val for val in login_info.values()):
            print("Email already in use.")
            createAlert("Email already in use.", "Error", "OK")
            return
        else:
            self.username = user.get()
            self.password = pw.get()
            self.email = email.get()
            self.date = datetime.now().strftime("%m/%d/%Y")

            values = (self.acct_id, self.username, self.password, self.email, self.date)
            print(values)
            query = """INSERT INTO accounts VALUES (?, ?, ?, ?, ?);"""

            insertions = {values: query}

            insert = db.insertAccount(insertions)
            if insert is True:
                print("Account creation successful!")
                createAlert("Account creation successful!", "Success", "OK")
                self.master.destroy()
            else:
                print("Error with account creation.")


class ForgotPassword(Frame):
    def __init__(self, master): 
        Frame.__init__(self, master)
                
        self.master = master
        self.master.geometry("750x400")
        self.init_window()

    def init_window(self):
        self.master.title("Arena - Forgot Password")
        self.pack(fill=BOTH, expand=1)

if __name__ == "__main__":
    root = Tk()

    #root.geometry("1080x600")
    root.resizable(False, False)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    app = LoginWindow(root).grid(sticky="NSEW")

    # Who is logged in
    CURRENT_USERNAME = ""

    # Initialize database at startup
    db = Database.Database()

    root.mainloop()