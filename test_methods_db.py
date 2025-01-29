import sqlite3
from words_table_funcs import WordsTableFunc

user_id = 0

con = sqlite3.connect('db_work/flsite.db')
con.row_factory = sqlite3.Row
words_table = WordsTableFunc(user_id, con)

# print(words_table.is_word_exists(2)) 
# print(dict(words_table.get_word_data(2)[0]))
# words_table.delete_word(2)
word_data = {
  'rus_word': 'fridge',
  'eng_word': 'холодильник',
  'word_examples': '',
  'word_description': '',
}
words_table.update_word(0, word_data)

con.close()

