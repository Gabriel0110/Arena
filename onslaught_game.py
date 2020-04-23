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

game = None # HOLDS THE ACTIVE VIEW AND USED TO CHANGE VIEWS
onslaught = None # hold Onslaught() creation to call to

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

player = None # holds the single player character sprite when created

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
        self.view = view

    def on_press(self):
        global game
        pregame_lobby_view = OnslaughtPreGameLobby(self.view)
        game.show_view(pregame_lobby_view)

class ArenaButton(TextButton):
    def __init__(self, view, x=0, y=0, width=175, height=40, text="1v1 PvP Arena", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        #self.game = game

    def on_press(self):
        global game
        pvp_arena_view = PvpArena()
        game.show_view(pvp_arena_view)

class StatsAndInventoryButton(TextButton):
    def __init__(self, view, x=0, y=0, width=175, height=40, text="Stats & Inventory", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        global game
        stats_and_inv = StatsAndInventory(self.view)
        game.show_view(stats_and_inv)

class TalentsAndSpellsButton(TextButton):
    def __init__(self, view, x=0, y=0, width=175, height=40, text="Talents & Spells", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        global game
        talents_and_spells = TalentsAndSpells(self.view)
        game.show_view(talents_and_spells)

class ContinueButton(TextButton):
    def __init__(self, view, x=0, y=0, width=120, height=40, text="Continue", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.view = view

    def on_press(self):
        #global game
        game_view = self.view
        game.show_view(game_view)

class LeaveLobbyButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=40, text="Leave Lobby", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        global game
        self.view = view
        self.text = "Leave Lobby"

    def on_press(self):
        global game
        # Go back to options screen
        char_select = CharacterSelect()
        options_view = AfterCharacterSelect(char_select)
        game.show_view(options_view)

class ReturnToLobbyButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=40, text="Quit Round", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        global game
        self.view = view
        self.text = "Quit Round"

    def on_press(self):
        global game
        # Leave current round and go back to pre-game lobby
        char_select = CharacterSelect()
        options_view = AfterCharacterSelect(char_select)
        pregame_lobby_view = OnslaughtPreGameLobby(options_view)
        game.show_view(pregame_lobby_view)

class MainMenuButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=40, text="Leave Lobby", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        global game
        self.view = view
        self.text = "Leave Lobby" if "PreGameLobby" in str(game.current_view) else "Quit Round"

    def on_press(self):
        global game
        if "PreGameLobby" in str(game.current_view):
            # Go back to options screen
            options_view = AfterCharacterSelect(CharacterSelect())
            game.show_view(options_view)
        elif "PreGameLobby" not in str(game.current_view):
            # Leave current round and go back to pre-game lobby
            pregame_lobby_view = OnslaughtPreGameLobby(AfterCharacterSelect(CharacterSelect()))
            game.show_view(pregame_lobby_view)

class CreateButton(TextButton):
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Create", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global game, total_characters, max_characters, createButtonPressed
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
            after_char_select_view = AfterCharacterSelect(self.view)
            game.show_view(after_char_select_view)
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
    import re
    def __init__(self, view, x=0, y=0, width=100, height=40, text="Choose Name", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)

    def on_press(self):
        global char_creation_name
        char_creation_name = pyautogui.prompt("What will your character's name be?\n   - Only letters are allowed\n   - Max length is 10 letters")
        if char_creation_name:
            for c in char_creation_name:
                if not c.isalpha():
                    createAlert("Only letters are allowed for naming. Please try a different name.", "Error", "OK")
                    char_creation_name = ""
                    break
            if len(char_creation_name) > 10:
                createAlert("That name is too long. The max length for a name is 10.", "Error", "OK")
                char_creation_name = ""
            
            char_creation_name = char_creation_name.title()

#-------------------------------------------  CHARACTER SELECT/DELETE BUTTONS   ---------------------------------------------#

class CharacterButton(TextButton):
    def __init__(self, view, x=0, y=0, width=150, height=100, text="", theme=None, char_name="", char_level=1, char_class=""):
        super().__init__(x, y, width, height, text, theme=theme)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.char_name = char_name
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


##############################################################################################################################


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
        global selected_class

        selected_class = ""

        self.theme = getButtonThemes()
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.7, 230, 50, text="Assassin", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.50, SCREEN_HEIGHT*0.7, 230, 50, text="Warrior", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.7, 230, 50, text="Mage", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5, 230, 50, text="Necromancer", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.50, SCREEN_HEIGHT*0.5, 230, 50, text="Void Stalker", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.5, 230, 50, text="Friar", theme=self.theme))

        self.button_list.append(PlayButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.1, 110, 50, text="Create", theme=self.theme))
        self.button_list.append(BackButton(CharacterSelect(), SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.1, 110, 50, text="Back", theme=self.theme))

        self.button_list.append(NameButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.2, 230, 50, text="Choose Name", theme=self.theme))

        # self.text_list.append(arcade.TextLabel("Name: ", self.center_x - 225, self.center_y))
        # self.textbox_list.append(arcade.TextBox(self.center_x - 125, self.center_y))
        # self.button_list.append(arcade.SubmitButton(self.textbox_list[0], self.on_submit, self.center_x, self.center_y))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        global selected_class, selected_class_bttn_loc, char_creation_name
        arcade.start_render()
        arcade.draw_text("CHARACTER CREATION", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.9, arcade.color.BLACK, font_size=25, anchor_x="center")
        for button in self.button_list:
            button.draw()

        # Notify of selected class and provide description of the class on the screen
        if selected_class:
            arcade.draw_text("Selected class: {}".format(selected_class), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.025, arcade.color.BLACK, font_size=20, anchor_x="center")
            arcade.draw_rectangle_outline(selected_class_bttn_loc[0], selected_class_bttn_loc[1], selected_class_bttn_loc[2]+20, selected_class_bttn_loc[3]+20, arcade.color.BLACK)
            if selected_class == "Assassin":
                arcade.draw_text("The assassin is a nimble, agile class with the ability use the shadows to its advantage, striking foes where they least expect it.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")
            elif selected_class == "Warrior":
                arcade.draw_text("Hack 'n Slash is the name of the game.. er, the class. Use brute force and the might of your blade to slash through your enemies\nand wreak havoc to the land.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")
            elif selected_class == "Mage":
                arcade.draw_text("Whether it be fire or ice, the mage is sure to control the fight, bending the elements to its will.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")
            elif selected_class == "Necromancer":
                arcade.draw_text("The Necromancer is not to be taken lightly... nor its undead minions. Call upon the dead to rise and serve you, attacking anything\nin sight while you drain the souls of your enemies.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")
            elif selected_class == "Void Stalker":
                arcade.draw_text("As the Void Stalker, harness the power of the void and shape it to your will, bringing destruction to enemies near and far... or let it harness you..", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")
            elif selected_class == "Friar":
                arcade.draw_text("Don't be fooled by the simple title. The friar is not to be meddled with as it wields holy power to smite its enemies and ensure it's\nthe last one standing at the end of a fight.", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.BLACK, font_size=24, anchor_x="center")

        if char_creation_name:
            arcade.draw_text("Name: {}".format(char_creation_name), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.1, arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_update(self, delta_time: float):
        global createButtonPressed, char_creation_name, selected_class
        if createButtonPressed and char_creation_name:
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
                char_names = c.execute("""SELECT char_name FROM characters""")
                names = [char_name[0].title() for char_name in char_names]
            except Error as e:
                print(e)
            
            if name.title() not in names:
                # Name not taken - CREATE CHARACTER
                self.char_name = name.title()
                self.char_class = clss
                print("CREATING CHARACTER: {} of the {} class.".format(self.char_name, self.char_class))
                self.createCharacter(self.char_name, self.char_class)
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
        char_texture = "images/adventurer_stand.png" # SHOULD BE DIFFERENT FOR EVERY CLASS
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
            self.insertGameStats(char_id)

    def getCharIds(self):
        c = db.conn.cursor()
        try:
            id_col = c.execute("""SELECT char_id FROM characters""")
            ids = [idx[0] for idx in id_col]
        except Error as e:
            print(e)
            exit()
        return ids

    def insertGameStats(self, char_id):
        insertions = {}
        query = """INSERT INTO game_stats VALUES (?, ?);"""
        values = (int(char_id), 1)
        insertions[values] = query
        result = db.insert(insertions)
        if not result:
            print("Error with submitting new character game stats (current wave number) into the database.")
            return

class TalentsAndSpells(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view

        self.theme = getButtonThemes()
        self.button_list.append(BackButton(self.prev_view, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.1, 100, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        for button in self.button_list:
            button.draw()

class StatsAndInventory(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view

        self.theme = getButtonThemes()
        self.button_list.append(BackButton(self.prev_view, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.1, 100, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        arcade.start_render()
        for button in self.button_list:
            button.draw()

class AfterCharacterSelect(arcade.View):
    def __init__(self, prev_view):
        super().__init__()
        self.prev_view = prev_view

        self.theme = getButtonThemes()
        self.button_list.append(SinglePlayerButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, 425, 50, theme=self.theme))
        self.button_list.append(ArenaButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.5, 425, 50, theme=self.theme))
        self.button_list.append(StatsAndInventoryButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.4, 425, 50, theme=self.theme))
        self.button_list.append(TalentsAndSpellsButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, 425, 50, theme=self.theme))
        self.button_list.append(BackButton(self.prev_view, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.1, 100, 50, theme=self.theme))

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
        self.button_list.append(ContinueButton(self.game_view, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.15, 200, 50, theme=self.theme))

        if "PreGame" in str(self.game_view):
            self.button_list.append(LeaveLobbyButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.15, 200, 50, theme=self.theme))
        elif "Onslaught" in str(self.game_view) and "PreGame" not in str(self.game_view):
            self.button_list.append(ReturnToLobbyButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.15, 200, 50, theme=self.theme))

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

        arcade.draw_text("PAUSED", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, arcade.color.BLACK, font_size=40, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press 'Continue' to return to the game.",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        # arcade.draw_text("Press 'Main Menu' to exit to the main menu.",
        #                  SCREEN_WIDTH/2,
        #                  SCREEN_HEIGHT/2-30,
        #                  arcade.color.BLACK,
        #                  font_size=20,
        #                  anchor_x="center")

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

class OnslaughtPreGameLobby(arcade.View):
    def __init__(self, view):
        super().__init__()
        global player
        self.view = view

        # Set up the empty sprite lists
        self.spell_slot_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        self.theme = getButtonThemes()
        self.button_list.append(LeaveLobbyButton(self, SCREEN_WIDTH*0.95, SCREEN_HEIGHT*0.97, 200, 50, theme=self.theme))

        self.player_velocity = 10
        self.curr_round_number = self.getCurrentRoundNumber()

        self.setup()

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = True

    def setup(self):
        global player
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        self.player = Character("images/adventurer_stand.png", 1.0)
        self.player.setup()
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.center_x = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)
        player = self.player

        # Set up for health bar
        self.max_health = self.player.getMaxHealth()
        self.current_health = self.player.getCurrentHealth()

        # Draw spell bar UI sprites, then add spell images inside them
        centers = [SCREEN_WIDTH*0.425, SCREEN_WIDTH*0.475, SCREEN_WIDTH*0.525, SCREEN_WIDTH*0.575, SCREEN_WIDTH*0.675]
        for i in range(5):
            if i == 4:
                spell_slot = arcade.Sprite("images/spell_slot.png", 1.0)
                spell_slot.bottom = SCREEN_HEIGHT*0.05
                spell_slot.center_x = centers[i]
            else:
                spell_slot = arcade.Sprite("images/spell_slot.png", 1.0)
                spell_slot.bottom = SCREEN_HEIGHT*0.05
                spell_slot.center_x = centers[i]
            self.spell_slot_list.append(spell_slot)
            self.all_sprites.append(spell_slot)

        # Draw lobby art and append to all_sprites list
        self.entrance = arcade.Sprite("images/entrance.png", 7.0)
        self.entrance.right = SCREEN_WIDTH
        self.entrance.center_y = SCREEN_HEIGHT/2
        self.entrance.angle = 270

        self.wall_piece1 = arcade.Sprite("images/corner.png", 7.0)
        self.wall_piece1.bottom = self.entrance.top
        self.wall_piece1.right = SCREEN_WIDTH
        self.wall_piece2 = arcade.Sprite("images/corner_inverted.png", 7.0)
        self.wall_piece2.top = self.entrance.bottom
        self.wall_piece2.right = SCREEN_WIDTH

        self.all_sprites.append(self.entrance)
        self.all_sprites.append(self.wall_piece1)
        self.all_sprites.append(self.wall_piece2)

        # Spawn a new enemy every 2 seconds
        #arcade.schedule(self.add_enemy, 2.0)

    def on_show(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

    def on_update(self, delta_time: float):
        global game, onslaught
        # If paused, don't update anything
        #if arcade.paused:
        #    return

        # Keep updating the player's current health
        self.current_health = self.player.getCurrentHealth()

        # Did the player step into the 
        if self.player.collides_with_sprite(self.entrance):
            # PROMPT TO ASK IF YOU WANT TO BEGIN ONSLAUGHT ROUND (can use pyautogui, but look into arcade gui prompt? there is an example)
            ans = pyautogui.confirm("Do you wish to begin the next Onslaught round?", "Start next round?", buttons=["Let's do it", "Cancel"])
            if ans == "Let's do it":
                onslaught = Onslaught()
                onslaught.setup()
                game.show_view(onslaught)
            else:
                # Move character out of entrance
                self.player.center_x = self.entrance.center_x - 200

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
        global CURRENT_CHAR
        # Begin rendering (will end automatically after method ends)
        arcade.start_render()

        arcade.draw_text("Trinket", SCREEN_WIDTH*0.6625, SCREEN_HEIGHT*0.025, arcade.color.BLACK, 16, bold=True)
        arcade.draw_text("Begin Round", self.entrance.left - 30, SCREEN_HEIGHT/2 - 50, arcade.color.BLACK, 16, bold=True, rotation=270.0, anchor_x="center")

        # Draw player name and health bar
        arcade.draw_text(CURRENT_CHAR, self.player.center_x, self.player.top+15, arcade.color.WHITE, 16, bold=True, anchor_x="center")
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+10, 70, 10, arcade.color.BLACK)
        self.hp_percent = self.current_health / self.max_health
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.hp_percent))/2), self.player.top+10, 69.7*self.hp_percent, 9.7, arcade.color.RED)

        # Display current round
        arcade.draw_text("Current Round: {}".format(self.curr_round_number), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.96, arcade.color.WHITE, 30, bold=True, anchor_x="center")

        for button in self.button_list:
            button.draw()

        self.all_sprites.draw()

    def on_key_press(self, key, modifiers):
        global game

        # SIMILAR TO PAUSE MENU, BUT OPTION TO GO BACK TO OPTIONS SELECTION
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

    def getCurrentRoundNumber(self):
        global CURRENT_CHAR
        c = db.conn.cursor()
        try:
            char_id = c.execute("""SELECT char_id FROM characters WHERE char_name = ?""", (CURRENT_CHAR,)).fetchall()
            round_num = c.execute("""SELECT curr_round_number FROM game_stats WHERE char_id = ?""", (str(char_id[0][0]),)).fetchall()
        except Error as e:
            print(e)
            exit()
        return round_num[0][0]

class Onslaught(arcade.View):
    def __init__(self):
        super().__init__()
        global player

        # Set up the empty sprite lists
        self.enemies_list = arcade.SpriteList()
        self.basic_attack_list = arcade.SpriteList()
        #self.weapon_list = arcade.SpriteList()
        self.spell_slot_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        #self.all_sprites.append(self.weapon_list)

        self.player = player
        self.char_class = self.getCharClass()
        self.basic_attack_img = self.getBasicAttackImage()
        self.sword = WeaponSprite("images/sword.png", 0.5)
        self.swingingWeapon = False
        self.quadrant = ""
        self.swing_timer = 0

        self.enemyHit = False
        self.deleteAttack = False

        self.player_velocity = 10

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = True

        # Schedule enemy spawning every 2 seconds
        arcade.schedule(self.add_enemy, 2.0)

    def setup(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        #self.player = Character("images/adventurer_stand.png", 1.0)
        #self.player.setup()
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.center_x = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)

        # Set up for health bar
        self.max_health = self.player.getMaxHealth()
        self.current_health = self.player.getCurrentHealth()

        # Draw spell bar UI sprites, then add spell images inside them
        centers = [SCREEN_WIDTH*0.425, SCREEN_WIDTH*0.475, SCREEN_WIDTH*0.525, SCREEN_WIDTH*0.575, SCREEN_WIDTH*0.675]
        for i in range(5):
            if i == 4:
                spell_slot = arcade.Sprite("images/spell_slot.png", 1.0)
                spell_slot.bottom = SCREEN_HEIGHT*0.05
                spell_slot.center_x = centers[i]
            else:
                spell_slot = arcade.Sprite("images/spell_slot.png", 1.0)
                spell_slot.bottom = SCREEN_HEIGHT*0.05
                spell_slot.center_x = centers[i]
            self.spell_slot_list.append(spell_slot)
            self.all_sprites.append(spell_slot)

        # Spawn a new enemy every 0.5 seconds
        #arcade.schedule(self.add_enemy, 0.5)

    def on_show(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

    def on_update(self, delta_time: float):
        global player, game
        # If paused, don't update anything
        #if arcade.paused:
        #    return

        # Keep updating the player's current health
        self.current_health = self.player.getCurrentHealth()

        if self.swingingWeapon is False:
            arcade.unschedule(self.swingWeapon) 
        else:
            if self.quadrant == "top_left":
                self.sword.center_x = self.player.center_x - 30
                self.sword.center_y = self.player.center_y + 30
            elif self.quadrant == "bottom_left":
                self.sword.center_x = self.player.center_x - 30
                self.sword.center_y = self.player.center_y - 30
            elif self.quadrant == "top_right":
                self.sword.center_x = self.player.center_x + 30
                self.sword.center_y = self.player.center_y + 30
            elif self.quadrant == "bottom_right":
                self.sword.center_x = self.player.center_x + 30
                self.sword.center_y = self.player.center_y - 30

        # Did you hit an enemy?
        if self.player.collides_with_list(self.enemies_list):
            self.player.takeDamage(self.player.getMaxHealth()*0.1)

        # Did you die?
        if self.current_health <= 0:
            # YOU DIED
            # Freeze screen and pop up something saying you died, or take to summary screen, or take to summary screen AFTER popup message, etc
            game.show_view(OnslaughtPreGameLobby(AfterCharacterSelect(CharacterSelect())))

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
        
        # Update global
        player = self.player

    def on_draw(self):
        global CURRENT_CHAR
        # Begin rendering (will end automatically after method ends)
        arcade.start_render()

        arcade.draw_text("Trinket", SCREEN_WIDTH*0.6625, SCREEN_HEIGHT*0.025, arcade.color.BLACK, 16, bold=True)

        # Draw player name and health bar
        arcade.draw_text(CURRENT_CHAR, self.player.center_x, self.player.top+15, arcade.color.WHITE, 16, bold=True, anchor_x="center")
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+10, 70, 10, arcade.color.BLACK)
        self.hp_percent = self.current_health / self.max_health
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.hp_percent))/2), self.player.top+10, 69.7*self.hp_percent, 9.7, arcade.color.RED)

        # Draw enemy health bars
        for enemy in self.enemies_list:
            arcade.draw_rectangle_outline(enemy.center_x, enemy.top+10, 70, 10, arcade.color.BLACK)
            hp_percent = enemy.enemy_current_health / enemy.enemy_max_health
            arcade.draw_rectangle_filled(enemy.center_x - ((69.7 - (69.7*hp_percent))/2), enemy.top+10, 69.7*hp_percent, 9.7, arcade.color.RED)

        self.all_sprites.draw()

    def add_enemy(self, delta_time: float):
        #if arcade.paused:
        #    return

        # First, create the new enemy sprite
        enemy = EnemySprite("images/enemy_sprite.png", 1.0)
        enemy.setup(50)

        # Set its position to a random x position and off-screen at the top
        enemy.top = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 80)
        enemy.left = random.randint(10, SCREEN_WIDTH - 10)

        # FIX ---- Set it to GO TOWARDS PLAYER
        enemy.velocity = (0, -2)

        # Add it to the enemies list and all_sprites list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

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

    def on_mouse_press(self, x, y, button, modifiers):
        import math

        if self.char_class == "Assassin":
            if self.swingingWeapon == False:
                self.swing_timer = 0
                self.swingingWeapon = True
                self.enemyHit = False

                # Position the bullet at the player's current location
                start_x = self.player.center_x
                start_y = self.player.center_y

                # Get from the mouse the destination location for the bullet
                # IMPORTANT! If you have a scrolling screen, you will also need
                # to add in self.view_bottom and self.view_left.
                dest_x = x
                dest_y = y

                # Do math to calculate how to get the bullet to the destination.
                # Calculation the angle in radians between the start points
                # and end points. This is the angle the bullet will travel.
                x_diff = dest_x - start_x
                y_diff = dest_y - start_y
                angle = math.atan2(y_diff, x_diff)

                # Angle the bullet sprite so it doesn't look like it is flying
                # sideways.
                self.sword.angle = math.degrees(angle)
                self.sword.turn_left(30)

                if x < self.player.center_x:
                    if y > self.player.center_y:
                        self.quadrant = "top_left"
                        self.sword.center_x = self.player.center_x - 30
                        self.sword.center_y = self.player.center_y + 30
                    else:
                        self.quadrant = "bottom_left"
                        self.sword.center_x = self.player.center_x - 30
                        self.sword.center_y = self.player.center_y - 30
                else:
                    if y > self.player.center_y:
                        self.quadrant = "top_right"
                        self.sword.center_x = self.player.center_x + 30
                        self.sword.center_y = self.player.center_y + 30
                    else:
                        self.quadrant = "bottom_right"
                        self.sword.center_x = self.player.center_x + 30
                        self.sword.center_y = self.player.center_y - 30

                self.all_sprites.append(self.sword)

                arcade.schedule(self.swingWeapon, 1/80)
        elif self.char_class == "Mage" or self.char_class == "Necromancer":
            basic_attack = BasicAttackSprite(self.basic_attack_img[0], self.basic_attack_img[1])
            basic_attack_speed = 15

            # Position the bullet at the player's current location
            start_x = self.player.center_x
            start_y = self.player.center_y
            basic_attack.center_x = start_x
            basic_attack.center_y = start_y

            # Get from the mouse the destination location for the bullet
            # IMPORTANT! If you have a scrolling screen, you will also need
            # to add in self.view_bottom and self.view_left.
            dest_x = x
            dest_y = y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Angle the bullet sprite so it doesn't look like it is flying
            # sideways.
            basic_attack.angle = math.degrees(angle)
            #print(f"Bullet angle: {basic_attack.angle:.2f}")

            # Taking into account the angle, calculate our change_x
            # and change_y. Velocity is how fast the bullet travels.
            basic_attack.change_x = math.cos(angle) * basic_attack_speed
            basic_attack.change_y = math.sin(angle) * basic_attack_speed

            # Add the bullet to the appropriate lists
            self.basic_attack_list.append(basic_attack)
            self.all_sprites.append(basic_attack)

    def getCharClass(self):
        global CURRENT_CHAR
        c = db.conn.cursor()
        try:
            char_class = c.execute("""SELECT char_class FROM characters WHERE char_name = ?""", (CURRENT_CHAR,)).fetchall()
        except Error as e:
            print(e)
            exit()
        return char_class[0][0]

    def getBasicAttackImage(self):
        # RETURNS IMAGE AND ITS SCALE
        if self.char_class == "Mage":
            return ["images/caster_bolt.png", 0.8]

    def swingWeapon(self, _delta_time):
        global onslaught
        RADIANS_PER_FRAME = 1.8
        arcade.start_render()

        self.sword.turn_right(8)

        self.swing_timer += 1/80
        if self.swing_timer >= 20/80:
            self.sword.center_x = SCREEN_WIDTH + 200
            self.sword.remove_from_sprite_lists()
            self.sword.kill()
            self.swingingWeapon = False
            arcade.unschedule(self.swingWeapon)
            return

class EnemySprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if onslaught.char_class == "Assassin" or onslaught.char_class == "Warrior":
            if self.collides_with_sprite(onslaught.sword):
                if onslaught.enemyHit == False:
                    onslaught.enemyHit = True
                    print("ENEMY HIT BY MELEE BASIC ATTACK - DECREMENTING HEALTH BY 10")
                    self.enemy_current_health -= 10
            #else:
                #onslaught.enemyHit = False
        elif onslaught.char_class == "Mage":
            if self.collides_with_list(onslaught.basic_attack_list):
                if onslaught.enemyHit == False:
                    onslaught.enemyHit = True
                    onslaught.deleteAttack = True
                    print("ENEMY HIT BY RANGED BASIC ATTACK - DECREMENTING HEALTH BY 10")
                    self.enemy_current_health -= 10
            else:
                onslaught.enemyHit = False

        if self.enemy_current_health <= 0:
            self.remove_from_sprite_lists()

    def setup(self, health):
        self.enemy_max_health = health
        self.enemy_current_health = self.enemy_max_health

class BasicAttackSprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if self.center_y >= SCREEN_HEIGHT or self.center_x >= SCREEN_WIDTH or self.center_x <= 0 or self.center_y <= 0:
            self.remove_from_sprite_lists()

        if self.collides_with_list(onslaught.enemies_list):
            if onslaught.deleteAttack:
                self.remove_from_sprite_lists()
                onslaught.deleteAttack = False

class WeaponSprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if onslaught.swingingWeapon == False:
            self.remove_from_sprite_lists()

        #if self.collides_with_list(onslaught.enemies_list):
            #self.remove_from_sprite_lists()

class Character(arcade.Sprite):
    def setup(self):
        #self.player_class = self.getCharClass()
        self.player_stats = self.getCharStats()
        self.player_max_health = self.player_stats[0][6]
        self.player_current_health = self.player_max_health # start current health at the max health

    def update(self):
        super().update()

    def castSpell(self, spell):
        pass

    def getMaxHealth(self):
        return self.player_max_health

    def getCurrentHealth(self):
        return self.player_current_health

    def takeDamage(self, dmg):
        self.player_current_health -= dmg

    def getCharStats(self):
        global CURRENT_CHAR
        c = db.conn.cursor()
        try:
            char_stats = c.execute("""SELECT * FROM characters WHERE char_name = ?""", (CURRENT_CHAR,)).fetchall()
            #stats = [stat[0] for stat in char_stats]
        except Error as e:
            print(e)
            exit()
        return char_stats

    def getCharClass(self):
        c = db.conn.cursor()
        try:
            char_class = c.execute("""SELECT char_class FROM characters WHERE char_name = ?""", (CURRENT_CHAR,)).fetchall()
        except Error as e:
            print(e)
            exit()
        return char_class[0][0]

class LoginWindow(Frame):
    def __init__(self, master=None): 
        Frame.__init__(self, master)

        self.master.protocol("WM_DELETE_WINDOW", self.client_exit)
                
        self.master = master
        self.master.geometry("600x400")

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