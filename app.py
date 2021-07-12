import os
from flask import Flask, render_template, redirect, url_for,request,session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,SelectField
from wtforms.validators import InputRequired, Email, Length,EqualTo
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail,Message

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123@localhost/education2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)


app.config['DEBUG'] = True
app.config["TESTING"] = False
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '93b6e2adccedc9'
app.config['MAIL_PASSWORD'] = '825b6b038df8b5'
app.config['MAIL_DEFAULT_SENDER'] = '7711173e43-a248f8@inbox.mailtrap.io'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False




class User(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    tele = db.Column(db.String(20))
    niveau = db.Column(db.String(20))
    sexe = db.Column(db.String(20))

class CountSexe:
    # Count All
    sql = text('select username from students WHERE admin IS NULL')
    result = db.engine.execute(sql)
    names = [row[0] for row in result]
    if len(names) > 0:
        NbAll = len(names)
    else:
        NbAll = 1

    # Count Male
    sql = text('select username from students WHERE sexe = "ch1" and admin IS NULL')
    result = db.engine.execute(sql)
    names = [row[0] for row in result]
    if len(names) > 0:
        NbMale = (len(names) * 100) / NbAll
    else:
        NbMale = 1
    # Count Female
    sql = text('select username from students WHERE sexe = "ch2" and admin IS NULL')
    result = db.engine.execute(sql)
    names = [row[0] for row in result]
    if len(names) > 0 :
        NbFemale = (len(names) * 100) / NbAll
    else:
        NbFemale = 1
class CountNiveau:
    #AllNiveau
    sql = text('select username from students')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    allNiveau = len(eles)
    #Niveau-Bac
    sql = text('select username from students WHERE niveau = "n1"')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    sansBac = len(eles)
    # NiveauBac
    sql = text('select username from students WHERE niveau = "n2"')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    withBac = len(eles)
    # Niveau1Bac
    sql = text('select username from students WHERE niveau = "n3"')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    bac1 = len(eles)
    # Niveau2Bac
    sql = text('select username from students WHERE niveau = "n4"')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    bac2 = len(eles)
    # Niveau3Bac
    sql = text('select username from students WHERE niveau = "n5"')
    result = db.engine.execute(sql)
    eles = [row[0] for row in result]
    bac3 = len(eles)

class SelectAllUser:

    sql = text('select id,username,email,tele,niveau,sexe from students')
    res = db.engine.execute(sql)
    selectAll = [row for row in res]
    lenAll = len(selectAll[0])



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    tele = StringField('N°Telephone : ', validators=[Length(min=8, max=13)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80),EqualTo('confirm',message='confirme your password')])
    confirm = PasswordField('Confirme Password')
    niveau = SelectField('Niveau SCL: ',choices=[('n0', '....'), ('n1', '-bac'), ('n2', 'bac'), ('n3', 'bac+2'), ('n4', 'bac+3'),('n5', 'bac++')], validators=[InputRequired()])
    sexe = SelectField('Sexe : ', choices=[('ch0', '.....'), ('ch1', 'Male'), ('ch2', 'Female')],validators=[InputRequired()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data and not(user.admin):
                login_user(user, remember=form.remember.data)
                session['id'] = user.id
                return redirect(url_for('dashboard'))
            elif user.password == form.password.data and user.admin:
                login_user(user, remember=form.remember.data)
                session['admin'] = user.admin
                return redirect(url_for('admin'))
        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route("/forget")
def forget():
    return render_template("sendingPass.html")


@app.route("/sendPass",methods=["POST"])
def sendPass():
    email = request.form["email"]
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message(f"Your Password is : {user.password}", sender='7711173e43-a248f8@inbox.mailtrap.io', recipients=['someone1@gmail.com'])
        msg.body = f"Your Password is : {user.password}"
        mail.send(msg)
        return "Send Seccuss "
    else:
        return "not found Email"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():

        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data,
                        tele=form.tele.data, niveau=form.niveau.data, sexe=form.sexe.data)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'


    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    uId = session['id']
    result = []
    # ID
    sql = text(f"select id from students WHERE id = {uId}")
    exec = db.engine.execute(sql)
    exec = [row[0] for row in exec]
    result += exec
    # Email
    sql = text(f"select email from students WHERE id = {uId}")
    exec = db.engine.execute(sql)
    exec = [row[0] for row in exec]
    result += exec
    # Tele
    sql = text(f"select tele from students WHERE id = {uId}")
    exec = db.engine.execute(sql)
    exec = [row[0] for row in exec]
    result += exec
    # Niveau
    sql = text(f"select niveau from students WHERE id = {uId}")
    exec = db.engine.execute(sql)
    exec = [row[0] for row in exec]
    result += exec
    # Sexe
    sql = text(f"select sexe from students WHERE id = {uId}")
    exec = db.engine.execute(sql)
    exec = [row[0] for row in exec]
    result += exec
    # result += [row[1] for row in result]


    return render_template('dashboard.html', name=current_user.username,result=result)



@app.route('/admin')
@login_required
def admin():
    if session['admin']:
        countSexeAll = CountSexe.NbAll
        countSexeMale = CountSexe.NbMale
        countSexeFemale = CountSexe.NbFemale
        # NiveauScolaire
        NiveauAll = CountNiveau.allNiveau
        sansBac = CountNiveau.sansBac
        withBac = CountNiveau.withBac
        Bac1 = CountNiveau.bac1
        Bac2 = CountNiveau.bac2
        Bac3 = CountNiveau.bac3
        niveau = [sansBac, withBac, Bac1, Bac2, Bac3]
        # SelectAllUser
        selectAll = SelectAllUser.selectAll
        lenAll = SelectAllUser.lenAll
        return render_template('admin.html', countSexeAll=countSexeAll, countSexeMale=countSexeMale,
                               countSexeFemale=countSexeFemale, niveau=niveau, selectAll=selectAll, lenAll=lenAll)
    return render_template('login.html')
@app.route('/supprimer',methods=["GET","POST"])
def supprimer():
    if request.method == "POST":
        myId = request.form['myId']
        myId = str(myId)
        sql = text(f"DELETE FROM students WHERE id = '{myId}'")
        db.engine.execute(sql)
        return redirect(url_for('admin'))
    return "Login via the login Form "
@app.route('/upgrad',methods=["GET","POST"])
def upgrad():
    if request.method == "POST":
        myIdU = request.form['myIdU']
        choix = request.form['choix']
        valeur = request.form['valeur']
        sql = text(f"UPDATE students SET {choix} = '{valeur}' WHERE id = '{myIdU}'")
        db.engine.execute(sql)
        return "Seccus Please roload the page"
    return "Login via the login Form"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)