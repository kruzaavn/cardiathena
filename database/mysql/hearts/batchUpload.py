import os
import glob
import shutil
import mysql

from HeartsMySQLVariables import CSV_DIR
from HeartsMySQLVariables import ARCHIVE_DIR
from HeartsMySQLVariables import STATE_TABLE
from HeartsMySQLVariables import GAME_TABLE
from HeartsMySQLVariables import CONFIG
from mysql.connector import errorcode

game_table_files = glob.glob(os.path.join(CSV_DIR, "*_gametable.csv"))
state_table_files = glob.glob(os.path.join(CSV_DIR, "*_statetable.csv"))


class MySQLDatabase:
    """
    Database connection object
    """
    def __init__(self):
        self.cnx = get_connection()

    def get_cursor(self):
        return self.cnx.cursor()


def get_connection():
    """
    Returns a MySQL connection object

    :returns cnx: MySQL connection object
    """
    try:
        cnx = mysql.connector.connect(**CONFIG)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def insert_game_table():
    dbs = MySQLDatabase()
    my_cursor = dbs.get_cursor()
    try:
        for file in game_table_files:
            query = "LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY ',' " \
                "LINES TERMINATED BY '\n'" \
                "(time, agent1, agent2, agent3, agent4, game_uuid)".format(file, GAME_TABLE)
            my_cursor.execute(query)
            shutil.move(file, ARCHIVE_DIR)
    except mysql.connector.Error as err:
        print(err)
    finally:
        dbs.cnx.commit()
        my_cursor.close()
        dbs.cnx.close()


def insert_state_table():
    dbs = MySQLDatabase()
    my_cursor = dbs.get_cursor()
    try:
        for file in state_table_files:
            query = "LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY ',' " \
                "ENCLOSED BY '\"' " \
                "LINES TERMINATED BY '\n'" \
                "(deck, action, score, game_uuid)".format(file, STATE_TABLE)
            my_cursor.execute(query)
            shutil.move(file, ARCHIVE_DIR)
    except mysql.connector.Error as err:
        print(err)
    finally:
        dbs.cnx.commit()
        my_cursor.close()
        dbs.cnx.close()


insert_game_table()
insert_state_table()
