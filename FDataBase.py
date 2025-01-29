import sqlite3
 
class FDataBase:
	def __init__(self, db):
		self.__db = db
		self.__cur = db.cursor()

	def getMenu(self):
		sql = '''SELECT * FROM mainmenu'''
		try:
				self.__cur.execute(sql)
				res = self.__cur.fetchall()
				if res: 
						return res
		except:
				print("Ошибка чтения из БД")
		return []

	def get_pages_names(self):
		sql = '''SELECT * FROM mainmenu'''
		try:
			self.__cur.execute(sql)
			pages_names_rows = self.__cur.fetchall()
			res = {}
			if pages_names_rows:
				for pages_names_row in pages_names_rows:
					# print(f'{dict(m) = }')
					res[pages_names_row['url']] = pages_names_row['page_title']
				return res
		except:
			print('Ошибка чтения из б.д.')
		return []
		
