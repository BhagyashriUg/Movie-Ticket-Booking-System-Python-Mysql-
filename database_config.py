import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        passwd="Bsu@0896",
        database="rec",
        cursorclass=pymysql.cursors.DictCursor
    )
