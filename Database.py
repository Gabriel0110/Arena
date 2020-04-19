import Spending_Tracker
import sqlite3
from sqlite3 import Error
import os
import pyautogui
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.CURRENT_USERNAME = ""

        # Connect to a database, or create + connect at startup
        cwd = os.getcwd()

        self.conn = self.create_connection(cwd + "/arena_db.db")

        self.create_accounts_table = """CREATE TABLE IF NOT EXISTS accounts (
                                        acct_id INTEGER PRIMARY KEY,
                                        acct_username VARCHAR(100) NOT NULL,
                                        acct_password VARCHAR(100) NOT NULL,
                                        acct_email VARCHAR(100) NOT NULL,
                                        acct_creation_date VARCHAR(10) NOT NULL
                                    ); """

        self.create_characters_table = """CREATE TABLE IF NOT EXISTS characters (
                                        char_id INTEGER PRIMARY KEY,
                                        acct_id INTEGER NOT NULL,
                                        char_name VARCHAR(40) NOT NULL,
                                        char_texture VARCHAR(100) NOT NULL,
                                        char_class VARCHAR(30) NOT NULL,
                                        char_level INTEGER NOT NULL,
                                        char_health INTEGER NOT NULL,
                                        char_mana INTEGER NOT NULL,
                                        char_strength INTEGER NOT NULL,
                                        char_stamina INTERGER NOT NULL,
                                        char_intellect INTEGER NOT NULL,
                                        char_agility INTEGER NOT NULL,
                                        char_attk_crit_chance FLOAT NOT NULL,
                                        char_spell_crit_chance FLOAT NOT NULL,
                                        char_spell_power INTEGER NOT NULL,
                                        char_attack_power INTEGER NOT NULL,
                                        char_move_speed FLOAT NOT NULL,
                                        curr_exp INTEGER NOT NULL,
                                        curr_pvp_rank INTEGER NOT NULL
                                    ); """

        self.create_spells_table = """CREATE TABLE IF NOT EXISTS spells (
                                        spell_id INTEGER PRIMARY KEY,
                                        spell_name VARCHAR(64) NOT NULL,
                                        spell_desc VARCHAR(256) NOT NULL,
                                        spell_rank INTEGER NOT NULL,
                                        spell_mana_cost INTEGER NOT NULL,
                                        spell_hasDamage BOOLEAN NOT NULL,
                                        spell_damage INTEGER
                                    ); """

        self.game_stats_table = """CREATE TABLE IF NOT EXISTS game_stats (
                                        char_id INTEGER PRIMARY KEY,
                                        curr_sp_wave INTEGER NOT NULL
                                    ); """

        if self.conn is not None:
            self.create_tables(self.conn, [self.create_accounts_table, self.create_characters_table, self.create_spells_table])
        else:
            print("Error -- no database connection found.")
            exit()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            print("Database connection successful!")
            return conn
        except Error as e:
            print(e) 
        return conn

    def create_tables(self, conn, tables):
        c = conn.cursor()
        for table in tables:
            try:
                c.execute(table)
            except Error as e:
                print(e)

    def insert(self, insertions):
        c = self.conn.cursor()

        # Loop through all records (entries), inserting each into the database
        for values, query in insertions.items():
            try:
                c.execute(query, values)
                print("Insertion successful!")
            except Error as e:
                print(e)
                return False
        self.conn.commit()
        return True

    def insertAccount(self, insertions):
        c = self.conn.cursor()

        # Loop through all records (entries), inserting each into the database
        for values, query in insertions.items():
            try:
                c.execute(query, values)
                print("Account insertion successful!")
            except Error as e:
                print(e)
                return False
        self.conn.commit()
        return True

    def getAcctIds(self):
        c = self.conn.cursor()
        try:
            id_col = c.execute("""SELECT acct_id FROM accounts""").fetchall()
            ids = [idx[0] for idx in id_col]
            #print(ids)
            return ids
        except Error as e:
            print("Could not get database IDs: {}".format(e))
            return

    def getLoginInfo(self):
        c = self.conn.cursor()
        try:
            info = c.execute("""SELECT acct_id, acct_username, acct_password, acct_email FROM accounts""").fetchall()

            info_dict = {}
            for (idx, user, pw, email) in info:
                info_dict[user] = [idx, pw, email]
            print(info_dict)
            return info_dict
        except Error as e:
            print(e)

    def getCurrentMonth(self):
        current_month = datetime.now().month
        if current_month in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            current_month = "0{}".format(current_month)
        else:
            current_month = str(current_month)
        return current_month

