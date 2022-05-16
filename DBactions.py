import sqlite3

conn = sqlite3.connect('D:\\TelegramBotPython\\db\\database.db', check_same_thread=False)
cursor = conn.cursor()
def updateNumberOfAneks():
    cursor.execute('SELECT AnekiTable.anek_id AS text FROM AnekiTable')
    rows = cursor.fetchall()
    numberOfAneksInDB = len(rows)
    return numberOfAneksInDB

def updateNumberOfMemes():
    cursor.execute('SELECT MemeTable.meme_id AS meme_id FROM MemeTable')
    rows = cursor.fetchall()
    numberOfMemesInDB = len(rows)
    return numberOfMemesInDB

def db_table_val(user_id: int, user_name: str, user_surname: str, nickname: str):
    cursor.execute('INSERT or IGNORE INTO userid (user_id, user_name, user_surname, nickname) VALUES (?, ?, ?, ?)', (user_id, user_name, user_surname, nickname))
    conn.commit()

def db_addAneki(text: str):
    cursor.execute('INSERT INTO AnekiTable(text) VALUES (?)',(text,))
    conn.commit()

def db_addWatchedAnek(user_id: int, anek_id: int):
    cursor.execute('INSERT INTO watchedContentAnek(user_id, anek_id) VALUES (?, ?)',(user_id, anek_id))
    conn.commit()

def db_addMeme(url: str, jpg, file_name: str):
    cursor.execute('INSERT INTO MemeTable(url, jpg, file_name) VALUES (?,?,?)',(url, jpg, file_name))
    conn.commit()

def db_addWatchedMeme(user_id: int, meme_id: int):
    cursor.execute('INSERT INTO watchedContentMeme(user_id, meme_id) VALUES (?, ?)',(user_id, meme_id))
    conn.commit()

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData
