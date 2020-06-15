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
gamePaused = False

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
CURRENT_ROUND = 0

player = None # holds the single player character sprite when created

# Cursor position
mouse_x = 0
mouse_y = 0

class GameSettings():
    def __init__(self):
        self.level_exp_requirements = {}
        self.setLevelRequirements()

        self.STAMINA_HEALTH_MULTIPLIER = 12 # each stamina point gives 12 hp
        self.INTELLECT_MANA_MULTIPLIER = 10 # each intellect point gives 10 mana

        self.AGILITY_CRIT_MULTIPLIER = 0.0005 # each agility point gives 0.0005% melee/range crit chance
        self.INTELLECT_CRIT_MULTIPLIER = 0.0005 # each intellect point gives 0.0005% SPELL crit chance

        self.AGILITY_AP_MULTIPLIER = 1 # each point of agility gives 1 attack power
        self.STRENGTH_AP_MULTIPLIER = 2 # each point of strength gives 3 attack power
        self.AP_DAMAGE_MULTIPLIER = 2 # each point of attack power increases melee/ranged damage by 2  (WILL NEED TO MULTIPLY THIS TO ABILITY DAMAGE)

        self.INTELLECT_SP_MULTIPLIER = 2 # each point of intellect gives 2 spell power
        self.SP_DAMAGE_MULTIPLIER = 3 # each point of spell power inceases spell damage by 3  (WILL NEED TO MULTIPLY THIS TO ABILITY DAMAGE)

    def setLevelRequirements(self):
        # Populates level exp requirements dict with all experience points required to get to each level (current max level is 50)
        level_req = 900
        self.level_exp_requirements = {}
        for level in range(2, 51):
            if level == 2:
                self.level_exp_requirements[level] = level_req
            else:
                self.level_exp_requirements[level] = level_req

            if level <= 5:
                level_req *= 1.5
            elif 5 < level <= 15:
                level_req *= 1.1
            elif 15 < level <= 20:
                level_req *= 1.05
            elif 20 < level <= 25:
                level_req *= 1.05
            elif level > 25:
                level_req *= 1.01

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
        global gamePaused
        if "RoundSummary" in str(self.view):
            game_view = OnslaughtPreGameLobby(AfterCharacterSelect(CharacterSelect()))
            game.show_view(game_view)
        else:
            gamePaused = False
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
    def __init__(self, view, x=0, y=0, width=350, height=175, text="", theme=None, char_name="", char_level=1, char_class="", char_round=1):
        super().__init__(x, y, width, height, text, theme=theme)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.char_name = char_name
        self.text = "Character: {}\nClass: {}\nLevel: {}\nRound: {}".format(char_name, char_class, char_level, char_round)

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
                self.button_list.append(CharacterButton(self, character_slot_locations[slot-1][0], character_slot_locations[slot-1][1], 350, 175, theme=self.theme, char_name=char_info[1], char_level=char_info[4], char_class=char_info[3], char_round=char_info[-1]))
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
            for (char_id, acct_id, char_name, char_texture, char_class, char_level, char_strength, char_stamina, char_intellect, char_agility, char_move_speed, curr_exp, curr_pvp_rank, curr_round_num) in characters:
                char_dict[char_id] = [acct_id, char_name, char_texture, char_class, char_level, char_strength, char_stamina, char_intellect, char_agility, char_move_speed, curr_exp, curr_pvp_rank, curr_round_num]
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
        #self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.50, SCREEN_HEIGHT*0.7, 230, 50, text="Warrior", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.7, 230, 50, text="Mage", theme=self.theme))
        #self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.25, SCREEN_HEIGHT*0.5, 230, 50, text="Necromancer", theme=self.theme))
        self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.50, SCREEN_HEIGHT*0.5, 230, 50, text="Void Stalker", theme=self.theme))
        #self.button_list.append(ClassButton(self, SCREEN_WIDTH*0.75, SCREEN_HEIGHT*0.5, 230, 50, text="Friar", theme=self.theme))

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
        char_stamina = 12
        char_strength = 7
        char_intellect = 8
        char_agility = 7
        char_attack_crit_chance = 0.05 + char_agility * game_settings.AGILITY_CRIT_MULTIPLIER
        char_spell_crit_chance = 0.05 + char_intellect * game_settings.INTELLECT_CRIT_MULTIPLIER
        char_spell_power = char_intellect * game_settings.INTELLECT_SP_MULTIPLIER
        char_attack_power = char_agility * game_settings.AGILITY_AP_MULTIPLIER + char_strength * game_settings.STRENGTH_AP_MULTIPLIER
        char_move_speed = 10
        char_health = char_stamina * game_settings.STAMINA_HEALTH_MULTIPLIER
        char_mana = char_intellect * game_settings.INTELLECT_MANA_MULTIPLIER
        curr_exp = 0
        curr_pvp_rank = 0
        curr_round_num = 1

        # Insert char_id (should be CURRENT_ACCT_ID -- a global variable), acct_id, char_name, char_texture, char_class and ALL of the starter stats created above into the characters DB
        insertions = {}
        query = """INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        values = (int(char_id), str(CURRENT_ACCT_ID), str(self.char_name), str(char_texture), str(self.char_class), int(char_level), int(char_strength), int(char_stamina), int(char_intellect), int(char_agility), int(char_move_speed), int(curr_exp), int(curr_pvp_rank), int(curr_round_num))
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
            #self.insertGameStats(char_id)

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

        # Load all learned spells that the character has as buttons (check [class]_spells_table for True booleans on spells, then pull their names)

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
        global gamePaused

        gamePaused = True

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

        self.all_sprites.draw()

class OnslaughtPreGameLobby(arcade.View):
    def __init__(self, view):
        super().__init__()
        global player, CURRENT_ROUND
        self.view = view

        self.game_settings = GameSettings()

        # Set up the empty sprite lists
        self.spell_slot_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        self.theme = getButtonThemes()
        self.button_list.append(LeaveLobbyButton(self, SCREEN_WIDTH*0.9, SCREEN_HEIGHT*0.97, 200, 50, theme=self.theme))

        self.player_velocity = 8
        self.curr_round_number = self.getCurrentRoundNumber()
        CURRENT_ROUND = self.curr_round_number

        self.setup()

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = True

    def setup(self):
        global player
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        self.player = Character("images/adventurer_stand.png", 0.8)
        self.player.setup()
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.center_x = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)
        player = self.player

        # Set up for health and mana bars
        self.max_health = self.player.getMaxHealth()
        self.current_health = self.player.getCurrentHealth()
        self.max_mana = self.player.getMaxMana()
        self.current_mana = self.player.getCurrentMana()

        # Draw spell bar UI sprites, then add spell images inside them
        centers = [SCREEN_WIDTH*0.400, SCREEN_WIDTH*0.470, SCREEN_WIDTH*0.540, SCREEN_WIDTH*0.610, SCREEN_WIDTH*0.700]
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

        # Keep updating the player's current health and mana
        self.current_health = self.player.getCurrentHealth()
        self.current_mana = self.player.getCurrentMana()

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

        arcade.draw_text("Trinket", SCREEN_WIDTH*0.7, SCREEN_HEIGHT*0.025, arcade.color.BLACK, 16, bold=True, anchor_x="center")
        arcade.draw_text("Begin Round", self.entrance.left - 30, SCREEN_HEIGHT/2 - 50, arcade.color.BLACK, 16, bold=True, rotation=270.0, anchor_x="center")
        if self.player.level != 50:
            arcade.draw_text("Character Level: {}\nExperience: {}/{}".format(self.player.level, int(self.player.current_exp), int(self.game_settings.level_exp_requirements[self.player.level+1])), SCREEN_WIDTH*0.105, SCREEN_HEIGHT*0.925, arcade.color.WHITE, 22, bold=True, anchor_x="center")

        # Draw player name
        arcade.draw_text(CURRENT_CHAR, self.player.center_x, self.player.top+17.5, arcade.color.WHITE, 16, bold=True, anchor_x="center")

        # Draw health bar
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+12.5, 70, 10, arcade.color.BLACK)
        self.hp_percent = self.current_health / self.max_health
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.hp_percent))/2), self.player.top+13, 69.7*self.hp_percent, 9.7, arcade.color.RED)

        # Draw mana bar
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+2, 70, 10, arcade.color.BLACK)
        self.mana_percent = self.current_mana / self.max_mana
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.mana_percent))/2), self.player.top+2, 69.7*self.mana_percent, 9.7, arcade.color.BLUE)

        # Display current round
        arcade.draw_text("Current Round: {}".format(self.curr_round_number), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.95, arcade.color.WHITE, 30, bold=True, anchor_x="center")

        # Add spell names to UI slots
        centers = [SCREEN_WIDTH*0.400, SCREEN_WIDTH*0.470, SCREEN_WIDTH*0.540, SCREEN_WIDTH*0.610, SCREEN_WIDTH*0.700]
        num_spells = len(self.player.spells)
        if num_spells > 0:
            for i in range(num_spells):
                arcade.draw_text(self.player.spells[i], centers[i], SCREEN_HEIGHT*0.08, arcade.color.BLACK, 14, bold=True, anchor_x="center")

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
            round_num = c.execute("""SELECT curr_round_num FROM characters WHERE char_id = ?""", (str(char_id[0][0]),)).fetchall()
        except Error as e:
            print(e)
            exit()
        return round_num[0][0]

class Onslaught(arcade.View):
    def __init__(self):
        super().__init__()
        global player, CURRENT_ROUND

        self.game_settings = GameSettings()

        # Set up the empty sprite lists
        self.basic_enemies_list = arcade.SpriteList()
        self.caster_enemies_list = arcade.SpriteList()
        self.boss_enemies_list = arcade.SpriteList()
        self.basic_attack_list = arcade.SpriteList()
        self.caster_attack_list = arcade.SpriteList()
        #self.weapon_list = arcade.SpriteList()
        self.spell_sprite_list = arcade.SpriteList()
        self.spell_slot_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

        #self.all_sprites.append(self.weapon_list)

        self.current_enemy_count = 0
        self.total_enemy_count = 6 + CURRENT_ROUND*2
        self.enemies_killed = 0

        self.bossSpawned = False

        self.player = player
        self.char_class = self.getCharClass()
        self.basic_attack_img = self.getBasicAttackImage()
        self.sword = WeaponSprite("images/sword.png", 0.5)
        self.swingingWeapon = False
        self.quadrant = ""
        self.swing_timer = 0

        self.enemyHit = False
        self.deleteAttack = False
        self.playerCanBeHit = True

        self.player_velocity = 10
        self.enemy_velocity = 2.5 # used in EnemySprite follow_sprite() method
        self.basic_enemy_velocity = (0, -2)
        self.boss_enemy_velocity = (0, -1.5)

        self.spell1_cooldown = 0
        self.spell2_cooldown = 0
        self.spell3_cooldown = 0
        self.spell4_cooldown = 0

        self.voidTipActive = False

        # FOR TESTING - set to "True" to not lose when hit by enemy.  Otherwise, KEEP "False"
        self.GOD_MODE = False

        # Schedule enemy spawning every 3 seconds
        arcade.schedule(self.add_enemy, 3.0)

        # Schedule to have caster enemies shoot if there are caster enemies alive
        arcade.schedule(self.casterShoot, 2.5)

        # Mana regeneration scheduler
        arcade.schedule(self.regenMana, 2.0)

    def setup(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

        # Set up the player
        #self.player = Character("images/adventurer_stand.png", 1.0)
        #self.player.setup()
        self.player.center_y = SCREEN_HEIGHT/2
        self.player.center_x = SCREEN_WIDTH/2
        self.all_sprites.append(self.player)

        # Set up for health and mana bars
        self.max_health = self.player.getMaxHealth()
        self.current_health = self.player.getCurrentHealth()
        self.max_mana = self.player.getMaxMana()
        self.current_mana = self.player.getCurrentMana()

        # Draw spell bar UI sprites, then add spell images inside them
        centers = [SCREEN_WIDTH*0.400, SCREEN_WIDTH*0.470, SCREEN_WIDTH*0.540, SCREEN_WIDTH*0.610, SCREEN_WIDTH*0.700]
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


    def on_show(self):
        # Set the background color
        arcade.set_background_color(arcade.color.GRAY)

    def on_update(self, delta_time: float):
        global player, game, CURRENT_ROUND, gamePaused
        # If paused, don't update anything
        if gamePaused:
            return

        # Keep updating the player's current health and mana
        self.current_health = self.player.getCurrentHealth()
        self.current_mana = self.player.getCurrentMana()

        # Keep weapon with the player when swinging
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

        # Did an enemy touch you? --- player can only be hit every 0.75 seconds after being hit before
        enemy_damage = 35 * (1.0 + (CURRENT_ROUND / 10))
        if self.player.collides_with_list(self.basic_enemies_list):
            if self.playerCanBeHit == True:
                self.player.takeDamage(enemy_damage)
                print("Enemy dealth {} damage.".format(enemy_damage))
                self.playerCanBeHit = False
                arcade.schedule(self.setPlayerHit, 0.75)

        boss_damage = 200 * (1.0 + (CURRENT_ROUND / 10))
        if self.player.collides_with_list(self.boss_enemies_list):
            if self.playerCanBeHit == True:
                self.player.takeDamage(boss_damage)
                print("Enemy dealth {} damage.".format(boss_damage))
                self.playerCanBeHit = False
                arcade.schedule(self.setPlayerHit, 0.75)

        # Did you die?
        if self.current_health <= 0:
            # YOU DIED - END THE ROUND
            # Freeze screen and pop up something saying you died, or take to summary screen, or take to summary screen AFTER popup message, etc
            print("ROUND OVER - PLAYER HAS DIED!")
            self.roundSummary("Lost")
            self.player.player_current_health = self.player.getMaxHealth()

        # Killed all enemies in round?
        if self.enemies_killed >= self.total_enemy_count:
            # END THE ROUND
            print("ROUND OVER - ALL ENEMIES KILLED!")
            self.roundSummary("Won")
            self.player.player_current_health = self.player.getMaxHealth()

        # Have enemies follow the player
        for enemy in self.basic_enemies_list:
            enemy.follow_sprite(self.player)

        if self.bossSpawned:
            for enemy in self.boss_enemies_list:
                enemy.follow_sprite(self.player)

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

        arcade.draw_text("Trinket", SCREEN_WIDTH*0.7, SCREEN_HEIGHT*0.025, arcade.color.BLACK, 16, bold=True, anchor_x="center")

        # Draw player name
        arcade.draw_text(CURRENT_CHAR, self.player.center_x, self.player.top+17.5, arcade.color.WHITE, 16, bold=True, anchor_x="center")

        # Draw health bar
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+12.5, 70, 10, arcade.color.BLACK)
        self.hp_percent = self.current_health / self.max_health
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.hp_percent))/2), self.player.top+13, 69.7*self.hp_percent, 9.7, arcade.color.RED)

        # Draw mana bar
        arcade.draw_rectangle_outline(self.player.center_x, self.player.top+2, 70, 10, arcade.color.BLACK)
        self.mana_percent = self.current_mana / self.max_mana
        arcade.draw_rectangle_filled(self.player.center_x - ((69.7 - (69.7*self.mana_percent))/2), self.player.top+2, 69.7*self.mana_percent, 9.7, arcade.color.BLUE)

        # Draw enemy health bars
        for enemy in self.basic_enemies_list:
            arcade.draw_rectangle_outline(enemy.center_x, enemy.top+10, 70, 10, arcade.color.BLACK)
            hp_percent = enemy.enemy_current_health / enemy.enemy_max_health
            arcade.draw_rectangle_filled(enemy.center_x - ((69.7 - (69.7*hp_percent))/2), enemy.top+10, 69.7*hp_percent, 9.7, arcade.color.RED)

        for enemy in self.caster_enemies_list:
            arcade.draw_rectangle_outline(enemy.center_x, enemy.top+10, 70, 10, arcade.color.BLACK)
            hp_percent = enemy.enemy_current_health / enemy.enemy_max_health
            arcade.draw_rectangle_filled(enemy.center_x - ((69.7 - (69.7*hp_percent))/2), enemy.top+10, 69.7*hp_percent, 9.7, arcade.color.RED)

        for enemy in self.boss_enemies_list:
            arcade.draw_rectangle_outline(enemy.center_x, enemy.top+10, 70, 10, arcade.color.BLACK)
            hp_percent = enemy.enemy_current_health / enemy.enemy_max_health
            arcade.draw_rectangle_filled(enemy.center_x - ((69.7 - (69.7*hp_percent))/2), enemy.top+10, 69.7*hp_percent, 9.7, arcade.color.RED)

        # Add spell names to UI slots
        centers = [SCREEN_WIDTH*0.400, SCREEN_WIDTH*0.470, SCREEN_WIDTH*0.540, SCREEN_WIDTH*0.610, SCREEN_WIDTH*0.700]
        num_spells = len(self.player.spells)
        if num_spells > 0:
            for i in range(num_spells):
                arcade.draw_text(self.player.spells[i], centers[i], SCREEN_HEIGHT*0.08, arcade.color.BLACK, 14, bold=True, anchor_x="center")

        # Add spell & trinket cooldown timers if they are on cooldown
        if self.spell1_cooldown > 0:
            arcade.draw_text("X", SCREEN_WIDTH*0.400, SCREEN_HEIGHT*0.06, arcade.color.BLACK, 48, bold=True, anchor_x="center")
            arcade.draw_text(str(self.spell1_cooldown), SCREEN_WIDTH*0.400, SCREEN_HEIGHT*0.015, arcade.color.BLACK, 25, bold=True, anchor_x="center")
        if self.spell2_cooldown > 0:
            arcade.draw_text("X", SCREEN_WIDTH*0.470, SCREEN_HEIGHT*0.06, arcade.color.BLACK, 48, bold=True, anchor_x="center")
            arcade.draw_text(str(self.spell2_cooldown), SCREEN_WIDTH*0.470, SCREEN_HEIGHT*0.015, arcade.color.BLACK, 25, bold=True, anchor_x="center")
        if self.spell3_cooldown > 0:
            arcade.draw_text("X", SCREEN_WIDTH*0.540, SCREEN_HEIGHT*0.06, arcade.color.BLACK, 48, bold=True, anchor_x="center")
            arcade.draw_text(str(self.spell3_cooldown), SCREEN_WIDTH*0.540, SCREEN_HEIGHT*0.015, arcade.color.BLACK, 25, bold=True, anchor_x="center")
        if self.spell4_cooldown > 0:
            arcade.draw_text("X", SCREEN_WIDTH*0.610, SCREEN_HEIGHT*0.06, arcade.color.BLACK, 48, bold=True, anchor_x="center")
            arcade.draw_text(str(self.spell4_cooldown), SCREEN_WIDTH*0.610, SCREEN_HEIGHT*0.015, arcade.color.BLACK, 25, bold=True, anchor_x="center")
        #if self.trinket_cooldown > 0:
        #    arcade.draw_text(self.trinket_cooldown, SCREEN_WIDTH*0.675, SCREEN_HEIGHT*0.08, arcade.color.BLACK, 14, bold=True, anchor_x="center")


        self.all_sprites.draw()

    def setPlayerHit(self, delta_time: float):
        self.playerCanBeHit = True
        arcade.unschedule(self.setPlayerHit)

    def casterShoot(self, delta_time: float):
        import math

        if len(self.caster_enemies_list) > 0:
            if self.player.isVisible == True:
                for enemy in self.caster_enemies_list:
                    attack_speed = 15

                    # Position the start at the enemy's current location
                    start_x = enemy.center_x
                    start_y = enemy.center_y

                    # Get the destination location for the bullet
                    dest_x = self.player.center_x
                    dest_y = self.player.center_y

                    # Do math to calculate how to get the bullet to the destination.
                    # Calculation the angle in radians between the start points
                    # and end points. This is the angle the bullet will travel.
                    x_diff = dest_x - start_x
                    y_diff = dest_y - start_y
                    angle = math.atan2(y_diff, x_diff)

                    bolt = CasterEnemyAttack("images/caster_bolt.png", 0.8)
                    bolt.center_x = start_x
                    bolt.center_y = start_y

                    # Angle the bullet sprite
                    bolt.angle = math.degrees(angle)

                    # Taking into account the angle, calculate our change_x
                    # and change_y. Velocity is how fast the bullet travels.
                    bolt.change_x = math.cos(angle) * attack_speed
                    bolt.change_y = math.sin(angle) * attack_speed

                    self.caster_attack_list.append(bolt)
                    self.all_sprites.append(bolt)

    def regenMana(self, delta_time: float):
        if self.player.getCurrentMana() < self.player.getMaxMana():
            self.player.player_current_mana += self.player.player_max_mana*0.05

        if self.player.getCurrentMana() > self.player.getMaxMana():
                self.player.player_current_mana = self.player.player_max_mana

    def add_enemy(self, delta_time: float):
        global CURRENT_ROUND, gamePaused
        
        if gamePaused:
            return

        if self.current_enemy_count <= self.total_enemy_count:
            if self.current_enemy_count % 5 == 0:
                # Spawn caster enemy
                if self.player.level < 6:
                    caster_enemy_health = 150 + CURRENT_ROUND*50
                else:
                    caster_enemy_health = 150 + CURRENT_ROUND*100

                # First, create the new enemy sprite
                caster_enemy = EnemySprite("images/caster_sprite.png", 0.8)
                caster_enemy.setup(caster_enemy_health) # SET'S ENEMY HEALTH

                # Set its position to a random x position and y position
                caster_enemy.top = random.randint(50, SCREEN_HEIGHT)
                caster_enemy.left = random.randint(10, SCREEN_WIDTH - 10)

                # INITIAL enemy velocity -- it changes once they see the player
                caster_enemy.velocity = (0, 0)

                # Add it to the enemies list and all_sprites list
                self.caster_enemies_list.append(caster_enemy)
                self.all_sprites.append(caster_enemy)
                self.current_enemy_count += 1

            if CURRENT_ROUND % 4 == 0 and self.bossSpawned == False:
                self.bossSpawned = True
                # Spawn a boss enemy
                boss_enemy_health = 4000 + CURRENT_ROUND*700

                # First, create the new enemy sprite
                boss_enemy = EnemySprite("images/boss_sprite.png", 1.3)
                boss_enemy.setup(boss_enemy_health) # SET'S ENEMY HEALTH

                # Set its position to a random x and y position
                boss_enemy.top = random.randint(50, SCREEN_HEIGHT + 80)
                boss_enemy.left = random.choice([random.randint(-80, -5), random.randint(SCREEN_WIDTH+5, SCREEN_WIDTH+80)])

                # INITIAL enemy velocity -- it changes once they see the player
                boss_enemy.velocity = (0, -2.0)

                # Add it to the enemies list and all_sprites list
                self.boss_enemies_list.append(boss_enemy)
                self.all_sprites.append(boss_enemy)
                self.current_enemy_count += 1
            
            # Now spawn basic enemy like normal
            if self.player.level < 6:
                basic_enemy_health = 150 + CURRENT_ROUND*50
            else:
                basic_enemy_health = 150 + CURRENT_ROUND*100

            # First, create the new enemy sprite
            enemy = EnemySprite("images/enemy_sprite.png", 0.8)
            enemy.setup(basic_enemy_health) # SET'S ENEMY HEALTH

            # Set its position to a random x and y positon but off the screen
            enemy.top = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 80)
            enemy.left = random.choice([random.randint(-80, -5), random.randint(SCREEN_WIDTH+5, SCREEN_WIDTH+80)])

            # INITIAL enemy velocity -- it changes once they see the player
            enemy.velocity = (0, -2)

            # Add it to the enemies list and all_sprites list
            self.basic_enemies_list.append(enemy)
            self.all_sprites.append(enemy)
            self.current_enemy_count += 1
        else:
            return

    def roundSummary(self, result):
        global game, CURRENT_ROUND, CURRENT_CHAR
        # Update DB with new stats/items/etc gained from round, then go to summary view for player to see the summary of the round including gained stats/items
        # Will need to check for character levelup after each round, whether win or lose
        if result == "Won":
            # Give player stats necessary AND update curr_round_num in DB to +1
            exp_earned = (100 * self.enemies_killed) + (CURRENT_ROUND * (CURRENT_ROUND + 100)) + (100*CURRENT_ROUND if self.bossSpawned else 0)
            self.player.current_exp += exp_earned
            CURRENT_ROUND += 1

            leveledUp = False

            # Check if levelup
            while True:
                if self.player.current_exp >= self.game_settings.level_exp_requirements[self.player.level+1]:
                    # LEVELUP -- setup new stat point increases and update DB with new stats for character
                    leveledUp = True
                    self.player.current_exp -= self.game_settings.level_exp_requirements[self.player.level+1]
                    self.player.level += 1
                    self.player.strength += 4 + self.player.level
                    self.player.agility += 4 + self.player.level
                    self.player.intellect += 4 + self.player.level
                    self.player.stamina += 4 + self.player.level
                    
                    query = """UPDATE characters SET char_level = ?, char_strength = ?, char_agility = ?, char_intellect = ?, char_stamina = ?, curr_exp = ?, curr_round_num = ? WHERE char_name = ?"""
                    data = (self.player.level, self.player.strength, self.player.agility, self.player.intellect, self.player.stamina, self.player.current_exp, CURRENT_ROUND, CURRENT_CHAR)
                    self.updateStats(query, data)
                else:
                    query = """UPDATE characters SET curr_exp = ?, curr_round_num = ? WHERE char_name = ?"""
                    data = (self.player.current_exp, CURRENT_ROUND, CURRENT_CHAR)
                    self.updateStats(query, data)
                    break

            # Change view to summary view that has continue button that brings the player back to pregame lobby
            game.show_view(RoundSummaryView("WIN", self.enemies_killed, leveledUp, exp_earned))
        if result == "Lost":
            # Still reward player with experience from enemies killed, but nothing else UNLESS leveled up
            exp_earned = (70 * self.enemies_killed)
            self.player.current_exp += exp_earned

            leveledUp = False

            # Check if levelup
            while True:
                if self.player.current_exp >= self.game_settings.level_exp_requirements[self.player.level+1]:
                    # LEVELUP -- setup new stat point increases and update DB with new stats for character
                    leveledUp = True
                    self.player.current_exp -= self.game_settings.level_exp_requirements[self.player.level+1]
                    self.player.level += 1
                    self.player.strength += 4 + self.player.level
                    self.player.agility += 4 + self.player.level
                    self.player.intellect += 4 + self.player.level
                    self.player.stamina += 4 + self.player.level
                    
                    query = """UPDATE characters SET char_level = ?, char_strength = ?, char_agility = ?, char_intellect = ?, char_stamina = ?, curr_exp = ?, curr_round_num = ? WHERE char_name = ?"""
                    data = (self.player.level, self.player.strength, self.player.agility, self.player.intellect, self.player.stamina, self.player.current_exp, CURRENT_ROUND, CURRENT_CHAR)
                    self.updateStats(query, data)
                else:
                    query = """UPDATE characters SET curr_exp = ? WHERE char_name = ?"""
                    data = (self.player.current_exp, CURRENT_CHAR)
                    self.updateStats(query, data)
                    break

            # Change view to summary view that has continue button that brings the player back to pregame lobby
            game.show_view(RoundSummaryView("LOSS", self.enemies_killed, leveledUp, exp_earned))

    def updateStats(self, query, data):
        c = db.conn.cursor()
        try:
            c.execute(query, data)
            db.conn.commit()
            print("Record updated successfully!")
        except Error as e:
            print(e)
            exit()

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
        elif key == arcade.key.E or key == arcade.key.KEY_1:
            # CHECK IF PLAYER HAS THE REQUIRED MANA FOR SPELL BEFORE CASTING AND SUBTRACTING MANA
            if len(self.player.spells) >= 1:
                if self.spell1_cooldown == 0:
                    spell = self.player.spells[0]
                    if self.current_mana >= self.max_mana*0.125:
                        self.player.castSpell(spell)
        elif key == arcade.key.R or key == arcade.key.KEY_2:
            if len(self.player.spells) >= 2:
                if self.spell2_cooldown == 0:
                    spell = self.player.spells[1]
                    if self.current_mana >= self.max_mana*0.125:
                        self.player.castSpell(spell)
        elif key == arcade.key.F or key == arcade.key.KEY_3:
            if len(self.player.spells) >= 3:
                if self.spell3_cooldown == 0:
                    spell = self.player.spells[2]
                    if self.current_mana >= self.max_mana*0.125:
                        self.player.castSpell(spell)
        elif key == arcade.key.C or key == arcade.key.KEY_4:
            if len(self.player.spells) >= 4:
                if self.spell4_cooldown == 0:
                    spell = self.player.spells[3]
                    if self.current_mana >= self.max_mana*0.25:
                        self.player.castSpell(spell)

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

        if self.char_class == "Assassin" or self.char_class == "Warrior" or self.char_class == "Void Stalker":
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

    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

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

        self.sword.turn_right(10)

        self.swing_timer += 1/80
        if self.swing_timer >= 20/80:
            self.sword.center_x = SCREEN_WIDTH + 200
            self.sword.remove_from_sprite_lists()
            self.sword.kill()
            self.swingingWeapon = False
            arcade.unschedule(self.swingWeapon)
            return

    def spell1Countdown(self, delta_time: float):
        if self.spell1_cooldown == 0:
            arcade.unschedule(self.spell1Countdown)
            return
        else:
            self.spell1_cooldown -= 1

    def spell2Countdown(self, delta_time: float):
        if self.spell2_cooldown == 0:
            arcade.unschedule(self.spell2Countdown)
            return
        else:
            self.spell2_cooldown -= 1

    def spell3Countdown(self, delta_time: float):
        if self.spell3_cooldown == 0:
            arcade.unschedule(self.spell3Countdown)
            return
        else:
            self.spell3_cooldown -= 1

    def spell4Countdown(self, delta_time: float):
        if self.spell4_cooldown == 0:
            arcade.unschedule(self.spell4Countdown)
            return
        else:
            self.spell4_cooldown -= 1

class RoundSummaryView(arcade.View):
    def __init__(self, result, enemies_killed, leveledUp, exp_earned):
        super().__init__()
        self.result = result
        self.enemies_killed = enemies_killed
        self.leveledUp = leveledUp
        self.exp_earned = exp_earned

        self.theme = getButtonThemes()
        self.button_list.append(ContinueButton(self, SCREEN_WIDTH/2, SCREEN_HEIGHT*0.1, 200, 50, theme=self.theme))

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        global onslaught
        arcade.start_render()

        arcade.draw_text("Round Summary", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.7, arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text("Result: {}".format(self.result), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.6, arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Enemies killed: {}".format(self.enemies_killed), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.55, arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Experience earned: {}".format(self.exp_earned), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.5, arcade.color.WHITE, font_size=30, anchor_x="center")

        if self.leveledUp:
            arcade.draw_text("LEVEL UP!", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.4, arcade.color.WHITE, font_size=40, anchor_x="center")
            arcade.draw_text("-------------", SCREEN_WIDTH/2, SCREEN_HEIGHT*0.385, arcade.color.WHITE, font_size=40, anchor_x="center")
            arcade.draw_text("Strength +{}".format(4+int(onslaught.player.level)), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.35, arcade.color.WHITE, font_size=20, anchor_x="center")
            arcade.draw_text("Agility +{}".format(4+int(onslaught.player.level)), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.325, arcade.color.WHITE, font_size=20, anchor_x="center")
            arcade.draw_text("Intellect +{}".format(4+int(onslaught.player.level)), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.3, arcade.color.WHITE, font_size=20, anchor_x="center")
            arcade.draw_text("Stamina +{}".format(4+int(onslaught.player.level)), SCREEN_WIDTH/2, SCREEN_HEIGHT*0.275, arcade.color.WHITE, font_size=20, anchor_x="center")

        for button in self.button_list:
            button.draw()

class EnemySprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if onslaught.char_class == "Assassin" or onslaught.char_class == "Warrior" or onslaught.char_class == "Void Stalker":
            if self.collides_with_sprite(onslaught.sword):
                if onslaught.enemyHit == False:
                    onslaught.enemyHit = True
                    self.enemy_current_health -= onslaught.player.basicDamage()
                    if onslaught.voidTipActive == True:
                        onslaught.voidTipActive = False
        elif onslaught.char_class == "Mage":
            if self.collides_with_list(onslaught.basic_attack_list):
                if onslaught.enemyHit == False:
                    onslaught.enemyHit = True
                    onslaught.deleteAttack = True
                    self.enemy_current_health -= onslaught.player.basicDamage()
            else:
                onslaught.enemyHit = False

        # Need a check if collides with spell, but have to determine how to know what spell to know how much damage to take, etc

        if self.enemy_current_health <= 0:
            self.remove_from_sprite_lists()
            onslaught.enemies_killed += 1

    def setup(self, health):
        self.enemy_max_health = health
        self.enemy_current_health = self.enemy_max_health
        self.movementAffected = False

    def takeDamage(self, dmg):
        self.enemy_current_health -= dmg

    def follow_sprite(self, player_sprite):
        global onslaught
        import math
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Random 1 in 100 chance that we'll change from our old direction and
        # then re-aim toward the player
        if random.randrange(25) == 0:
            start_x = self.center_x
            start_y = self.center_y

            # Get the destination location for the bullet
            dest_x = player_sprite.center_x
            dest_y = player_sprite.center_y

            # Do math to calculate how to get the bullet to the destination.
            # Calculation the angle in radians between the start points
            # and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # Taking into account the angle, calculate our change_x
            # and change_y. Velocity is how fast the bullet travels.
            if onslaught.player.isVisible == True:
                if self.movementAffected == False:
                    self.velocity = (math.cos(angle) * 2.5, math.sin(angle) * 2.5)
                else:
                    self.velocity = (math.cos(angle) * onslaught.enemy_velocity, math.sin(angle) * onslaught.enemy_velocity)
                    arcade.schedule(self.unsetMovementAffected, 3.0)
            else:
                self.velocity = (0, 0)
            #self.change_x = math.cos(angle) * 1.5
            #self.change_y = math.sin(angle) * 1.5

    def unsetMovementAffected(self, delta_time: float):
        self.movementAffected = False
        arcade.unschedule(self.unsetMovementAffected)

class BasicAttackSprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if self.center_y >= SCREEN_HEIGHT or self.center_x >= SCREEN_WIDTH or self.center_x <= 0 or self.center_y <= 0:
            self.remove_from_sprite_lists()

        if self.collides_with_list(onslaught.basic_enemies_list):
            if onslaught.deleteAttack:
                self.remove_from_sprite_lists()
                onslaught.deleteAttack = False
        elif self.collides_with_list(onslaught.caster_enemies_list):
            if onslaught.deleteAttack:
                self.remove_from_sprite_lists()
                onslaught.deleteAttack = False
        elif self.collides_with_list(onslaught.boss_enemies_list):
            if onslaught.deleteAttack:
                self.remove_from_sprite_lists()
                onslaught.deleteAttack = False

class CasterEnemyAttack(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if self.center_y >= SCREEN_HEIGHT or self.center_x >= SCREEN_WIDTH or self.center_x <= 0 or self.center_y <= 0:
            self.remove_from_sprite_lists()

        if self.collides_with_sprite(onslaught.player):
                self.remove_from_sprite_lists()
                if onslaught.playerCanBeHit == True:
                    enemy_damage = 75 * (1.0 + (CURRENT_ROUND / 10))
                    onslaught.player.takeDamage(enemy_damage)

class WeaponSprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught

        if onslaught.swingingWeapon == False:
            self.remove_from_sprite_lists()

        #if self.collides_with_list(onslaught.basic_enemies_list):
            #self.remove_from_sprite_lists()

class SpellSprite(arcade.Sprite):
    def update(self):
        super().update()
        global onslaught
        import numpy as np

        if self.center_y >= SCREEN_HEIGHT or self.center_x >= SCREEN_WIDTH or self.center_x <= 0 or self.center_y <= 0:
            self.remove_from_sprite_lists()

        if "freezing" in self.name.lower():
            dist = np.linalg.norm(np.array([MageSpells.nova_start_x, MageSpells.nova_start_y]) - np.array([self.center_x, self.center_y]))
            if dist >= 200:
                self.remove_from_sprite_lists()

        # Generate a list of all sprites that collided with the spell.
        basic_enemy_hit_list = arcade.check_for_collision_with_list(self, onslaught.basic_enemies_list)
        caster_enemy_hit_list = arcade.check_for_collision_with_list(self, onslaught.caster_enemies_list)
        boss_enemy_hit_list = arcade.check_for_collision_with_list(self, onslaught.boss_enemies_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for enemy in basic_enemy_hit_list:
            if "freezing" not in self.name.lower():
                self.remove_from_sprite_lists()
            enemy.movementAffected = True
            enemy.takeDamage(self.dmg)
            print("Spell dealt {} damage to an enemy.".format(self.dmg))

            if "grip" in self.name.lower():
                onslaught.playerCanBeHit = False
                enemy.center_x = onslaught.player.center_x
                enemy.center_y = onslaught.player.center_y
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)

            if self.speedEffect != 0:
                onslaught.enemy_velocity -= onslaught.enemy_velocity * self.speedEffect
                arcade.schedule(self.resetEnemyVelocity, self.speedDuration)

        for enemy in caster_enemy_hit_list:
            if "freezing" not in self.name.lower():
                self.remove_from_sprite_lists()
            enemy.takeDamage(self.dmg)
            print("Spell dealt {} damage to an enemy.".format(self.dmg))

            if "grip" in self.name.lower():
                onslaught.playerCanBeHit = False
                enemy.center_x = onslaught.player.center_x
                enemy.center_y = onslaught.player.center_y
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)

        for enemy in boss_enemy_hit_list:
            if "freezing" not in self.name.lower():
                self.remove_from_sprite_lists()
            enemy.movementAffected = True
            enemy.takeDamage(self.dmg)
            print("Spell dealt {} damage to an enemy.".format(self.dmg))

            if "grip" in self.name.lower():
                onslaught.playerCanBeHit = False
                enemy.center_x = onslaught.player.center_x
                enemy.center_y = onslaught.player.center_y
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)

            if self.speedEffect != 0:
                onslaught.enemy_velocity -= onslaught.enemy_velocity * self.speedEffect
                arcade.schedule(self.resetEnemyVelocity, self.speedDuration)

    def setup(self, name, dmg, speedEffect, speedDuration=3.0):
        self.name = name
        self.dmg = dmg
        self.speedEffect = speedEffect
        self.speedDuration = speedDuration

    def resetEnemyVelocity(self, delta_time: float):
        onslaught.enemy_velocity = 2.5
        arcade.unschedule(self.resetEnemyVelocity)

class Character(arcade.Sprite):
    def setup(self):
        self.game_settings = GameSettings()

        self.player_class = self.getCharClass()

        # (int(char_id), str(CURRENT_ACCT_ID), str(self.char_name), str(char_texture), str(self.char_class), int(char_level), int(char_strength), int(char_stamina), int(char_intellect), int(char_agility), int(char_move_speed), int(curr_exp), int(curr_pvp_rank), int(curr_round_num))
        self.player_stats = self.getCharStats()[0]

        self.level = self.player_stats[5]

        self.strength = self.player_stats[6]
        self.stamina = self.player_stats[7]
        self.intellect = self.player_stats[8]
        self.agility = self.player_stats[9]

        self.player_max_health = self.stamina * self.game_settings.STAMINA_HEALTH_MULTIPLIER
        self.player_current_health = self.player_max_health # start current health at the max health
        self.player_max_mana = self.intellect * self.game_settings.INTELLECT_MANA_MULTIPLIER
        self.player_current_mana = self.player_max_mana

        self.attack_crit = 0.05 + self.agility * self.game_settings.AGILITY_CRIT_MULTIPLIER
        self.spell_crit = 0.05 + self.intellect * self.game_settings.INTELLECT_CRIT_MULTIPLIER

        self.attack_power = self.agility * self.game_settings.AGILITY_AP_MULTIPLIER + self.strength * self.game_settings.STRENGTH_AP_MULTIPLIER
        self.spell_power = self.intellect * self.game_settings.INTELLECT_SP_MULTIPLIER

        self.current_exp = self.player_stats[11]

        self.isVisible = True # used to check if player can be seen

        self.spells = self.getCharSpells() # list of spell names for the class

    def update(self):
        super().update()
        if self.player_current_mana <= 0:
            self.player_current_mana = 0

    def castSpell(self, spell):
        global mouse_x, mouse_y
        if self.player_class == "Assassin":
            if "poison" in spell.lower():
                AssassinSpells.poisonShuriken()
            elif "ass" in spell.lower():
                AssassinSpells.assassinate()
            elif "vanish" in spell.lower():
                AssassinSpells.vanish()
            elif "blitz" in spell.lower():
                AssassinSpells.shurikenBlitz()
        elif self.player_class == "Mage":
            if "eruption" in spell.lower():
                MageSpells.eruption()
            elif "teleport" in spell.lower():
                MageSpells.teleport()
            elif "freezing" in spell.lower():
                MageSpells.freezingNova()
            elif "glacial" in spell.lower():
                MageSpells.glacialComet()
        elif self.player_class == "Void Stalker":
            if "void-tipped" in spell.lower():
                VoidStalkerSpells.voidTippedBlade()
            elif "grip" in spell.lower():
                VoidStalkerSpells.shadowGrip()
            elif "nova" in spell.lower():
                VoidStalkerSpells.voidNova()
            elif "enter" in spell.lower():
                VoidStalkerSpells.enterTheVoid()

    def getMaxHealth(self):
        return self.player_max_health

    def getCurrentHealth(self):
        return self.player_current_health

    def getMaxMana(self):
        return self.player_max_mana

    def getCurrentMana(self):
        return self.player_current_mana

    def takeDamage(self, dmg):
        self.player_current_health -= dmg

    def loseMana(self, mana):
        self.player_current_mana -= mana

    def basicDamage(self):
        global onslaught
        if self.player_class == "Assassin" or self.player_class == "Warrior" or self.player_class == "Void Stalker":
            damage = 3 + self.attack_power + (0 if onslaught.voidTipActive == False else (self.attack_power*1.5 + self.spell_power*0.5))
            if random.random() <= self.attack_crit:
                damage *= 1.65
                print("Player critical strike hit for {}!".format(damage))
                return damage
            else:
                print("Player attack hit for {}".format(damage))
                return damage
        elif self.player_class == "Mage":
            damage = 5 + self.spell_power
            print("Caster crit chance: {}".format(self.spell_crit))
            if random.random() <= self.spell_crit:
                damage *= 1.65
                print("Player critical strike hit for {}!".format(damage))
                return damage
            else:
                print("Player attack hit for {}".format(damage))
                return damage

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

    def getCharSpells(self):
        spells = []
        if self.level >= 2:
            # Insert level 2 spell name
            if self.player_class == "Assassin":
                spells.append("Poison\nShuriken")
            elif self.player_class == "Mage":
                spells.append("Eruption")
            elif self.player_class == "Warrior":
                pass
            elif self.player_class == "Void Stalker":
                spells.append("Void-Tipped\nBlade")
        
        if self.level >= 4:
            # Insert level 4 spell name
            if self.player_class == "Assassin":
                spells.append("Assassinate")
            elif self.player_class == "Mage":
                spells.append("Teleport")
            elif self.player_class == "Warrior":
                pass
            elif self.player_class == "Void Stalker":
                spells.append("Shadow\nGrip")

        if self.level >= 6:
            # Insert level 6 spell name
            if self.player_class == "Assassin":
                spells.append("Vanish")
            elif self.player_class == "Mage":
                spells.append("Freezing\nNova")
            elif self.player_class == "Warrior":
                pass
            elif self.player_class == "Void Stalker":
                spells.append("Void\nNova")

        if self.level >= 8:
            # Insert level 8 spell name
            if self.player_class == "Assassin":
                spells.append("Shuriken\nBlitz")
            elif self.player_class == "Mage":
                spells.append("Glacial\nComet")
            elif self.player_class == "Warrior":
                pass
            elif self.player_class == "Void Stalker":
                spells.append("Enter\nthe\nVoid")

        return spells


class AssassinSpells:
    blitz_timer = 0.0

    def startShurikenBlitz(delta_time: float):
        global onslaught
        import math

        if AssassinSpells.blitz_timer < 4.0:
            AssassinSpells.blitz_timer += 0.1
            dmg = 10 + (onslaught.player.attack_power * 0.5)

            x = mouse_x
            y = mouse_y

            # Crit?
            if random.random() <= onslaught.player.attack_crit:
                dmg *= 1.65
            shuriken = SpellSprite("images/shuriken.png", 0.1)
            shuriken.setup("Shuriken Blitz", dmg, 0.3)
            shuriken_speed = 40

            start_x = onslaught.player.center_x
            start_y = onslaught.player.center_y
            shuriken.center_x = start_x
            shuriken.center_y = start_y

            dest_x = x
            dest_y = y

            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            shuriken.angle = math.degrees(angle)
            shuriken.change_x = math.cos(angle) * shuriken_speed
            shuriken.change_y = math.sin(angle) * shuriken_speed

            onslaught.spell_sprite_list.append(shuriken)
            onslaught.all_sprites.append(shuriken)
            onslaught.player.loseMana(onslaught.max_mana*0.125)
        else:
            arcade.unschedule(AssassinSpells.startShurikenBlitz)
            AssassinSpells.blitz_timer = 0

    def endInvisibility(self):
        global onslaught
        onslaught.player.isVisible = True
        arcade.set_background_color(arcade.color.GRAY)
        arcade.unschedule(AssassinSpells.endInvisibility)

    def endInvulnerability(delta_time: float):
        global onslaught
        onslaught.playerCanBeHit = True
        arcade.unschedule(AssassinSpells.endInvulnerability)

    def poisonShuriken():
        import math
        global onslaught, mouse_x, mouse_y
        """ Throw a poison-tipped shuriken in the direction of your mouse that deals 100 damage + 160% of attack power to any enemy hit and slows them by 50% for 3 seconds. """
        dmg = 100 + (onslaught.player.attack_power * 1.6)

        #pos = pag.position() #queryMousePosition()
        #print(pos)
        x = mouse_x
        y = mouse_y
        
        degrees = [-75, 0, 75]

        for i in range(3):
            # Crit?
            if random.random() <= onslaught.player.attack_crit:
                dmg *= 1.65
            shuriken = SpellSprite("images/shuriken.png", 0.1)
            shuriken.setup("Poison Shuriken", dmg, 0.5)
            shuriken_speed = 40

            start_x = onslaught.player.center_x
            start_y = onslaught.player.center_y
            shuriken.center_x = start_x
            shuriken.center_y = start_y

            dest_x = x
            dest_y = y

            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            shuriken.angle = math.degrees(angle)
            shuriken.change_x = math.cos(angle+degrees[i]) * shuriken_speed
            shuriken.change_y = math.sin(angle+degrees[i]) * shuriken_speed

            onslaught.spell_sprite_list.append(shuriken)
            onslaught.all_sprites.append(shuriken)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell1_cooldown = 6
        arcade.schedule(onslaught.spell1Countdown, 1.0)

    def assassinate():
        import numpy as np
        global onslaught, mouse_x, mouse_y
        """ Step through the shadows to an enemy target and stab them in the back for 150 damage + 180% of attack power. Always a critical hit. Must have mouse cursor on an enemy to perform. """
        dmg = 150 + (onslaught.player.attack_power * 1.8)
        crit = False

        # Crit?
        if random.random() <= onslaught.player.attack_crit:
            dmg *= 1.65
            crit = True

        x = mouse_x
        y = mouse_y

        for enemy in onslaught.basic_enemies_list:
            # get euclidean distance to enemy.center_x and see if it's close enough
            dist = np.linalg.norm(np.array([x, y]) - np.array([enemy.center_x, enemy.center_y]))
            if dist <= 40:
                # TELEPORT PLAYER AND DEAL DAMAGE, AND STOP CHECKING ENEMIES
                onslaught.playerCanBeHit = False
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)
                onslaught.player.loseMana(onslaught.max_mana*0.125)
                onslaught.player.center_x = enemy.center_x
                onslaught.player.center_y = enemy.center_y
                enemy.takeDamage(dmg)
                onslaught.spell2_cooldown = 12
                arcade.schedule(onslaught.spell2Countdown, 1.0)
                print("Assassinate {} {} damage to an enemy.".format("dealt" if crit == False else "CRIT", dmg))
                break

        for enemy in onslaught.caster_enemies_list:
            # get euclidean distance to enemy.center_x and see if it's close enough
            dist = np.linalg.norm(np.array([x, y]) - np.array([enemy.center_x, enemy.center_y]))
            if dist <= 40:
                # TELEPORT PLAYER AND DEAL DAMAGE, AND STOP CHECKING ENEMIES
                onslaught.playerCanBeHit = False
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)
                onslaught.player.loseMana(onslaught.max_mana*0.125)
                onslaught.player.center_x = enemy.center_x
                onslaught.player.center_y = enemy.center_y
                enemy.takeDamage(dmg)
                onslaught.spell2_cooldown = 12
                arcade.schedule(onslaught.spell2Countdown, 1.0)
                print("Assassinate {} {} damage to an enemy.".format("dealt" if crit == False else "CRIT", dmg))
                break

        for enemy in onslaught.boss_enemies_list:
            # get euclidean distance to enemy.center_x and see if it's close enough
            dist = np.linalg.norm(np.array([x, y]) - np.array([enemy.center_x, enemy.center_y]))
            if dist <= 40:
                # TELEPORT PLAYER AND DEAL DAMAGE, AND STOP CHECKING ENEMIES
                onslaught.playerCanBeHit = False
                arcade.schedule(AssassinSpells.endInvulnerability, 1.0)
                onslaught.player.loseMana(onslaught.max_mana*0.125)
                onslaught.player.center_x = enemy.center_x
                onslaught.player.center_y = enemy.center_y
                enemy.takeDamage(dmg)
                onslaught.spell2_cooldown = 12
                arcade.schedule(onslaught.spell2Countdown, 1.0)
                print("Assassinate {} {} damage to an enemy.".format("dealt" if crit == False else "CRIT", dmg))
                break

    def vanish():
        global onslaught
        """ Vanish into the darkness and become hidden from your enemies for 3 seconds. """
        onslaught.player.isVisible = False
        arcade.set_background_color(arcade.color.BLACK)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell3_cooldown = 20
        arcade.schedule(onslaught.spell3Countdown, 1.0)
        arcade.schedule(AssassinSpells.endInvisibility, 3.0)

    def shurikenBlitz():
        """ Launch a barrage of shuriken at the location of your mouse for 4 seconds. Each shuriken deals 10 damage + 50% of attack power and slows the enemy by 30%. """
        arcade.schedule(AssassinSpells.startShurikenBlitz, 0.1)
        onslaught.player.loseMana(onslaught.max_mana*0.25)
        onslaught.spell4_cooldown = 45
        arcade.schedule(onslaught.spell4Countdown, 1.0)

class MageSpells:
    nova_start_x = 0
    nova_start_y = 0

    def eruption():
        """ Explode, shooting fiery comets from all around you that burn any enemy hit for 50 damage + 140% of spell power. """
        import math
        global onslaught
        
        dmg = 50 + (onslaught.player.spell_power * 1.4)
        
        degrees = [30, 60, 90, 120, 150, 180, 210, 240, 270]

        for i in range(9):
            # Crit?
            if random.random() <= onslaught.player.spell_crit:
                dmg *= 1.65
            fireball = SpellSprite("images/fireball.png", 0.5)
            fireball.setup("Eruption", dmg, 0)
            fireball_speed = 20

            start_x = onslaught.player.center_x
            start_y = onslaught.player.center_y
            fireball.center_x = start_x
            fireball.center_y = start_y

            fireball.angle = degrees[i]
            fireball.change_x = math.cos(degrees[i]) * fireball_speed
            fireball.change_y = math.sin(degrees[i]) * fireball_speed

            onslaught.spell_sprite_list.append(fireball)
            onslaught.all_sprites.append(fireball)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell1_cooldown = 6
        arcade.schedule(onslaught.spell1Countdown, 1.0)

    def teleport():
        """ Teleport to your current mouse location.  (OR, Teleport to a location clicked on). """
        global onslaught, mouse_x, mouse_y
        x = mouse_x
        y = mouse_y

        onslaught.player.center_x = x
        onslaught.player.center_y = y
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell2_cooldown = 12
        arcade.schedule(onslaught.spell2Countdown, 1.0)

    def freezingNova():
        """ Freeze all nearby enemies in their place for 3 seconds and deal 25 damage + 80% of spell power. """
        import math
        global onslaught

        MageSpells.nova_start_x = onslaught.player.center_x
        MageSpells.nova_start_y = onslaught.player.center_y
        
        dmg = 0 # 25 + (onslaught.player.spell_power * 0.8)

        # Crit?
        if random.random() <= onslaught.player.spell_crit:
            dmg *= 1.65
        
        degrees = [30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270]

        for i in range(len(degrees)):
            frost = SpellSprite("images/caster_bolt2.png", 0.5)
            frost.setup("Freezing Nova", dmg, 1.0)
            frost_speed = 20

            start_x = onslaught.player.center_x
            start_y = onslaught.player.center_y
            frost.center_x = start_x
            frost.center_y = start_y

            frost.angle = degrees[i]
            frost.change_x = math.cos(degrees[i]) * frost_speed
            frost.change_y = math.sin(degrees[i]) * frost_speed

            onslaught.spell_sprite_list.append(frost)
            onslaught.all_sprites.append(frost)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell3_cooldown = 20
        arcade.schedule(onslaught.spell3Countdown, 1.0)

    def glacialComet():
        global onslaught
        import math
        """ Send a glacial comet soaring toward the direction of your mouse that deals 300 + 200% of spell power to any enemy hit, slowing them by 70% for 3 seconds. """
        dmg = 500 + (onslaught.player.spell_power * 3.0)

        #pos = pag.position() #queryMousePosition()
        #print(pos)
        x = mouse_x
        y = mouse_y

        # Crit?
        if random.random() <= onslaught.player.spell_crit:
            dmg *= 1.65

        comet = SpellSprite("images/caster_bolt.png", 4.0)
        comet.setup("Glacial Comet", dmg, 0.7)
        comet_speed = 30

        start_x = onslaught.player.center_x
        start_y = onslaught.player.center_y
        comet.center_x = start_x
        comet.center_y = start_y

        dest_x = x
        dest_y = y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        comet.angle = math.degrees(angle)
        comet.change_x = math.cos(angle) * comet_speed
        comet.change_y = math.sin(angle) * comet_speed

        onslaught.spell_sprite_list.append(comet)
        onslaught.all_sprites.append(comet)
        onslaught.player.loseMana(onslaught.max_mana*0.25)
        onslaught.spell4_cooldown = 45
        arcade.schedule(onslaught.spell4Countdown, 1.0)

class VoidStalkerSpells:
    bonus_ap = 0
    movespeed_reduction = 0

    def voidTippedBlade():
        global onslaught
        """ Your next basic attack deals 150% of attack power and 50% of spell power.  If the target is a player, the player will have 10% of their mana drained. """
        onslaught.voidTipActive = True
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell1_cooldown = 6
        arcade.schedule(onslaught.spell1Countdown, 1.0)

    def shadowGrip():
        """ Shoot a bolt of shadow in the direction of your mouse. If it hits an enemy, deal 50 damage + 100% of attack power and 75% of spell power, and grip them through the shadows to your current location, immobilizing them for 1 second. """
        global onslaught
        import math

        dmg = 50 + (onslaught.player.attack_power * 1.0 + onslaught.player.spell_power * 0.75)

        #pos = pag.position() #queryMousePosition()
        #print(pos)
        x = mouse_x
        y = mouse_y

        # Crit?
        if random.random() <= onslaught.player.attack_crit:
            dmg *= 1.65

        grip = SpellSprite("images/shadow_ball.png", 0.2)
        grip.setup("Shadow Grip", dmg, 1.0, 1.0) # 100% slow for 1 second
        grip_speed = 30

        start_x = onslaught.player.center_x
        start_y = onslaught.player.center_y
        grip.center_x = start_x
        grip.center_y = start_y

        dest_x = x
        dest_y = y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        grip.angle = math.degrees(angle)
        grip.change_x = math.cos(angle) * grip_speed
        grip.change_y = math.sin(angle) * grip_speed

        onslaught.spell_sprite_list.append(grip)
        onslaught.all_sprites.append(grip)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell2_cooldown = 12
        arcade.schedule(onslaught.spell2Countdown, 1.0)

    def voidNova():
        """ Explode with the power of the void, sending out void bolts in all directions dealing 50 damage + 100% of attack power and 40% of spell power to all enemies hit.  If the target is a player,the player will have 10% of their mana drained. """
        import math
        global onslaught
        
        dmg = 50 + (onslaught.player.attack_power * 1.0 + onslaught.player.spell_power * 0.4)
        
        degrees = [30, 60, 90, 120, 150, 180, 210, 240, 270]

        for i in range(9):
            # Crit?
            if random.random() <= onslaught.player.spell_crit:
                dmg *= 1.65
            fireball = SpellSprite("images/shadow_ball.png", 0.5)
            fireball.setup("Void Nova", dmg, 0)
            fireball_speed = 20

            start_x = onslaught.player.center_x
            start_y = onslaught.player.center_y
            fireball.center_x = start_x
            fireball.center_y = start_y

            fireball.angle = degrees[i]
            fireball.change_x = math.cos(degrees[i]) * fireball_speed
            fireball.change_y = math.sin(degrees[i]) * fireball_speed

            onslaught.spell_sprite_list.append(fireball)
            onslaught.all_sprites.append(fireball)
        onslaught.player.loseMana(onslaught.max_mana*0.125)
        onslaught.spell3_cooldown = 20
        arcade.schedule(onslaught.spell3Countdown, 1.0)

    def enterTheVoid():
        """ Enter the void, stepping into another dimension and becoming unseen by enemies for 8 seconds. While active, you are slowed, but you can attack your enemies undetected and unseen with 25% increased attack power. At the
        end of the duration, you will exit the void from where you entered, becoming visible again. Area effect spells and abilities can still hit you in the void. """
        global onslaught
        onslaught.player.isVisible = False
        arcade.set_background_color(arcade.color.BLACK)
        VoidStalkerSpells.bonus_ap = onslaught.player.attack_power * 0.25
        onslaught.player.attack_power += VoidStalkerSpells.bonus_ap
        VoidStalkerSpells.movespeed_reduction = onslaught.player_velocity * 0.3
        onslaught.player_velocity -= VoidStalkerSpells.movespeed_reduction 
        onslaught.player.loseMana(onslaught.max_mana*0.25)
        onslaught.spell4_cooldown = 45
        arcade.schedule(onslaught.spell4Countdown, 1.0)
        arcade.schedule(VoidStalkerSpells.endEnterTheVoid, 8.0)

    def endEnterTheVoid(delta_time: float):
        global onslaught
        onslaught.player.isVisible = True
        arcade.set_background_color(arcade.color.GRAY)
        onslaught.player.attack_power -= VoidStalkerSpells.bonus_ap
        onslaught.player_velocity += VoidStalkerSpells.movespeed_reduction 
        arcade.unschedule(VoidStalkerSpells.endEnterTheVoid)


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