import sqlite3 as sq
# Базовые операции для работы с таблицей слов.

class UserWords:
  def __init__(self, user_id: int, con):
    if not isinstance(user_id, int):
      raise TypeError("Type error, user_id should be int.")
    if user_id < 0:
      raise ValueError("Value error, user_id should be bigger or equal to zero.")
    
    self.__user_id = user_id
    # con.row_factory = sq.Row
    self.__con = con
    self.__num_words = -1
    self.__max_word_number = -1

  @property
  def num_words(self) -> int:
    if self.__num_words == -1:
      # Получить количество слов пользователя из б.д.
      try:
        cur = self.__con.cursor()
        cur.execute('\
          SELECT count(id) FROM user_words WHERE user_id = :user_id',
          {'user_id': self.__user_id}
        )        
        self.__num_words = int(cur.fetchone()[0])    
      except sq.Error as e:        
        print(f"Ошибка при получении количества слов пользователя: {e}")
    return self.__num_words
  
  @num_words.setter
  def num_words(self, val: int) -> None: # FIXME - возможно эта функция не нужна.
    if val < 0:
      raise ValueError("Num of words in user table shoult be more or equal to zero.")
    if not isinstance(val, int):
      raise TypeError("val in num_words should be int.")    
    self.__num_words = val

  @property
  def max_word_number(self) -> int:
    if self.__max_word_number == -1:
      try:
        cur = self.__con.cursor()
        cur.execute(
          'SELECT max(word_number) FROM user_words WHERE user_id = :user_id',
          {'user_id': self.__user_id}
        )
        self.__max_word_number = int(cur.fetchone()[0])
      except sq.Error as e:
        print(f"Ошибка вычисления максимального номера слова у пользователя: {e}")
    return self.__max_word_number  

  def is_user_id_exists(self) -> bool: # -> get_words.
    return self.num_words > 0
  
  def is_word_number_exists(self, word_number: int) -> bool:
    if not isinstance(word_number, int):
      raise TyperError("word_nubmer should be int")
    if word_number <= 0 or word_number > self.max_word_number:
      return False
    
    try:
      cur = self.__con.cursor()
      cur.execute(
        'SELECT word_number FROM user_words WHERE\
          user_id == :user_id and word_number == :word_number',
        {'user_id': self.__user_id,
         'word_number': word_number}
        )
      res = cur.fetchone()
      if res is None:
        print(f'Слово с номером {word_number} не существует.')
        return False
      else:
        return True
    except sq.Error as e:
      print(f'Ошибка получения номера слова из базы данных: {e}')      
    return False
  
  def add_word(self, eng_word: str, rus_word: str, word_description: str, word_examples: str) -> bool:
    
    # Проверка существования user_id.
    if not self.is_user_id_exists():
      return False
    
    try:
      self.__num_words += 1 # ?????
      cur = self.__con.cursor()
      cur.execute('\
        INSERT INTO user_words (\
          user_id, \
          word_number,\
          eng_word,\
          rus_word,\
          word_description,\
          word_examples,\
          add_date\
        ) VALUES (\
          :user_id,\
          :word_number,\
          :eng_word,\
          :rus_word,\
          :word_description,\
          :word_examples,\
          date()\
        )',{
          'user_id': self.__user_id,
          'word_number': self.__num_words,
          'eng_word': eng_word,
          'rus_word': rus_word,
          'word_description': word_description,
          'word_examples': word_examples,
        }
      )
      self.__con.commit()      
      self.__max_word_number = -1
    except sq.Error as e:
      self.__num_words -= 1
      print(f'Ошибка добавления слова в базу данных: {e}')
      return False
    return True

  def get_words(self, start_number: int = 0, end_number: int = -1) -> dict:
    # Проверка существования пользователя с данным user_id.
    if not self.is_user_id_exists():
      return {}
    
    # Проверка корретности введенного диапазона  [start_nubmer; end_numbser)
    if start_number < 0 or end_number != -1 and end_number <= start_number:
      raise ValueError("Incorrect start_number and/or end_number")
  
    # Определение диапазона передаваемых слов.
    if end_number == -1:
      end_number = self.num_words

    # Извлечение слов из базы данных.
    try:
      cur = self.__con.cursor()
      cur.execute('SELECT id, word_number, eng_word, rus_word FROM user_words  \
                  WHERE user_id == :user_id and word_number >= :start_number and word_number < :end_number',
                  {'user_id': self.__user_id, 'start_number': start_number, 'end_number': end_number} )
      # print(f'{self.__user_id = }\n{start_number = }\n{end_number = }')
      res = cur.fetchall()
    except sq.Error as e:
      print(f"Ошибка извлечения слов из базы данных {e}")
      res = None

    # Преобразование слов в словарь.
    if res is  None:
      return {}
    else:
      return [{'word_id': word_id,
        'word_number': word_number,
        'word_eng': word_eng,
        'word_rus': word_rus,}
        for word_id, word_number, word_eng, word_rus in res]
    
  def edit_word(self, *, word_number: int, word_eng: str, word_rus: str, word_description: str, word_examples: str) -> bool:
    if not self.is_user_id_exists():
      print('user id doesn\'t exist')
      return False
    if not self.is_word_number_exists(word_number):
      print(f'word number {word_number} doesn\'t exist')
      return False    
    
    try:
      cur = self.__con.cursor()
      cur.execute('\
        UPDATE user_words SET\
          word_number = :word_number,\
          eng_word = :word_eng,\
          rus_word = :word_rus,\
          word_description = :word_description,\
          word_examples = :word_examples\
          WHERE user_id == :user_id and word_number == :word_number'
      ,
        {
          'word_number': word_number,
          'word_eng': word_eng,
          'word_rus': word_rus,
          'word_description': word_description,
          'word_examples': word_examples,
          'user_id': self.__user_id
        }
      )
      self.__con.commit()
      res = True
    except sq.Error as e:
      print(f'Ошибка изменения данных слова: {e}')
      res = False

    return res

    

    

  def del_word(self, word_number):
    # Проверка, содержится ли номер в допустимом диапазоне.
    if word_number <= 0 or word_number > self.max_word_number: 
      raise ValueError(f'Слова с номером {word_number} не существует')    
    
    # Проверка, существует ли слово с указанным номером.
    # ~ возможно можно проверить через результат удаления.
    try:
      cur = self.__con.cursor()
      cur.execute('\
        DELETE FROM user_words WHERE user_id = :user_id and word_number = :word_number\
      ',{
        'user_id': self.__user_id,
        'word_number': word_number
      })
      self.__con.commit()
      self.__max_word_number = -1
      res = cur.fetchall()
      print(f'Результат удаления слова из базы данных: {res}')
    except sq.Error as e:
      print(f'Ошибка удаления слова из б.д.: {e}')

if __name__ == '__main__':
  user_words = UserWords(0, sq.connect('words.db'))
  print(f'{user_words.num_words = }')
  # print(f'{user_words.get_words() = }')
  # print(user_words.add_word('stab', 'удар, попытка', '-', '-'))
  # try:
  #   print(user_words.del_word(100))
  # except ValueError as e:
  #   print(str(e))
  # print(f'{user_words.max_word_number = }')
  # print(f'{user_words.is_word_number_exists(105) = }')
  print(f'{user_words.edit_word(
    word_number = 103,
    word_eng = 'stab',
    word_rus = 'удар, попытка',
    word_description = '-',
    word_examples = '-'
  )}')
  print('Продолжение программы.')