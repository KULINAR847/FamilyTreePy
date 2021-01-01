

words = {'pid': 'ИД', 'rid': 'ИД связи', 'name': 'Имя', 'maiden': 'Девичья', 'surname': 'Фамилия', 'midname': 'Отчество',
	'birthday': 'Дата рождения', 'date_end': 'Дата смерти', 'pol': 'Пол', 'date_start': 'Дата начала', 'date_finish': 'Дата окончания', 
	'mid':'ИД отца','wid': 'ИД матери', 'type': 'Тип связи', 'event_desc': 'Описание', 'event_date': 'Дата события', 'place': 'Место', 'person_years':'Возраст участник(а/ов)'}
rewords = {v:k for k, v in words.items()}

def translate(word):
	if word in words.keys():
		return str(words[word])
	elif word in rewords.keys():
		return str(rewords[word])
	else:
		return str(word)