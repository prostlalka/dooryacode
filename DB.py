import logging

import mysql.connector
import configparser


class DB():

    def __init__(self, **kwargs):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        self.conn = mysql.connector.connect(user=config["mysql"]["username"], password=config["mysql"]["password"],
                                            host='127.0.0.1',
                                            database=config["mysql"]["database"])
        try:
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(str(e))

    def execute(self, query, data=None, ret1=False):
        try:
            if not self.conn:
                self.__init__()
            else:
                if data:
                    self.cursor.execute(query, data)
                else:
                    self.cursor.execute(query)

                if 'INSERT' in query or 'UPDATE' in query or 'DELETE' in query or 'DROP' in query:
                    self.conn.commit()

                if ret1:
                    return self.cursor.fetchone()
                else:
                    return self.cursor.fetchall()

        except:
            logging.error('end', exc_info=True)
            return 'error'
