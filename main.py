import math
import os
from collections import Counter
# from copy import copy

import sqlite3
from flask import Flask
from flask import render_template
from flask import url_for
from flask import g
from flask import request, session
from flask import flash
from markupsafe import escape

from FDataBase import FDataBase
from words_table_funcs import WordsTableFunc

def connect_db():
  conn = sqlite3.connect(app.config['DATABASE'])
  conn.row_factory = sqlite3.Row
  return conn


def create_db():
  """Вспомогательная функция для созданшия таблиц БД"""
  db = connect_db()
  with app.open_resource('sq_db.sql', mode='r', encoding='utf-8') as f:
    db.cursor().executescript(f.read())
  db.commit()
  db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db




DATABASE = '/db_work/flask_dict.db'
DEBUG = True
SECRET_KEY = '4ec8b079d80d0a6f1f488e17bcff547ea007b968fc8a145e04b4c037c154047c'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'db_work', 'flsite.db')))

with app.app_context():
  db = get_db()
  dbase = FDataBase(db)
  # menu = dbase.getMenu()
  pages_names = dbase.get_pages_names()
  # for m in menu:
  #   print(f'{dict(m) = }')
  #   pages_names[m['url']] = m['page_title']


def del_dublicate_show_words(pages_name: dict):
  # FIXME Временно исправляет дублирование ключа '/show_words/num's
  vals_count = Counter(pages_name.values())

  # print(f'{vals_count=}')
  if vals_count['Изменить слово'] > 1:
    for key, val in pages_names.items():
      if val == 'Изменить слово':
        del pages_names[key]
        break



def change_current_words_page(new_page_number: int, current_page_number: int) -> None:
  print(f'{pages_names=}')
  if f'/show_words/{current_page_number}' in pages_names:
    del pages_names[f'/show_words/{current_page_number}'] # FIXME '/show_words/{current_page_number}'
  pages_names[f'/show_words/{new_page_number}'] = 'Показать слова' # FIXME '/show_words/{new_page_number}'

  del_dublicate_show_words(pages_names)

@app.errorhandler(404)
def pageNotFound(error):
  return render_template('page404.html', pages_names = pages_names, page_title='Страница не найдена.', current_page_url = '')


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
@app.route('/main')
def index():
  if 'current_page_number' not in session:
    session['current_page_number'] = 1
  return render_template('index.html', pages_names = pages_names, page_title=pages_names[url_for('index')], current_page_url=url_for('index'), current_page_number = session['current_page_number'])


@app.route('/user_profile')
def user_profile():
  if 'current_page_number' not in session:
    session['current_page_number'] = 1
  return render_template('user_profile.html', pages_names = pages_names, page_title=pages_names[url_for('user_profile')], current_page_url=url_for('user_profile'))


@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
  if 'current_page_number' not in session:
    session['current_page_number'] = 1
  if request.method == 'POST':
    print(f"{" Введенное слово ":=^30}")
    print(f"{"Английский перевод:":.<22} {escape(request.form['eng_word'])}")
    print(f"{"Русский перевод:":.<22} {escape(request.form['rus_word'])}")
    print(f"{"Описание слова:":.<22} {escape(request.form['word_description'])}")
    print(f"{"Примеры использования:":=<22} {escape(request.form['word_examples'])}")
    print(f"{'':=^30}")

    user_id = 0
    words_table = WordsTableFunc(user_id, get_db())
    word_data_to_add = {
      'eng_word': escape(request.form['eng_word']),
      'rus_word': escape(request.form['rus_word']),
      'word_description': escape(request.form['word_description']),
      'word_examples': escape(request.form['word_examples']),
    }
    is_word_added = words_table.add_word(word_data_to_add)

    if is_word_added is not False:
      flash('Слово добавлено.', category='success')
    else:
      flash('Ошибка добавления слова.', category='error')
  
  return render_template('add_word.html', pages_names = pages_names, page_title=pages_names[url_for('add_word')], current_page_url=url_for('add_word'))


@app.route('/edit_word', methods=['GET', 'POST'])
def edit_word():
  is_error = False

  if 'current_page_number' not in session:
    session['current_page_number'] = 1

  user_id = 0
  words_table = WordsTableFunc(user_id, get_db())

  is_choose_id_state = True # choose_id
  word_data = {}

  if request.method == 'POST':
    if 'get_word_info_btn' in request.form:
      word_number = escape(request.form.get('word_number'))
      # print(f'THIS {request.form=}')
      # print(f'{word_number=}')
      if not word_number.isdigit():
        flash('Введен некорректный номер слова.', category='error')        
        is_error = True

      if not is_error:
        word_number = int(word_number) - 1
        is_word_exists = words_table.is_word_exists(word_number)

      if not is_error and not is_word_exists:
        is_error = True
        flash(f'Ошибка слова с номером {word_number} не существует', category='error')      
      
      if not is_error:
        word_data = words_table.get_word_data(word_number)      
      
      is_choose_id_state  = True if is_error else False

    elif 'confirm_edit_btn' in request.form:
      word_number = escape(request.form.get('word_number'))
      if not word_number.isdigit():
        flash('Введен некорректный номер слова.', category='error')        
        is_error = True
      if not is_error:
        word_number = int(word_number) - 1   
        is_word_exists = words_table.is_word_exists(word_number)
      if not is_error and not is_word_exists:
        is_error = True
        flash(f'Ошибка слова с номером {word_number} не существует', category='error')    

      # Проверка наличия всех полей данных слова.
      if not is_error:
        keys = ['eng_word', 'rus_word', 'word_description', 'word_examples']
        
        for key in keys:
          if key not in request.form:
            is_error = True
            flash('Ошибка изменения слова', category='error')
            break

      if not is_error:
        word_new_data = {
          'eng_word': escape(request.form['eng_word']),
          'rus_word': escape(request.form['rus_word']),
          'word_description': escape(request.form['word_description']),
          'word_examples': escape(request.form['word_examples']),
        }
        words_table.update_word(word_number, word_new_data)
        flash('Слово изменено', category='success')


  word_data = dict(word_data)

  # print(f'THIS {word_data = }')
  # print(f'{is_choose_id_state}')

  for key, val in word_data.items():
    if val is None:
      word_data[key] = '-'

  return render_template(
      'edit_word.html',
      pages_names = pages_names,
      page_title=pages_names[url_for('edit_word')],
      current_page_url=url_for('edit_word'),
      is_choose_id_state = is_choose_id_state,
      word_data=word_data
    )


@app.route('/show_words/<int:num_of_page>', methods=['GET', 'POST'])
def show_words(num_of_page):

  def create_num_pages_list(cur: int, last: int) -> list[int | str]:
    if last <= 5:
      res = [i for i in range(1, last+1)]
    else: 
      if cur == 1:
        prev = 1
        cur = 2
        next = 3
      elif cur == last:
        perv = last - 2 
        cur = last - 1
        next = last

      if cur == 2:
        res = [1, 2, 3, '...', last]
      elif cur == 3:
        res = [1, 2, 3, 4, '...', last]
      elif cur == last - 2:
        res = [1, '...', last - 3, last - 2, last - 1, last]
      elif cur == last - 1:
        res = [1, '...', last - 2, last - 1, last]
      else: 
        res = [1, '...', cur - 1, cur, cur + 1, '...', last]
    return res
  
  def is_page_number_correct(num_of_page: int, last_page_number: int, request, flash) -> tuple[bool, int]:
    is_error = False
    try:
      form_num_of_page = int(request.form['num_of_page'])
    except:
      flash('Введен некорректный номер страницы.', category='error')
      form_num_of_page = last_page_number
      is_error = True
    return is_error, form_num_of_page
  
  def is_page_with_number_exists(num_of_page: int, max_page_num: int, last_page_number: int, flash, is_error: bool = False) -> tuple[int, int]:
    if num_of_page < 1 or num_of_page > max_page_num:
      flash(f'Страницы с номером { num_of_page } не существует', category='error')
      is_error = True
      num_of_page = last_page_number
    return is_error, num_of_page
  
  if 'current_page_number' not in session:
    session['current_page_number'] = 1

  is_error = False  

  user_id = 0 # FIXME: Далее брать user_id из сессии!
  words_table = WordsTableFunc(user_id, get_db())
  num_words = words_table.get_num_user_words()
  step = 10
  max_page_num = int(math.ceil(num_words / step))

  if request.method == 'POST' and 'num_of_page_btn' in request.form:
     is_error, num_of_page = is_page_number_correct(request.form['num_of_page'], session['current_page_number'], request, flash)

  if not is_error:    
    # print(session['current_page_number'])
    is_error, num_of_page = is_page_with_number_exists(num_of_page, max_page_num, session['current_page_number'], flash, is_error)

  if not is_error:
    change_current_words_page(num_of_page, session['current_page_number'])
    session['current_page_number'] = num_of_page

  user_words = words_table.get_user_words_with_numbers(step*(num_of_page-1), step*num_of_page)


  # return f'user {user_id} has {num_words} words'

  return render_template(
      'show_words.html',
      pages_names = pages_names,
      page_title=pages_names[url_for('show_words', num_of_page=session['current_page_number'])],
      current_page_url=url_for('show_words', num_of_page='1'),
      words = user_words,
      num_of_page = num_of_page,
      max_page_num = max_page_num,
      num_pages_list = create_num_pages_list(num_of_page, max_page_num),
    )


@app.route('/delete_word', methods=['GET', 'POST'])
def delete_word():
  is_error = False

  if 'current_page_number' not in session:
    session['current_page_number'] = 1

  user_id = 0
  words_table = WordsTableFunc(user_id, get_db())

  is_choose_id_state = True # choose_id
  word_data = {}

  if request.method == 'POST':
    if 'get_word_info_btn' in request.form:
      word_number = escape(request.form.get('word_number'))
      print('get_word_info_btn 0')
      print(f'{word_number=}')
      if not word_number.isdigit():
        print('get_word_info_btn 1')
        flash('Введен некорректный номер слова.', category='error')        
        is_error = True

      if not is_error:
        word_number = int(word_number) - 1
        is_word_exists = words_table.is_word_exists(word_number)

      if not is_error and not is_word_exists:
        is_error = True
        flash(f'Ошибка слова с номером {word_number} не существует', category='error')      
      
      if not is_error:
        word_data = words_table.get_word_data(word_number)      
      
      is_choose_id_state  = True if is_error else False

    elif 'confirm_del_btn' in request.form:
      word_number = escape(request.form.get('word_number'))
      if not word_number.isdigit():
        flash('Введен некорректный номер слова.', category='error')        
        is_error = True
      if not is_error:
        word_number = int(word_number) - 1   
        is_word_exists = words_table.is_word_exists(word_number)
      if not is_error and not is_word_exists:
        is_error = True
        flash(f'Ошибка слова с номером {word_number} не существует', category='error')    
      if not is_error:
        words_table.delete_word(word_number)
        flash('Слово удалено', category='success')


  word_data = dict(word_data)

  # print(f'THIS {word_data = }')
  # print(f'{is_choose_id_state}')

  for key, val in word_data.items():
    if val is None:
      word_data[key] = '-'

  return render_template(
      'delete_word.html',
      pages_names = pages_names,
      page_title=pages_names[url_for('delete_word')],
      current_page_url=url_for('delete_word'),
      is_choose_id_state = is_choose_id_state,
      word_data=word_data
    )


if __name__ == '__main__':
  app.run(debug=True)