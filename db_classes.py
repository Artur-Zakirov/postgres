import psycopg2


class postgresdb:

    def __init__(self, database_name, user_name, user_password):
        self.database = database_name
        self.user = user_name
        self.password = user_password

    def get_connection(self):
        conn = psycopg2.connect(database=self.database, user=self.user, password=self.password)
        return conn

    def create_tables(self):
        conn = self.get_connection()
        with conn.cursor() as cur:
            cur.execute('''
                DROP TABLE IF EXISTS client_phone;
                DROP TABLE IF EXISTS phone_numbers;
                DROP TABLE IF EXISTS clients;
            ''')
            conn.commit()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                surname VARCHAR(40) NOT NULL,
                email VARCHAR(40) NOT NULL UNIQUE
                );
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS phone_numbers (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                phone_number VARCHAR(40)
                );
            ''')
            conn.commit()
            print('Таблицы созданы')
        conn.close()

    def add_client(self):
        conn = self.get_connection()
        while True:
            try:
                name = input('Введите имя клиента:\n')
                while not name:
                    name = input('Вы ничего не ввели.\nВведите имя клиента:\n')
                surname = input('Введите фамилию клиента:\n')
                while not surname:
                    surname = input('Вы ничего не ввели.\nВведите фамилию клиента:\n')
                email = input('Введите электронную почту клиента:\n')
                while not email:
                    email = input('Вы ничего не ввели.\nВведите электронную почту клиента:\n')
                client_phone = input(
                    'Введите номер телефона клиента начиная с 8\n(если номера телефона нет, нажмите enter):\n')
                with conn.cursor() as cur:
                    cur.execute('''
                        INSERT INTO clients(name, surname, email) VALUES (%s, %s, %s) RETURNING id, name, surname;
                    ''', (name, surname, email))
                    conn.commit()
                    client_id, client_name, client_surname = cur.fetchone()

                if client_phone:
                    while not client_phone.isdigit():
                        client_phone = input('Неправильно набран номер.\nВведите номер телефона клиента начиная с 8\n')
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO phone_numbers (client_id, phone_number) VALUES (%s, %s) 
                            RETURNING id, phone_number;
                        ''', (client_id, client_phone))
                        conn.commit()
                print(client_name, client_surname, 'Добавлен')
                break
            except psycopg2.errors.UniqueViolation as err:
                print(err)
        conn.close()

    def add_client_phone(self):
        conn = self.get_connection()
        email = input('Введите электронную почту клиента, для которого хотите добавить номер телефона:\n')
        while not email:
            email = input('Вы ничего не ввели.\nВведите электронную почту клиента:\n')
        with conn.cursor() as cur:
            cur.execute('''
                SELECT id, name, surname FROM clients WHERE email=%s;
            ''', (email,))
            client_id, client_name, client_surname = cur.fetchone()
        print('Клиент:', client_name)
        client_phone = input('Введите номер телефона клиента начиная с 8\n'
                             'или нажмите enter, если передумали:\n')
        if client_phone:
            while not client_phone.isdigit():
                client_phone = input('Неправильно набран номер.\nВведите номер телефона клиента начиная с 8\n')
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO phone_numbers (client_id, phone_number) VALUES (%s, %s) RETURNING id, phone_number;
                ''', (client_id, client_phone))
                conn.commit()
                phone_id, phone = cur.fetchone()
        print('Номер телефона', phone, 'Добавлен клиенту', client_name)
        conn.close()

    def edit_client(self):
        conn = self.get_connection()
        param_dict = {'1': 'name', '2': 'surname', '3': 'email'}
        clients = self.show_client(param_dict)
        while not clients:
            clients = self.show_client(param_dict)
        client_id = input('Введите id клиента для которого хотите изменить данные:\n')
        param_dict = {'1': 'name', '2': 'surname', '3': 'email', '4': 'phone_number'}
        param = input('Введите номер параметра, который хотите изменить:'
                      '1 - name\n;2 - surname;\n3 - email;\n4 - phone number.\n')
        param = param_dict.get(param, 'Такого параметра нет')
        while param == 'Такого параметра нет':
            param = input('Введите номер параметра, который хотите изменить:\n'
                          '1 - name\n;2 - surname;\n3 - email;\n4 - phone number.\n')
            param = param_dict.get(param, 'Такого параметра нет')
        new_sub = input('Введите новое значение параметра:\n')
        while not new_sub:
            new_sub = input('Вы ничего не ввели.\nВведите новое значение параметра:\n')
        if param == 'phone_number':
            old_phone_number = input('Введите старый номер телефона, который хотите заменить:\n')
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE phone_numbers SET phone_number=%s WHERE client_id=%s AND phone_number=%s;
                ''', (new_sub, client_id, old_phone_number))
                conn.commit()
                print('Номер телефона изменён.')
        elif param == 'name':
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE clients SET name=%s WHERE id=%s;
                ''', (new_sub, client_id))
                conn.commit()
                print('Имя изменено.')
        elif param == 'surname':
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE clients SET surname=%s WHERE id=%s;
                ''', (new_sub, client_id))
                conn.commit()
                print('Фамилия изменена.')
        elif param == 'email':
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE clients SET email=%s WHERE id=%s;
                ''', (new_sub, client_id))
                conn.commit()
                print('Почта изменена.')
        conn.close()

    def delete_client_phone(self):
        conn = self.get_connection()
        param_dict = {'1': 'name', '2': 'surname', '3': 'email'}
        clients = self.show_client(param_dict)
        while not clients:
            clients = self.show_client(param_dict)
        client_id = input('Введите id клиента, для которого хотите удалить номер телефона:\n')
        phone_number = input('Введите номер телефона, который хотите удалить\n'
                             'или введите all, чтобы удалить все номера:\n')
        if phone_number == 'all':
            with conn.cursor() as cur:
                cur.execute('''
                            DELETE FROM phone_numbers WHERE client_id=%s;
                        ''', (client_id,))
                conn.commit()
                print('Номера телефонов удалены.')
        else:
            with conn.cursor() as cur:
                cur.execute('''
                            DELETE FROM phone_numbers WHERE client_id=%s AND phone_number=%s;
                        ''', (client_id, phone_number))
                conn.commit()
                print('Номер телефона удалён.')
        conn.close()

    def delete_client(self):
        conn = self.get_connection()
        param_dict = {'1': 'name', '2': 'surname', '3': 'email'}
        clients = self.show_client(param_dict)
        while not clients:
            clients = self.show_client(param_dict)
        client_id = input('Введите id клиента, которого хотите удалить:\n')
        with conn.cursor() as cur:
            cur.execute('''
                            DELETE FROM phone_numbers WHERE client_id=%s;
                        ''', (client_id,))
            cur.execute('''
                                    DELETE FROM clients WHERE id=%s;
                                ''', (client_id,))
            conn.commit()
            print('Клиент удалён.')
        conn.close()

    def show_client(self, parametres: dict):
        conn = self.get_connection()
        param = input('Введите параметр, по которому хотите найти клиента:\n'
                      '1 - name;\n2 - surname;\n3 - email;\n4 - phone number.\n'
                      '0 - показать всех клиентов\n')
        param = parametres.get(param, 'Такого параметра нет')
        while param == 'Такого параметра нет':
            param = input('Введите параметр, по которому хотите найти клиента:\n'
                          '1 - name;\n2 - surname;\n3 - email;\n4 - phone number.\n'
                          '0 - показать всех клиентов\n')
            param = parametres.get(param, 'Такого параметра нет')
        if param == 'all':
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT clients.id, name, surname, email, phone_number FROM clients
                            FULL JOIN phone_numbers ON clients.id = phone_numbers.client_id;
                        ''')
                clients = cur.fetchall()
                if not clients:
                    print('Клиент не найден.')
                else:
                    for client in clients:
                        client_id, name, surname, email, phone = client
                        print(f'id клиента: {client_id}\n'
                              f'Имя: {name}\n'
                              f'Фамилия: {surname}\n'
                              f'Почта: {email}\n'
                              f'Номер телефона: {phone}\n')
        else:
            client_info = input('Введите данные клиента, которого хотите найти:\n')
            if param == 'name':
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT clients.id, name, surname, email, phone_number FROM clients
                                FULL JOIN phone_numbers ON clients.id = phone_numbers.client_id
                                WHERE name=%s;
                            ''', (client_info,))
                    clients = cur.fetchall()
                    if not clients:
                        print('Клиент не найден.')
                    else:
                        for client in clients:
                            client_id, name, surname, email, phone = client
                            print(f'id клиента: {client_id}\n'
                                  f'Имя: {name}\n'
                                  f'Фамилия: {surname}\n'
                                  f'Почта: {email}\n'
                                  f'Номер телефона: {phone}\n')
            elif param == 'surname':
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT clients.id, name, surname, email, phone_number FROM clients
                                FULL JOIN phone_numbers ON clients.id = phone_numbers.client_id
                                WHERE surname=%s;
                            ''', (client_info,))
                    clients = cur.fetchall()
                    if not clients:
                        print('Клиент не найден.')
                    else:
                        for client in clients:
                            client_id, name, surname, email, phone = client
                            print(f'id клиента: {client_id}\n'
                                  f'Имя: {name}\n'
                                  f'Фамилия: {surname}\n'
                                  f'Почта: {email}\n'
                                  f'Номер телефона: {phone}\n')
            elif param == 'email':
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT clients.id, name, surname, email, phone_number FROM clients
                                FULL JOIN phone_numbers ON clients.id = phone_numbers.client_id
                                WHERE email=%s;
                            ''', (client_info,))
                    clients = cur.fetchall()
                    if not clients:
                        print('Клиент не найден.')
                    else:
                        for client in clients:
                            client_id, name, surname, email, phone = client
                            print(f'id клиента: {client_id}\n'
                                  f'Имя: {name}\n'
                                  f'Фамилия: {surname}\n'
                                  f'Почта: {email}\n'
                                  f'Номер телефона: {phone}\n')
            elif param == 'phone_number':
                with conn.cursor() as cur:
                    cur.execute('''
                                SELECT clients.id, name, surname, email, phone_number FROM phone_numbers
                                FULL JOIN clients ON clients.id = phone_numbers.client_id
                                WHERE phone_number=%s;
                            ''', (client_info,))
                    clients = cur.fetchall()
                    if not clients:
                        print('Клиент не найден.')
                    else:
                        for client in clients:
                            client_id, name, surname, email, phone = client
                            print(f'id клиента: {client_id}\n'
                                  f'Имя: {name}\n'
                                  f'Фамилия: {surname}\n'
                                  f'Почта: {email}\n'
                                  f'Номер телефона: {phone}\n')
        conn.close()
        return clients
