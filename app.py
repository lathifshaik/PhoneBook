from flask import Flask, render_template, url_for, redirect, request, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
import os

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://ilathifshaik:4MCQLGQP7wN8S8O0@cluster0.yxujzng.mongodb.net/phonebook?retryWrites=true&w=majority"
app.secret_key = 'screate/key'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# the rest of your routes go here

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            pw_hash = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
            users.insert_one({
                'name' : request.form['username'],
                'password' : pw_hash,
                'security_answer': request.form['security_answer']
            })
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')




@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user:
            if bcrypt.check_password_hash(login_user['password'], request.form['pass']):
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        return 'Invalid username/password combination'

    return render_template('login.html')


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'name' : request.form['username']})

        if user and user.get('security_answer') == request.form['security_answer']:
            pw_hash = bcrypt.generate_password_hash(request.form['new_password']).decode('utf-8')
            users.update_one({'_id': user['_id']}, {'$set': {'password': pw_hash}})
            return redirect(url_for('login'))

        return 'Invalid username or security answer!'

    return render_template('forgot_password.html')



@app.route('/')
def index():
    if 'username' in session:
        contacts = mongo.db.contacts.find({'username': session['username']})
        return render_template('dashboard.html', contacts=contacts)

    return render_template('index.html')


@app.route('/new_contact', methods=['POST', 'GET'])
def new_contact():
    if request.method == 'POST':
        contact = {
            'name': request.form.get('name'),
            'phone': request.form.get('phone'),
            'username': session['username']
        }

        contacts = mongo.db.contacts
        contacts.insert_one(contact)

        return redirect(url_for('index'))

    return render_template('new_contact.html')


@app.route('/delete_contact/<contact_id>')
def delete_contact(contact_id):
    contacts = mongo.db.contacts
    contacts.delete_one({'_id': ObjectId(contact_id)})
    
    return redirect(url_for('index'))

@app.route('/edit_contact/<contact_id>', methods=['POST', 'GET'])
def edit_contact(contact_id):
    if request.method == 'POST':
        contacts = mongo.db.contacts
        contacts.update_one(
            {'_id': ObjectId(contact_id)},
            {'$set':
                {
                    'name': request.form.get('name'),
                    'phone': request.form.get('phone')
                }
            }
        )
        return redirect(url_for('index'))

    contact = mongo.db.contacts.find_one({'_id': ObjectId(contact_id)})
    return render_template('edit_contact.html', contact=contact)

@app.route('/favourites')
def favourites():
    if 'username' in session:
        favourite_contacts = mongo.db.contacts.find({'username': session['username'], 'favourite': True})
        return render_template('favourites.html', contacts=favourite_contacts)

    return redirect(url_for('index'))  # redirect to login if not logged in


@app.route('/add_favourite/<contact_id>')
def add_favourite(contact_id):
    contacts = mongo.db.contacts
    contacts.update_one({'_id': ObjectId(contact_id)}, {'$set': {'favourite': True}})
    return redirect(url_for('index'))

@app.route('/remove_favourite/<contact_id>')
def remove_favourite(contact_id):
    contacts = mongo.db.contacts
    contacts.update_one({'_id': ObjectId(contact_id)}, {'$set': {'favourite': False}})
    return redirect(url_for('index'))

