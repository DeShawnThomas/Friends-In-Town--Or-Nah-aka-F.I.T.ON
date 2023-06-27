from flask_app.config.mysqlconnection import connectToMySQL
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash
from flask_bcrypt import check_password_hash
import json

class User:
    db = "fiton_schema"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.phone_number = data['phone_number']
        self.birthday = data['birthday']
        self.password = data['password']
        self.profile_picture = data['profile_picture']
        self.about_me = data['about_me']
        self.facebook = data['facebook']
        self.twitter = data['twitter']
        self.instagram = data['instagram']
        self.snapchat = data['snapchat']
        self.linkedin = data['linkedin']
        self.tiktok = data['tiktok']
        self.monday = data['monday']
        self.tuesday = data['tuesday']
        self.wednesday = data['wednesday']
        self.thursday = data['thursday']
        self.friday = data['friday']
        self.saturday = data['saturday']
        self.sunday = data['sunday']
        self.friends_id = data['friends_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.status = data['status']
        self.latitude = data['latitude']
        self.longitude = data['longitude']


    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, phone_number, birthday, password, profile_picture, about_me, facebook, twitter, instagram, snapchat, linkedin, tiktok, friends_id) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(phone_number)s, %(birthday)s, %(password)s, %(profile_picture)s, %(about_me)s, %(facebook)s, %(twitter)s, %(instagram)s, %(snapchat)s, %(linkedin)s, %(tiktok)s, %(friends_id)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def update(cls, data):
        query = "UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, email=%(email)s, phone_number=%(phone_number)s, password=%(password)s, profile_picture=%(profile_picture)s, about_me=%(about_me)s, facebook=%(facebook)s, twitter=%(twitter)s, instagram=%(instagram)s, snapchat=%(snapchat)s, linkedin=%(linkedin)s, tiktok=%(tiktok)s, WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def update_calendar(cls, user_id, calendar_data):
        try:
            query = "UPDATE users SET monday = %(monday)s, tuesday = %(tuesday)s, wednesday = %(wednesday)s, thursday = %(thursday)s, friday = %(friday)s, saturday = %(saturday)s, sunday = %(sunday)s WHERE id = %(user_id)s;"
            data = {
                'monday': calendar_data.get('monday'),
                'tuesday': calendar_data.get('tuesday'),
                'wednesday': calendar_data.get('wednesday'),
                'thursday': calendar_data.get('thursday'),
                'friday': calendar_data.get('friday'),
                'saturday': calendar_data.get('saturday'),
                'sunday': calendar_data.get('sunday'),
                'user_id': user_id
            }
            result = connectToMySQL(cls.db).query_db(query, data)
            return result
        except Exception as e:
            print(f"An error occurred while updating the user's calendar: {e}")
            return False
        
    @classmethod
    def update_status(cls, user_id, status):
        query = "UPDATE users SET status = %(status)s WHERE id = %(user_id)s;"
        data = {
            'status': status,
            'user_id': user_id
        }
        result = connectToMySQL(cls.db).query_db(query, data)
        return result
    
    @classmethod
    def update_location(cls, user_id, latitude, longitude):
        query = "UPDATE users SET latitude = %(latitude)s, longitude = %(longitude)s WHERE id = %(user_id)s;"
        data = {
            'latitude': latitude,
            'longitude': longitude,
            'user_id': user_id
        }
        result = connectToMySQL(cls.db).query_db(query, data)
        return result

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for row in results:
            users.append(cls(row))
        return users

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query, {'email': email})
        if not results:
            return False
        return cls(results[0])

    @classmethod
    def get_by_phone_number(cls, phone_number):
        query = "SELECT * FROM users WHERE phone_number = %(phone_number)s;"
        results = connectToMySQL(cls.db).query_db(query, {'phone_number': phone_number})
        if not results:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        data = {'id': id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if not result:
            return False
        return cls(result[0])
    
    @classmethod
    def get_by_friends_id(cls, friends_id):
        query = "SELECT * FROM users WHERE friends_id = %(friends_id)s;"
        results = connectToMySQL(cls.db).query_db(query, {'friends_id': friends_id})
        users = []
        for row in results:
            users.append(cls(row))
        return users


    @staticmethod
    def validate_user(user):
        is_valid = True
        if len(user['first_name']) < 2:
            flash("First name must be at least 2 characters")
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Last name must be at least 2 characters")
            is_valid = False
        if len(user['email']) < 1:
            flash("Email unusable.")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("Incorrect Email")
            is_valid = False
        if len(user['phone_number']) < 2:
            flash("Phone number must be at least 10 characters")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters")
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash("Password and confirmation password do not match.", "register")
            is_valid = False
        if len(user['about_me']) < 2:
            flash("Description must be at least 2 characters")
            is_valid = False
        if user['facebook'].startswith('/'):
            flash("Facebook registration must not start with '/'")
            is_valid = False
        if user['twitter'].startswith('@'):
            flash("Twitter registration must not start with '@'")
            is_valid = False
        if user['instagram'].startswith('@'):
            flash("Instagram registration must not start with '@'")
            is_valid = False
        if not user['snapchat'].startswith('@'):
            flash("Snapchat registration must start with '@'")
            is_valid = False
        if user['linkedin'].startswith('/'):
            flash("LinkedIn registration must not start with '/'")
            is_valid = False
        if not user['tiktok'].startswith('@'):
            flash("TikTok registration must start with '@'")
            is_valid = False
        return is_valid

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)