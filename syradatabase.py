import pymysql
import syracommon
from time import sleep


class Mysql:

    def __init__(self):
        self.write_buffer = set()
        self.read_buffer = set()
        self.cursor_locked = False
        self.buffer_locked = False
        conf = syracommon.extract_config('mysql.json')
        self.debug = bool(conf['debug'])
        self.con = pymysql.connect(conf['host'], conf['user'], conf['password'], conf['database'])
        self.cursor = self.con.cursor()

    def rewrite_state(self, uid, state):
        query = 'UPDATE Res_state SET state = \'{}\' WHERE uid = \'{}\''.format(state, uid)
        self.write_cursor(query)

    def rewrite_status(self, uid, status):
        query = 'UPDATE Dev_status SET status = \'{}\' WHERE uid = \'{}\''.format(status, uid)
        self.write_cursor(query)

    def check_state_row_exist(self, uid):
        query = 'SELECT uid FROM Res_state WHERE uid = \'{}\''.format(uid)
        if not self.send_read_query(query):
            self.create_state_row(uid)

    def check_status_row_exist(self, uid):
        query = 'SELECT uid FROM Dev_status WHERE uid = \'{}\''.format(uid)
        if not self.send_read_query(query):
            self.create_status_row(uid)

    def create_state_row(self, uid):
        query = 'INSERT INTO Res_state (uid, state) VALUES (\'{}\', \'{}\')'.format(uid, 'None')
        self.send_write_query(query)

    def create_status_row(self, uid):
        query = 'INSERT INTO Dev_status (uid, status) VALUES (\'{}\', \'{}\')'.format(uid, 'None')
        self.send_write_query(query)
    
    def send_write_query(self, query):
        if not self.cursor_locked:
            self.write_cursor(query)
        else:
            while self.buffer_locked:
                sleep(0.1)
            self.write_buffer.update({query})
            
    def send_read_query(self, query):
        while self.cursor_locked:
            sleep(0.1)
        return self.read_cursor(query)

    def write_cursor(self, query):
        if self.debug:
            print(query)
        self.cursor_locked = True
        if self.write_buffer:
            self.buffer_locked = True
            for query in self.write_buffer:
                self.cursor.execute(query)
            self.con.commit()
            self.write_buffer.clear()
            self.buffer_locked = False
        self.cursor.execute(query)
        result = self.con.commit()
        self.cursor_locked = False
        return result

    def read_cursor(self, query):
        if self.debug:
            print(query)
        self.cursor_locked = True
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.cursor_locked = False
        return result



