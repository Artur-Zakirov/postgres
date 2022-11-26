from db_classes import postgresdb


if __name__ == '__main__':
    print('Добро пожаловать!')
    database = input('Введите название БД\n')
    user = input('Введите имя пользователя\n')
    password = input('Введите пароль\n')
    my_db = postgresdb(database, user, password)
    while True:
        command = input('Список доступных команд (латиницей):\n'
                        'c - создать таблицу (или удалить и создать новую таблицу, в случае,'
                        'если таблица уже существует);\n'
                        'a - добавить данные клиента;\n'
                        's - показать данные клиента;\n'
                        'p - добавить номер телефона к клиенту;\n'
                        'e - редактировать данные клиента;\n'
                        'd - удалить данные клиента;\n'
                        'dp - удалить номер телефона клиента;\n'
                        'x - выйти из программы.\n')
        if command == 'c':
            my_db.create_tables()
        elif command == 'a':
            my_db.add_client()
        elif command == 's':
            param_dict = {'0': 'all', '1': 'name', '2': 'surname', '3': 'email', '4': 'phone_number'}
            my_db.show_client(param_dict)
        elif command == 'p':
            my_db.add_client_phone()
        elif command == 'e':
            my_db.edit_client()
        elif command == 'd':
            my_db.delete_client()
        elif command == 'dp':
            my_db.delete_client_phone()
        elif command == 'x':
            break
        else:
            print('Неизвестная команда.')
