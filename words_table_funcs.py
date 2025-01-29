import sqlite3

# Класс для ~представления show_words

class WordsTableFunc: # Работа со словами конкретного пользователя.
  def __init__(self, user_id: int, con):
    self.user_id = user_id
    self.con = con

  def query_db(self, query, args=(), one=False):
    try:
      cur = self.con.cursor()
      cur.execute(query, args)
      rv = cur.fetchall()
      cur.close()
      return (rv[0] if rv else None) if one else rv
    except:
      print('Ошибка чтения из б.д.')
    return False
  
  def query_db_commit(self, query, args=()):
    # try:
    cur = self.con.cursor()
    cur.execute(query, args)
    self.con.commit()
    return True
    # except:
    #   print('Ошибка записи в б.д.')
    # return False

  def get_num_user_words(self) -> int:
    query = 'SELECT count("word_number") as words_count FROM user_words WHERE user_id == ?'
    args=(self.user_id, )
    res = self.query_db(query, args)
    if res is False:
      return False
    else:    
      return int(res[0]['words_count'])
  
  def get_max_word_number(self) -> int:
    query = 'SELECT max("word_number") as max_id FROM user_words WHERE user_id == ?'
    args=(self.user_id, )
    res = self.query_db(query, args)
    if res is False:
      return False
    else:
      return int(res[0]['max_id'])
  
  def get_new_word_number(self) -> int:
    return self.get_max_word_number() + 1
  
  def get_user_words_with_numbers(self, fr:int , to:int ): # От fr включительно, до to 1.
    query = 'SELECT * FROM user_words WHERE user_id == ? and word_number >= ? and word_number < ?;'
    args = (self.user_id, fr, to)
    res = self.query_db(query, args)
    if res is False:
      return False
    else:
      return res

  def get_word_data(self, word_number: int) -> dict:
    script = 'SELECT * FROM user_words WHERE user_id = ? and word_number = ?'
    args = (self.user_id, word_number)
    word_data = self.query_db(script, args, True)
    return word_data

  def is_word_exists(self, word_number: int) -> bool:
    script = 'SELECT count("word_id") as word_number FROM user_words WHERE user_id == ? and word_number == ?'
    args = (self.user_id, word_number)
    res = self.query_db(script, args)
    
    # if res is False # Действия при ошибке работы с б.д.
    if res[0][0] == 0:
      return False
    else:
      return True
  
  def add_word(self, word_data_to_add: dict) -> bool:
    query = """INSERT INTO user_words (user_id, word_number, eng_word, rus_word, word_examples, word_examples, add_date) VALUES
      (?, ?, ?, ?, ?, ?, date());
    """
    args = (
      self.user_id,
      self.get_new_word_number(),
      word_data_to_add['eng_word'],
      word_data_to_add['rus_word'],
      word_data_to_add['word_description'],
      word_data_to_add['word_examples']
      )
    res = self.query_db_commit(query, args)
    return res

  def update_word(self, word_number, word_new_data: dict):
    script = """UPDATE user_words SET
        rus_word = ?,
        eng_word = ?,
        word_examples = ?,
        word_description = ?
        WHERE user_id = ? and word_number = ?
      """      
    args = (
      word_new_data['rus_word'],
      word_new_data['eng_word'],
      word_new_data['word_examples'],
      word_new_data['word_description'],
      self.user_id,
      word_number,      
      )
    self.query_db_commit(script, args)

  def delete_word(self, word_number: int) -> None:
    query = 'DELETE FROM user_words WHERE user_id = ? and word_number = ?' # Добавить word_id для большей точности удаления.
    args = (self.user_id, word_number)
    self.query_db_commit(query, args)


if __name__ == '__main__':
  con = sqlite3.connect('db_work/flsite.db')
  con.row_factory = sqlite3.Row
  sw = WordsTableFunc(0, con)
  # sw.get_num_words()
  sw.get_user_words_with_numbers(0, 9)

