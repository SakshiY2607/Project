from unicodedata import category
from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

'''
to create the project database, open terminal
- type python and press enter
- type 
    from app import app, db
    with app.app_context():
        db.create_all()
- enter twice to confirm
'''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adminname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)   

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question= db.Column(db.String(1024), unique=True, nullable=False)
    option_A = db.Column(db.String(500), nullable=False)
    option_B = db.Column(db.String(500), nullable=False)
    option_C = db.Column(db.String(500), nullable=False)
    option_D = db.Column(db.String(500), nullable=False)
    answer=db.Column(db.String(500),nullable=False)
    category = db.Column(db.String(80), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)    

    def __str__(self):
        return f'{self.question}'

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        return f'{self.score} of {self.user_id}'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.sqlite'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'supersecretkeythatnooneknows'
    db.init_app(app)
    return app

app = create_app()

def create_login_session(user: User):
    session['id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    session['is_logged_in'] = True

def create_admin_session(admin:Admin):
    session['id'] = admin.id
    session['username'] = admin.adminname
    session['email'] = admin.email
    session['is_logged_in'] = True
    session['is_admin'] = True   
   

def destroy_login_session():
    if 'is_logged_in' in session:
        session.clear()


@app.route('/')
def index():
    return render_template('index.html')

# froute
@app.route('/login',  methods=['GET','POST'])
def login():
    errors = {}
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("LOGGIN IN",email, password)
        if password and email:
            if len(email) < 11 or '@' not in email:
                errors['email'] = 'Email is Invalid'
            if len(errors) == 0:
                user = User.query.filter_by(email=email).first()
                if user is not None:
                    print("user account found", user)
                    if user.password == password:
                        create_login_session(user)
                        flash('Login Successfull', "success")
                        return redirect('/')
                    else:
                        errors['password'] = 'Password is invalid'
                else:
                    errors['email']= 'Account does not exists'
        else:
            errors['email'] = 'Please fill valid details'
            errors['password'] = 'Please fill valid details'
    return render_template('login.html', errors = errors)

@app.route('/register', methods=['GET','POST'])
def register():
    errors = []
    if request.method == 'POST': # if form was submitted
        username = request.form.get('username')
        email = request.form.get('email')
        pwd = request.form.get('password')
        cpwd = request.form.get('confirmpass')
        print(username, email, pwd, cpwd)
        if username and email and pwd and cpwd:
            if len(username)<2:
                errors.append("Username is too small")
            if len(email) < 11 or '@' not in email:
                errors.append("Email is invalid")
            if len(pwd) < 6:
                errors.append("Password should be 6 or more chars")
            if pwd != cpwd:
                errors.append("passwords do not match")
            if len(errors) == 0:
                user = User(username=username, email=email, password=pwd)
                db.session.add(user)
                db.session.commit()
                flash('user account created','success')
                return redirect('/login')
        else:
            errors.append('Fill all the fields')
            flash('user account could not be created','warning')
    return render_template('register.html', error_list=errors)

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    errors = {}
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("LOGGIN IN",email, password)
        if password and email:
            if len(email) < 11 or '@' not in email:
                errors['email'] = 'Email is Invalid'
            if len(errors) == 0:
                admin = Admin.query.filter_by(email=email).first()
                if admin is not None:
                    print("admin account found", admin)
                    if admin.password == password:
                        create_admin_session(admin)
                        flash('Login Successfull', "success")
                        return redirect('/admin/dashboard')
                    else:
                        errors['password'] = 'Password is invalid'
                else:
                    errors['email']= 'Account does not exists'
        else:
            errors['email'] = 'Please fill valid details'
            errors['password'] = 'Please fill valid details'
    return render_template('admin_login.html', errors = errors)

@app.route('/admin/register', methods=['GET','POST'])
def admin_register():
    # if session.get('is_logged_in', False) and session.get('is_admin',False):
        errors = []
        if request.method == 'POST': # if form was submitted
            adminname = request.form.get('adminname')
            email = request.form.get('email')
            pwd = request.form.get('password')
            cpwd = request.form.get('confirmpass')
            print(adminname, email, pwd, cpwd)
            if adminname and email and pwd and cpwd:
                if len(adminname)<2:
                    errors.append("Adminname is too small")
                if len(email) < 11 or '@' not in email:
                    errors.append("Email is invalid")
                if len(pwd) < 6:
                    errors.append("Password should be 6 or more chars")
                if pwd != cpwd:
                    errors.append("passwords do not match")
                if len(errors) == 0:
                    admin = Admin(adminname=adminname, email=email, password=pwd)
                    db.session.add(admin)
                    db.session.commit()
                    flash('Admin account created','success')
                    return redirect('/admin_login')
            else:
                errors.append('Fill all the fields')
                flash('admin account could not be created','warning')
        return render_template('admin_register.html', error_list=errors)
     # else:
    #     flash('Login in admin to access this content','danger')
    #     return redirect('/')

@app.route('/admin/dashboard', methods=['GET','POST'])    
def admin():
    if session.get('is_logged_in', False) and session.get('is_admin',False):
        return render_template('admin_dashboard.html')
    else:
        flash('Login in admin to access this content','danger')
        return redirect('/')

@app.route('/logout')
def logout():
    destroy_login_session()
    flash('You are logged out','success')
    return redirect('/')    

@app.route('/quiz/add', methods=['GET','POST'])
def add_questions():
    if session.get('is_logged_in', False) and session.get('is_admin',False):
        errors = []
        if request.method == 'POST':
            question = request.form.get('question')
            option_A = request.form.get('option_A')
            option_B = request.form.get('option_B')
            option_C = request.form.get('option_C')
            option_D = request.form.get('option_D')
            answer = request.form.get('answer')
            category = request.form.get('category')
            print(question, option_A, option_B, option_C, option_D, answer, category)
            if question and option_A and option_B and option_C and option_D and answer and category:
                if len(question)<2:
                    errors.append("Question is too small")
                if len(option_A) < 1:
                    errors.append("Option A is invalid")
                if len(option_B) < 1:
                    errors.append("Option B is invalid")
                if len(option_C) < 1:
                    errors.append("Option C is invalid")
                if len(option_D) < 1:
                    errors.append("Option D is invalid")
                if len(answer) < 1:
                    errors.append("Answer is invalid")
                if len(errors) == 0:
                    quiz = Quiz(question=question, option_A=option_A, option_B=option_B, option_C=option_C, option_D=option_D, answer=answer, category=category)
                    db.session.add(quiz)
                    db.session.commit()
                    flash('Question added','success')
                    return redirect('/quiz/add')
            else:
                errors.append('Fill all the fields')
                flash('Question could not be added','warning')
        return render_template('add_question.html', error_list=errors)
    else:
        flash('Login in admin to access this content','danger')
        return redirect('/')

@app.route('/quiz/view')
def view_questions():
    if session.get('is_logged_in', False) and session.get('is_admin',False):
        questions = Quiz.query.all()
        return render_template('view_questions.html', questions=questions)
    else:
        flash('Login in admin to access this content','danger')
        return redirect('/')

@app.route('/quiz/delete/<int:id>')
def delete_question(id):
    if session.get('is_logged_in', False) and session.get('is_admin',False):
        question = Quiz.query.get(id)
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted','success')
        return redirect('/quiz/view')
    else:
        flash('Login in admin to access this content','danger')
        return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)