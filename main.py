from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json

# Load configuration parameters from a JSON file
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# Initialize the Flask application
local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Configure the SQLAlchemy database
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['proud_uri']

db = SQLAlchemy(app)

# Define database models using SQLAlchemy ORM
class Medicines(db.Model):
    # Define columns for the Medicines table
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    medicines = db.Column(db.String(500), nullable=False)
    products = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mid = db.Column(db.String(120), nullable=False)

class Posts(db.Model):
    # Define columns for the Posts table
    mid = db.Column(db.Integer, primary_key=True)
    medical_name = db.Column(db.String(80), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(120), nullable=False)

class Addmp(db.Model):
    # Define columns for the Addmp table
    sno = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String, nullable=False)

class Addpd(db.Model):
    # Define columns for the Addpd table
    sno = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String, nullable=False)

class Logs(db.Model):
    # Define columns for the Logs table
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String, nullable=True)
    action = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(100), nullable=False)

# Define routes and their corresponding functionalities
@app.route("/")
def hello():
    return render_template('index.html', params=params)

@app.route("/index")
def home():
    return render_template('dashbord.html', params=params)

@app.route("/details", methods=['GET', 'POST'])
def details():
    # Render the details template with data from the Logs table
    if 'user' in session and session['user'] == params['user']:
        posts = Logs.query.all()
        return render_template('details.html', params=params, posts=posts)

from sqlalchemy.exc import IntegrityError

@app.route("/insert", methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        mid = request.form.get('mid')
        medical_name = request.form.get('medical_name')
        owner_name = request.form.get('owner_name')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')

        # Validate phone number length
        if len(phone_no) != 10:
            flash("Mobile number must be exactly 10 digits", "danger")
            return redirect(request.referrer)

        # Check if the phone number already exists in the database
        existing_post = Posts.query.filter_by(phone_no=phone_no).first()
        if existing_post:
            flash("This mobile number already exists, please use a different one", "danger")
            return redirect(request.referrer)

        try:
            # Insert data into the Posts table
            push = Posts(mid=mid, medical_name=medical_name, owner_name=owner_name, phone_no=phone_no, address=address)
            db.session.add(push)
            db.session.commit()
            flash("Thanks for submitting your details", "success")
        except IntegrityError as e:
            db.session.rollback()
            flash("An error occurred while adding your details. Please try again.", "danger")

    return render_template('insert.html', params=params)

@app.route("/list", methods=['GET', 'POST'])
def post():
    # Render the post template with data from the Medicines table
    if 'user' in session and session['user'] == params['user']:
        posts = Medicines.query.all()
        return render_template('post.html', params=params, posts=posts)

@app.route("/items", methods=['GET', 'POST'])
def items():
    # Render the items template with data from the Addmp table
    if 'user' in session and session['user'] == params['user']:
        posts = Addmp.query.all()
        return render_template('items.html', params=params, posts=posts)

@app.route("/items2", methods=['GET', 'POST'])
def items2():
    # Render the items2 template with data from the Addpd table
    if 'user' in session and session['user'] == params['user']:
        posts = Addpd.query.all()
        return render_template('items2.html', params=params, posts=posts)

@app.route("/sp", methods=['GET', 'POST'])
def sp():
    # Render the store template with data from the Medicines table
    if 'user' in session and session['user'] == params['user']:
        posts = Medicines.query.all()
        return render_template('store.html', params=params, posts=posts)

@app.route("/logout")
def logout():
    # Logout the user by removing session data and redirect to login page
    session.pop('user')
    flash("You are logout", "primary")
    return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # User login functionality
    if 'user' in session and session['user'] == params['user']:
        posts = Posts.query.all()
        return render_template('dashbord.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('password')
        if username == params['user'] and userpass == params['password']:
            session['user'] = username
            posts = Posts.query.all()
            flash("You are Logged in", "primary")
            return render_template('index.html', params=params, posts=posts)
        else:
            flash("wrong password", "danger")
    return render_template('login.html', params=params)

@app.route("/edit/<string:mid>", methods=['GET', 'POST'])
def edit(mid):
    # Edit post functionality
    if 'user' in session and session['user'] == params['user']:
        if request.method == 'POST':
            medical_name = request.form.get('medical_name')
            owner_name = request.form.get('owner_name')
            phone_no = request.form.get('phone_no')
            address = request.form.get('address')

            if mid == 0:
                post = Posts(medical_name=medical_name, owner_name=owner_name, phone_no=phone_no, address=address)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(mid=mid).first()
                post.medical_name = medical_name
                post.owner_name = owner_name
                post.phone_no = phone_no
                post.address = address
                db.session.commit()
                flash("data updated ", "success")
                return redirect('/edit/' + mid)
        post = Posts.query.filter_by(mid=mid).first()
        return render_template('edit.html', params=params, post=post)

@app.route("/delete/<string:mid>", methods=['GET', 'POST'])
def delete(mid):
    # Delete post functionality
    if 'user' in session and session['user'] == params['user']:
        post = Posts.query.filter_by(mid=mid).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "warning")
    return redirect('/login')

@app.route("/deletemp/<string:id>", methods=['GET', 'POST'])
def deletemp(id):
    # Delete entry from Medicines table functionality
    if 'user' in session and session['user'] == params['user']:
        post = Medicines.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted Successfully", "primary")
    return redirect('/list')

@app.route("/medicines", methods=['GET', 'POST'])
def medicine():
    # Add entry to Medicines table functionality
    if request.method == 'POST':
        mid = request.form.get('mid')
        name = request.form.get('name')
        medicines = request.form.get('medicines')
        products = request.form.get('products')
        email = request.form.get('email')
        amount = request.form.get('amount')

        entry = Medicines(mid=mid, name=name, medicines=medicines, products=products, email=email, amount=amount)
        db.session.add(entry)
        db.session.commit()
        flash("Data Added Successfully", "primary")

    return render_template('medicine.html', params=params)

if __name__ == '__main__':
    app.run(debug=True)
