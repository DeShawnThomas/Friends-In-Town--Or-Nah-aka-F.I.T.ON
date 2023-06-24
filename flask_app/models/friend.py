from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user import User

class Friend:
    db = "fiton_schema"

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']

    @classmethod
    def save(cls, data):
        query = "INSERT INTO friends (name) VALUES (%(name)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_by_id(cls, friend_id):
        query = "SELECT * FROM friends WHERE id = %(friend_id)s;"
        data = {'friend_id': friend_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if not result:
            return None
        return cls(result[0])

    @classmethod
    def get_group_id_by_name(cls, name):
        query = "SELECT id FROM friends WHERE name = %(name)s;"
        data = {'name': name}
        result = connectToMySQL(cls.db).query_db(query, data)
        if not result:
            return None
        return result[0]['id']

    @classmethod
    def get_users_by_friends_id(cls, friends_id):
        query = "SELECT * FROM users WHERE friends_id = %(friends_id)s;"
        data = {'friends_id': friends_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        users = []
        for row in result:
            user_data = {
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'phone_number': row['phone_number'],
                'birthday': row['birthday'],
                'password': row['password'],
                'about_me': row['about_me'],
                'facebook': row['facebook'],
                'twitter': row['twitter'],
                'instagram': row['instagram'],
                'snapchat': row['snapchat'],
                'linkedin': row['linkedin'],
                'tiktok': row['tiktok'],
                'user_location': row['user_location'],
                'profile_picture': row['profile_picture'],
                'monday': row['monday'],
                'tuesday': row['tuesday'],
                'wednesday': row['wednesday'],
                'thursday': row['thursday'],
                'friday': row['friday'],
                'saturday': row['saturday'],
                'sunday': row['sunday'],
                'friends_id': row['friends_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            users.append(User(user_data))
        return users
