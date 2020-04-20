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

SCREEN_WIDTH = round(pyautogui.size()[0]*0.8)
SCREEN_HEIGHT = round(pyautogui.size()[1]*0.8)
SCREEN_TITLE = "Onslaught"
char_creation_root = None
root_master = None

game = None
characterSelected = False
char_selected_bttn_loc = []
attemptedPlay = False
selected_class = ""
selected_class_bttn_loc = []
char_creation_name = ""
createButtonPressed = False
deleteButtonPressed = False

total_characters = 0  # INCREMENT THIS WHEN CHARACTERS ARE CREATED FOR ACCOUNT, and NEED TO CHECK BEFORE CREATION
max_characters = 4
character_slot_locations = [[SCREEN_WIDTH*0.23, SCREEN_HEIGHT*0.60], [SCREEN_WIDTH*0.73, SCREEN_HEIGHT*0.60], [SCREEN_WIDTH*0.23, SCREEN_HEIGHT*0.32], [SCREEN_WIDTH*0.73, SCREEN_HEIGHT*0.32]]
loaded_characters = {}
all_char_ids = []
CURRENT_USERNAME = ""
CURRENT_ACCT_ID = None
CURRENT_CHAR = None

class GameSettings():
    def __init__(self):
        self.level_exp_requirements = {}
        self.setLevelRequirements()

        self.STAMINA_HEALTH_MULTIPLIER = 12 # each stamina point gives 12 hp
        self.INTELLECT_MANA_MULTIPLIER = 10 # each intellect point gives 10 mana

        self.AGILITY_CRIT_MULTIPLIER = 0.05 # each agility point gives 0.05% melee/range crit chance
        self.INTELLECT_CRIT_MULTIPLIER = 0.05 # each intellect point gives 0.05% SPELL crit chance

        self.AGILITY_AP_MULTIPLIER = 2 # each point of agility gives 2 attack power
        self.STRENGTH_AP_MULTIPLIER = 4 # each point of strength gives 4 attack power
        self.AP_DAMAGE_MULTIPLIER = 2 # each point of attack power increases melee/ranged damage by 2  (WILL NEED TO MULTIPLY THIS TO ABILITY DAMAGE)

        self.INTELLECT_SP_MULTIPLIER = 2 # each point of intellect gives 2 spell power
        self.SP_DAMAGE_MULTIPLIER = 2 # each point of spell power inceases spell damage by 2  (WILL NEED TO MULTIPLY THIS TO ABILITY DAMAGE)

    def setLevelRequirements(self):
        # Populates level exp requirements dict with all experience points required to get to each level (current max level is 50)
        level_req = 400
        self.level_exp_requirements = {}
        for level in range(2, 51):
            if level == 2:
                self.level_exp_requirements[level] = level_req
            else:
                self.level_exp_requirements[level] = level_req
            level_req *= 1.3

def createAlert(text, title, button):
    pyautogui.alert(text=text, title=title, button=button)

def getButtonThemes():
    theme = Theme()
    theme.set_font(24, arcade.color.BLACK)
    normal = "images/Normal.png"
    hover = "images/Hover.png"
    clicked = "images/Clicked.png"
    locked = "images/Locked.png"
    theme.add_button_textures(normal, hover, clicked, locked)
    return theme

#########################################################################################################
#                                                BUTTONS                                                #
#########################################################################################################

class BackButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Back", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        #global characterSelected
        game_view = self.view
        game.show_view(game_view)

class SinglePlayerButton(TextButton):
    def __init__(self, view, x=0, y=0, width=300, height=40, text="Single-Player Onslaught", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        #self.game = game

    def on_press(self):
        global game
        onslaught_view = Onslaught()
        onslaught_view.setup()
        game.show_view(onslaught_view)

class ArenaButton(TextButton):
    def __init__(self, view, x=0, y=0, width=175, height=40, text="1v1 PvP Arena", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        #self.game = game

    def on_press(self):
        global game
        pvp_arena_view = PvpArena()
        game.show_view(pvp_arena_view)

class ContinueButton(TextButton):
    def __init__(self, view, x=0, y=0, width=120, height=40, text="Continue", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        #global game
        game_view = self.view
        game.show_view(game_view)

class MainMenuButton(TextButton):
    def __init__(self, view, x=0, y=0, width=120, height=40, text="Main Menu", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game
        main_menu = MainMenu()
        game.show_view(main_menu)

class CreateButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Create", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game, total_characters, max_characters, char_creation_root, createButtonPressed
        if total_characters < max_characters:
            game.show_view(CharacterCreationView())
            createButtonPressed = False
        elif total_characters == max_characters:
            createAlert("You have too many characters! Please delete one to create a free slot.", "Error", "OK")
            print("You have too many characters! Please delete one to create a free slot.")


class ChooseButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Choose", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        global game, characterSelected, attemptedPlay
        attemptedPlay = True
        if characterSelected:
            mode_view = ModeSelect(self.view)
            game.show_view(mode_view)
            attemptedPlay = False
            characterSelected = False
        else:
            print("Please select a character to play. If you don't have any characters, create a new one!")

class PlayButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Play", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view
        self.text = text

    def on_press(self):
        global game, createButtonPressed, char_creation_name
        if "CharacterCreationView" in str(game.current_view):
            createButtonPressed = True
            if len(char_creation_name) > 0: 
                pass
            else:
                createAlert("A character name is required!", "Error", "OK")
                createButtonPressed = False
        if "MainMenu" in str(game.current_view):
            game.show_view(CharacterSelect())

class ExitButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Exit", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        #self.pressed = True
        db.conn.close()
        exit()

class ClassButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Class", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def on_press(self):
        global selected_class, selected_class_bttn_loc
        selected_class = self.text
        selected_class_bttn_loc = [self.x, self.y, self.width, self.height]

class NameButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Choose Name", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global char_creation_name
        char_creation_name = pyautogui.prompt("What will your character's name be?")

#-------------------------------------------  CHARACTER SELECT/DELETE BUTTONS   ---------------------------------------------#

class CharacterButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=100, text="", theme=None, char_name="", char_level=1, char_class=""):
        super().__init__(x, y, width, height, text, theme=theme)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = "Character: {}\nClass: {}\nLevel: {}".format(char_name, char_class, char_level)

    def on_press(self):
        global characterSelected, CURRENT_CHAR, char_selected_bttn_loc
        char_selected_bttn_loc = [self.x, self.y, self.width, self.height]
        characterSelected = True
        CURRENT_CHAR = self.char_name

class DeleteButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=100, text="X", theme=None, char_name=""):
        super().__init__(x, y, width, height, text, theme=theme)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.char_name = char_name

    def on_press(self):
        global CURRENT_CHAR, deleteButtonPressed
        deleteButtonPressed = True
        CURRENT_CHAR = self.char_name


#######################################################################################################################


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.theme = getButtonThemes()
        self.button_list.append(PlayButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.25, 110, 50, theme=self.theme))
        self.button_list.append(ExitButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.25, 110, 50, theme=self.theme))

        self.background = arcade.load_texture("images/title_screen_img.jpg")

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        scale = SCREEN_WIDTH / self.background.width
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        arcade.draw_text("ONSLAUGHT", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.7, arcade.color.WHITE, font_size=60, font_name='GOTHIC', anchor_x="center", bold=True)
        for button in self.button_list:
            button.draw()

class CharacterSelect(arcade.View):
    def __init__(self):
        global loaded_characters, character_slot_locations, characterSelected, total_characters, max_characters
        super().__init__()

        self.maxCharsText = False

        # Pull all characters from DB for player account that is logged in
        loaded_characters = self.getCharacters()
        total_characters = len(loaded_characters)

        self.theme = getButtonThemes()
        self.button_list.append(ChooseButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.15, 130, 50, theme=self.theme))

        if total_characters < max_characters:
            self.button_list.append(CreateButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.15, 130, 50, theme=self.theme))
        else:
            self.maxCharsText = True

        characterSelected = False

        # Make character buttons for each character, looping through characters with character_slot_locations to place buttons
        if len(loaded_characters) > 0:
            slot = 1
            for char_id, char_info in loaded_characters.items():
                self.button_list.append(CharacterButton(self, character_slot_locations[slot-1][0], character_slot_locations[slot-1][1], 350, 150, theme=self.theme, char_name=char_info[1], char_level=char_info[4], char_class=char_info[3]))
                self.button_list.append(DeleteButton(self, character_slot_locations[slot-1][0]+185, character_slot_locations[slot-1][1]+5, 50, 50, theme=self.theme, text="X", char_name=char_info[1]))
                slot += 1
    
    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)
        print("ENTERED CHARACTER SELECT")

    def on_draw(self):
        global game, characterSelected, attemptedPlay, loaded_characters, char_selected_bttn_loc
        arcade.start_render()
        arcade.draw_text("Character Select", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.9, arcade.color.BLACK, font_size=30, anchor_x="center")
        arcade.draw_text("Choose one of your current characters to\ncontinue playing, or create a new one!", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.8, arcade.color.BLACK, font_size=20, anchor_x="center")
        for button in self.button_list:
            button.draw()

        # Instead of create button, tell user character limit is reached
        if self.maxCharsText:
            arcade.draw_text("Character Limit\n    Reached!", SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.12, arcade.color.BLACK, font_size=15, anchor_x="center")

        if len(loaded_characters) == 0:
            arcade.draw_text("NO CHARACTERS AVAILABLE", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK, font_size=30, anchor_x="center")

        if characterSelected:
            arcade.draw_rectangle_outline(char_selected_bttn_loc[0], char_selected_bttn_loc[1], char_selected_bttn_loc[2]+20, char_selected_bttn_loc[3]+20, arcade.color.BLACK)

        if attemptedPlay and not characterSelected:
            arcade.draw_text("You must select a character to play.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.03, arcade.color.BLACK, font_size=30, anchor_x="center")

    def on_update(self, delta_time: float):
        global deleteButtonPressed, CURRENT_CHAR
        # Trying to delete character?
        if deleteButtonPressed:
            ans = pyautogui.confirm(text='Do you really want to delete {}?'.format(CURRENT_CHAR), title='Delete Character?', buttons=['Delete {}'.format(CURRENT_CHAR), 'Cancel'])
            if "Delete" in ans:
                print("DELETING {}".format(CURRENT_CHAR))
                self.deleteCharacter(CURRENT_CHAR)
                #game._recreate()
                game.show_view(CharacterSelect())
                deleteButtonPressed = False
                CURRENT_CHAR = None
            else:
                deleteButtonPressed = False
                CURRENT_CHAR = None

    def deleteCharacter(self, char):
        c = db.conn.cursor()
        try:
            c.execute("""DELETE FROM characters WHERE char_name = ?""", (char,))
            db.conn.commit()
            print("Successfully deleted character.")
        except Error as e:
            print(e)

    def getCharacters(self):
        global CURRENT_ACCT_ID
        c = db.conn.cursor()
        try:
            characters = c.execute("""SELECT * FROM characters WHERE acct_id = ?""", (CURRENT_ACCT_ID,)).fetchall()

            char_dict = {}
            for (char_id, acct_id, char_name, char_texture, char_class, char_level, char_health, char_mana, char_strength, char_stamina, char_intellect, char_agility, char_attack_crit_chance, char_spell_crit_chance, char_spell_power, char_attack_power, char_move_speed, curr_exp, curr_pvp_rank) in characters:
                char_dict[char_id] = [acct_id, char_name, char_texture, char_class, char_level, char_health, char_mana, char_strength, char_stamina, char_intellect, char_agility, char_attack_crit_chance, char_spell_crit_chance, char_spell_power, char_attack_power, char_move_speed, curr_exp, curr_pvp_rank]
            print("CHAR_DICT: {}".format(char_dict))
            return char_dict
        except Error as e:
            print(e)

class CharacterCreationView(arcade.View):
    def __init__(self):
        super().__init__()
        print("CHARACTERCREATIONVIEW ENTERED")

        self.theme = getButtonThemes()
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.7, 220, 50, text="Ninja", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.7, 220, 50, text="Warrior", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5, 220, 50, text="Mage", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.5, 220, 50, text="Necromancer", theme=self.theme))

        self.button_list.append(PlayButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.1, 110, 50, text="Create", theme=self.theme))
        self.button_list.append(BackButton(CharacterSelect(), SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.1, 110, 50, text="Back", theme=self.theme))

        self.button_list.append(NameButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, 230, 50, text="Choose Name", theme=self.theme))

        # self.text_list.append(arcade.TextLabel("Name: ", self.center_x - 225, self.center_y))
        # self.textbox_list.append(arcade.TextBox(self.center_x - 125, self.center_y))
        # self.button_list.append(arcade.SubmitButton(self.textbox_list[0], self.on_submit, self.center_x, self.center_y))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        global selected_class, selected_class_bttn_loc
        arcade.start_render()
        arcade.draw_text("CHARACTER CREATION", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.9, arcade.color.BLACK, font_size=25, anchor_x="center")
        for button in self.button_list:
            button.draw()
        if selected_class:
            arcade.draw_text("Selected class: {}".format(selected_class), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.025, arcade.color.BLACK, font_size=20, anchor_x="center")
            arcade.draw_rectangle_outline(selected_class_bttn_loc[0], selected_class_bttn_loc[1], selected_class_bttn_loc[2]+20, selected_class_bttn_loc[3]+20, arcade.color.BLACK)

    def on_update(self, delta_time: float):
        global createButtonPressed, char_creation_name, selected_class
        if createButtonPressed and len(char_creation_name) > 0:
            print("CREATE BUTTON PRESSED -- PROCESSING CREATION...")
            self.processCreation(char_creation_name, selected_class)
            createButtonPressed = False

    def processCreation(self, name, clss):
        global game, loaded_characters
        if not name:
            print("A name is required!")
            createAlert("A character name is required!", "Error", "OK")
            return
        else:
            # Check if there are any characters in database with that name already
            c = db.conn.cursor()
            try:
                char_names = c.execute("""SELECT char_name FROM characters""").fetchall()
            except Error as e:
                print(e)
            
            if name not in char_names:
                # Name not taken - CREATE CHARACTER
                self.char_name = name
                self.char_class = clss
                print("CREATING CHARACTER: {} of the {} class.".format(self.char_name, self.char_class))
                self.createCharacter(self.char_name, self.char_class)
                
                #loaded_characters[1] = "test"
                #game.show_view(CharacterSelect())
            else:
                # Name taken - DO NOT CREATE CHARACTER
                print("Name already taken!")
                createAlert("That name is already taken! Try a different one.", "Error", "OK")
                return
            
    def createCharacter(self, char_name, char_class):
        global game, all_char_ids, CURRENT_ACCT_ID, total_characters

        game_settings = GameSettings()

        self.char_name = char_name
        self.char_class = char_class
        all_char_ids = self.getCharIds()
        print("CHAR IDs: {}".format(all_char_ids))

        char_id = 0
        # Get char_id that is not currently in the database
        while True:
            if char_id in all_char_ids:
                print("Character ID already found in DB -- incrementing ID")
                char_id += 1
            else:
                break

        # Set all starter stats based on the class chosen (INCLUDING WHICH TEXTURE WILL BE USED)
        # STAT VALUES ARE ARBITRARY RIGHT NOW -- just putting something there to satisfy
        if self.char_class in ["Ninja", "Warrior"]:
            char_texture = "images/player_stand.png" if char_class == "Ninja" else "images/player_stand.png"
            char_level = 1
            char_stamina = 9
            char_strength = 5
            char_intellect = 5
            char_agility = 5
            char_attack_crit_chance = char_agility * game_settings.AGILITY_CRIT_MULTIPLIER
            char_spell_crit_chance = char_intellect * game_settings.INTELLECT_CRIT_MULTIPLIER
            char_spell_power = char_intellect * game_settings.INTELLECT_SP_MULTIPLIER
            char_attack_power = char_agility * game_settings.AGILITY_AP_MULTIPLIER + char_strength * game_settings.STRENGTH_AP_MULTIPLIER
            char_move_speed = 10
            char_health = char_stamina * game_settings.STAMINA_HEALTH_MULTIPLIER
            char_mana = char_intellect * game_settings.INTELLECT_MANA_MULTIPLIER
            curr_exp = 0
            curr_pvp_rank = 0
        elif self.char_class in ["Mage", "Necromancer"]:
            char_texture = "images/adventurer_stand.png" if char_class == "Mage" else "images/adventurer_stand.png"
            char_level = 1
            char_stamina = 9
            char_strength = 5
            char_intellect = 5
            char_agility = 5
            char_attack_crit_chance = char_agility * game_settings.AGILITY_CRIT_MULTIPLIER
            char_spell_crit_chance = char_intellect * game_settings.INTELLECT_CRIT_MULTIPLIER
            char_spell_power = char_intellect * game_settings.INTELLECT_SP_MULTIPLIER
            char_attack_power = char_agility * game_settings.AGILITY_AP_MULTIPLIER + char_strength * game_settings.STRENGTH_AP_MULTIPLIER
            char_move_speed = 10
            char_health = char_stamina * game_settings.STAMINA_HEALTH_MULTIPLIER
            char_mana = char_intellect * game_settings.INTELLECT_MANA_MULTIPLIER
            curr_exp = 0
            curr_pvp_rank = 0

        # Insert char_id (should be CURRENT_ACCT_ID -- a global variable), acct_id, char_name, char_texture, char_class and ALL of the starter stats created above into the characters DB
        insertions = {}
        query = """INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        values = (int(char_id), str(CURRENT_ACCT_ID), str(self.char_name), str(char_texture), str(self.char_class), int(char_level), int(char_health), int(char_mana), int(char_strength), int(char_stamina), int(char_intellect), int(char_agility), float(char_attack_crit_chance), float(char_spell_crit_chance), int(char_spell_power), int(char_attack_power), int(char_move_speed), int(curr_exp), int(curr_pvp_rank))
        insertions[values] = query

        result = db.insert(insertions)
        if not result:
            print("Error with submitting new character entries into the database.")
            return
        else:
            print("Character created - New character stats successfully input into database.")
            createAlert("Character created!", "Success", "OK")
            total_characters += 1
            game.show_view(CharacterSelect())

    def getCharIds(self):
        c = db.conn.cursor()
        try:
            id_col = c.execute("""SELECT char_id FROM characters""")
            ids = [idx[0] for idx in id_col]
        except Error as e:
            print(e)
            exit()
        return ids

class ModeSelect(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view

        self.theme = getButtonThemes()
        self.button_list.append(SinglePlayerButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, 400, 50, theme=self.theme))
        self.button_list.append(ArenaButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.4, 250, 50, theme=self.theme))
        self.button_list.append(BackButton(self.prev_view, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.2, 100, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Choose what you would like to do:", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.8, arcade.color.BLACK, font_size=30, anchor_x="center")
        for button in self.button_list:
            button.draw()

class PauseMenu(arcade.View):
    # For pause and unpause to work, the call to PauseMenu must have self sent with it, so pause = PauseMenu(self), then self.window.show_view(pause)
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

        self.theme = getButtonThemes()
        self.button_list.append(ContinueButton(self.game_view, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.15, 175, 50, theme=self.theme))
        self.button_list.append(MainMenuButton(self.game_view, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.15, 175, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        arcade.start_render()

        # draw an orange filter over him
        arcade.draw_lrtb_rectangle_filled(left=SCREEN_WIDTH*0,
                                          right=SCREEN_WIDTH,
                                          top=SCREEN_HEIGHT,
                                          bottom=SCREEN_HEIGHT*0,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, arcade.color.BLACK, font_size=30, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press 'Continue' to return to the game.",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press 'Main Menu' to exit to the main menu.",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

        for button in self.button_list:
            button.draw()

class PvpArena(arcade.View):
    def __init__(self):
        super().__init__()

        # Set up the empty sprite lists
        self.enemies_list = arcade.SpriteList()
        self.bullets_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        self.player_velocity = 15

    def setup(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up ALL players (pull them from DB, etc)
        self.player = arcade.Sprite("images/player_sprite.png", 0.25)
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.left = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)

        # Spawn a new enemy every 0.5 seconds
        #arcade.schedule(self.add_enemy, 0.5)

    def on_show(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

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
        # self.score_text = arcade.draw_text("SCORE: {}".format(str(self.score)), SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        # self.level_text = arcade.draw_text("Level: {}".format(str(self.level)), SCREEN_WIDTH - 175, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        
        # Sanity check to let you know that god mode is active when using it
        #if self.GOD_MODE:
            #self.godmode_active_text = arcade.draw_text("GOD MODE ACTIVE", SCREEN_WIDTH*0.02, SCREEN_HEIGHT - 35, arcade.color.BLACK, 20)

        self.all_sprites.draw()


class Onslaught(arcade.View):
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

    def on_show(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

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
        # self.score_text = arcade.draw_text("SCORE: {}".format(str(self.score)), SCREEN_WIDTH/2 - 75, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        # self.level_text = arcade.draw_text("Level: {}".format(str(self.level)), SCREEN_WIDTH - 175, SCREEN_HEIGHT - 35, arcade.color.BLACK, 18)
        
        # Sanity check to let you know that god mode is active when using it
        #if self.GOD_MODE:
            #self.godmode_active_text = arcade.draw_text("GOD MODE ACTIVE", SCREEN_WIDTH*0.02, SCREEN_HEIGHT - 35, arcade.color.BLACK, 20)

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
        global game

        # Have to create a pause menu
        if key == arcade.key.ESCAPE:
           pause_menu = PauseMenu(self)
           game.show_view(pause_menu)

        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -self.player_velocity
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = self.player_velocity
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = self.player_velocity
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = -self.player_velocity

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

class Character(arcade.Sprite):
    def __init__(self, char_id):
        super().init()
        self.char_id = char_id

    def update(self):
        super().update()

    def castSpell(self, spell):
        pass

class LoginWindow(Frame):
    def __init__(self, master=None): 
        global root_master
        Frame.__init__(self, master)

        self.master.protocol("WM_DELETE_WINDOW", self.client_exit)
                
        self.master = master
        self.master.geometry("600x400")
        root_master = self.master

        self.game = None

        self.init_window()

    def init_window(self):
        self.master.title("Onslaught - Login")

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
        global CURRENT_USERNAME, CURRENT_ACCT_ID
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
            CURRENT_ACCT_ID = login_info[username][0]
            user.delete(0, END)
            pw.delete(0, END)
            
            # Start game
            self.launchGame()
            root.withdraw()

    def newWindow(self, window):
        self.new = Toplevel(self.master)
        window(self.new)
        if window != CreateAccount:
            root.withdraw() # hide the login window on successful login

    def launchGame(self):
        global game, all_char_ids

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
        self.master.title("Onslaught - Account Creation")
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
        self.master.title("Onslaught - Forgot Password")
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