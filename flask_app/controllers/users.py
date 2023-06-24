from flask import render_template, request,session, redirect, flash, send_from_directory, jsonify, json
from flask_app import app
from flask_app import social_media_icons
from flask_app.models.user import User
from flask_app.models.friend import Friend
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create', methods=['POST'])
def create_user():
    if not User.validate_user(request.form):
        return redirect('/register')

    file = request.files['profile_picture']
    filename = None

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            print(f"File saved to: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

    user_data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "phone_number": request.form['phone_number'],
        "birthday": request.form['birthday'],
        "password": request.form['password'],
        "confirm_password": request.form['confirm_password'],
        "about_me": request.form['about_me'],
        "facebook": request.form['facebook'],
        "twitter": request.form['twitter'],
        "instagram": request.form['instagram'],
        "snapchat": request.form['snapchat'],
        "linkedin": request.form['linkedin'],
        "tiktok": request.form['tiktok'],
        "friends_id": request.form['friends_id'],
        "profile_picture": filename,
    }

    hashed_password = bcrypt.generate_password_hash(user_data['password'])
    user_data['password'] = hashed_password

    user_id = User.save(user_data)

    session['user_id'] = user_id

    return redirect('/dashboard')

@app.route('/returning', methods=['POST'])

def login_user():
    email_or_phone = request.form['email']
    password = request.form['password']

    user = User.get_by_email(email_or_phone)
    if not user:
        user = User.get_by_phone_number(email_or_phone)

    if not user or not User.check_password(user.password, password):
        flash("Invalid email or password", "login")
        return redirect('/login')

    session['user_id'] = user.id

    return redirect('/dashboard')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/create-group')
def create_group():
    return render_template('create_group.html')

@app.route('/group-made', methods=['POST'])
def group_made():
    # Process the form data and save it to the friends table
    name = request.form.get('name')
    Friend.save({'name': name})

    # Retrieve the group ID based on the friend's name
    group_id = Friend.get_group_id_by_name(name)
    
    # Return the group ID as a JSON response
    return jsonify(group_id=group_id)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')

    user = User.get_by_id(session['user_id'])
    friend = Friend.get_by_id(user.friends_id)
    group_members = []

    if user:
        group_members = User.get_by_friends_id(user.friends_id)  # Retrieve users with matching friends_id

    return render_template('dashboard.html', user=user, groupMembers=group_members, friend=friend)  # Pass groupMembers data to the template

@app.route('/update_availability', methods=['POST'])
def update_availability():
    user_id = session.get('user_id')

    if user_id:
        calendar_data = {}
        for day, availability in request.form.items():
            calendar_data[day] = availability

        updated = User.update_calendar(user_id, calendar_data)
        if updated:
            print("User calendar updated successfully")
        else:
            print("Failed to update user's calendar")
    else:
        print("User ID not found in the session")

    return jsonify({'message': 'Availability updated successfully'})

@app.route('/get_availability', methods=['GET'])
def get_availability():
    user_id = session.get('user_id')

    if user_id:
        # Retrieve the user from the database
        user = User.get_by_id(user_id)

        if user:
            # Extract the availability data from the user instance
            availability_data = {
                'monday': user.monday,
                'tuesday': user.tuesday,
                'wednesday': user.wednesday,
                'thursday': user.thursday,
                'friday': user.friday,
                'saturday': user.saturday,
                'sunday': user.sunday
            }

            # Return the availability data as JSON response
            return jsonify({'availability': availability_data})

        # If user is not found, return an error message
        return jsonify({'error': 'User not found'})

    # If user_id is not found in the session or other error occurs, return an error message
    return jsonify({'error': 'User ID not found or other error occurred'})

@app.route('/get_group_members', methods=['POST'])
def get_group_members():
    user_id = session.get('user_id')
    
    if user_id:
        user = User.get_by_id(user_id)
        friends_id = user.friends_id

        # Retrieve users with matching friends_id from the database
        group_members = User.get_by_friends_id(friends_id)

        # Create a list of member data including calendars
        member_data = []
        for member in group_members:
            member_info = {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'calendar': {
                    'monday': member.monday,
                    'tuesday': member.tuesday,
                    'wednesday': member.wednesday,
                    'thursday': member.thursday,
                    'friday': member.friday,
                    'saturday': member.saturday,
                    'sunday': member.sunday
                }
            }
            member_data.append(member_info)

        return jsonify({'members': member_data})

    return jsonify({'error': 'User ID not found or other error occurred'})



@app.route('/user/<int:user_id>')
def user_profile(user_id):
    if 'user_id' not in session:
        return redirect('/logout')
    
    user = User.get_by_id(user_id)

    return render_template('my_profile.html', user=user, social_media_icons=social_media_icons)

@app.route('/user/edit/<int:user_id>')
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect('/logout')
    
    user = User.get_by_id(user_id)

    return render_template('edit_profile.html', user=user)

@app.route('/user/update/<int:user_id>', methods=['POST'])
def update_user(user_id):
    if 'user_id' not in session:
        return redirect('/logout')

    if not User.validate_user(request.form):
        return redirect(f'/user/edit/{user_id}')

    user = User.get_by_id(user_id)

    if 'password' in request.form:
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password)
    else:
        hashed_password = user.password

    file = request.files['profile_picture']
    filename = user.profile_picture

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if user.profile_picture != filename:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture))

    user_data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "phone_number": request.form['phone_number'],
        "birthday": request.form['birthday'],
        "password": request.form['password'],
        "confirm_password": request.form['confirm_password'],
        "about_me": request.form['about_me'],
        "facebook": request.form['facebook'],
        "twitter": request.form['twitter'],
        "instagram": request.form['instagram'],
        "snapchat": request.form['snapchat'],
        "linkedin": request.form['linkedin'],
        "tiktok": request.form['tiktok'],
        "profile_picture": request.files['profile_picture'],
    }


    User.update(user_data)

    return redirect(f'/user/{user_id}')

@app.route('/status/<int:user_id>')
def status(user_id):
    if 'user_id' not in session:
        return redirect('/logout')
    
    user = User.get_by_id(session['user_id'])
    
    return render_template('status.html', user=user)

@app.route('/status/update/<int:user_id>', methods=['POST'])
def update_status(user_id):
    if 'user_id' not in session:
        return redirect('/logout')

    # Retrieve the user from the database
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({'error': 'User not found'})

    # Update the status of the user
    status = request.form['status']
    User.update_status(user_id, status)

    # Redirect to the user's profile page
    return redirect('/dashboard')

@app.route('/update-location', methods=['POST'])
def update_location():
    user_id = session.get('user_id')

    if user_id:
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')

        # Update the user's location in the database
        User.update_location(user_id, latitude, longitude)

        return jsonify({'message': 'Location updated successfully'})
    else:
        return jsonify({'error': 'User ID not found or other error occurred'})


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
