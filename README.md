# Описание файлов в репе

`db.sqlite` - исходный файл с данными, которые необходимо смигрировать в 
Postgres.

`sqlite.dll` - описание схемы данных в `db.sqlite`.

`movies_database.dll` - описание базы данных Postgres.

`main.py` - рабочий черновик на данный момент реализует метод 
`extract_data`, который чанками/батчами загружает данные из `db.sqlite` и 
создает объекты датаклассов, описывающих таблицы БД.


## Проектное задание: перенос данных
Вооружитесь библиотеками `psycopg2` и `sqlite3`, чтобы создать скрипт для миграции данных в новую базу.

Критерии готовности:

- После применения скрипта все фильмы, персоны и жанры появляются в PostgreSQL.  
- Все связи между записями сохранены. 
- В коде используются `dataclass`.
- Повторный запуск скрипта не создаёт дублирующиеся записи.
- В коде есть обработка ошибок записи и чтения.
- Для установки и закрытия соединений используются менеджеры контекста.
- Соединения устанавливаются один раз в начале работы программы.

Дополнительное условие: 

    Загружайте данные пачками по n записей.

Решение задачи залейте в папку sqlite_to_postgres вашего репозитория.

## Тестирование решения
Убедитесь, что код загрузки данных из SQLite в PostgreSQL работает правильно. Для этого вам необходимо написать простой тест, который сравнивает содержимое таблиц двух БД. 
Что должно быть в тесте:
- Проверка целостности данных между каждой парой таблиц в SQLite и Postgres. 
Достаточно проверять количество записей в каждой таблице.
- Проверка содержимого записей внутри каждой таблицы. Проверьте, что все 
  записи из PostgreSQL присутствуют с такими же значениями полей, как и в SQLite.
- Проверка таблиц `genre`, `film_work`, `person`, `genre_film_work`, 
  `person_film_work`.

Используйте `assert` при сравнении ожидаемых и существующих данных.
Залейте решение в папку tests/check_consistency вашего проекта.