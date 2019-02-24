import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from forms import LoginForm, ForgotForm, KjoopForm, SalgForm
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from werkzeug.utils import secure_filename



app = Flask(__name__)
#Navbar
nav = Nav(app)
app.config['SECRET_KEY'] = 'secretkey'

navbar = Navbar('',
    View('Kjøp', 'kjoop'),
    View('Salg', 'salg'),
    View('Historikk', 'historikk'),
    View('Profil', 'profil')
)
nav.register_element('nav', navbar)

nav.init_app(app)

#Uploading files to server
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
@app.route('/kjoop', methods=['GET', 'POST'])
def kjoop():
    form = KjoopForm()

    if form.validate_on_submit():
        return "Kjoop-form validated"

    return render_template('kjoop.html', title="Kjoop", form=form)


@app.route('/salg', methods=['GET', 'POST'])
def salg():
    form = SalgForm()

    if form.validate_on_submit():
        return "Salg-form validated"

    return render_template('salg.html', title="Salg", form=form)


@app.route('/historikk')
def historikk():
    return render_template('historikk.html', title="Historikk")


@app.route('/profil')
def profil():
    return render_template('profil.html', title="Profil")


@app.route('/logg_inn', methods=['GET', 'POST'])
def logg_inn():
    form = LoginForm()

    if form.validate_on_submit():
        return "Login-form validated"

    return render_template('logg_inn.html', title="Logg inn", form=form)


@app.route('/glemt_passord', methods=['GET', 'POST'])
def glemt_passord():
    form = ForgotForm()

    if form.validate_on_submit():
        return "Forgot-form validated"
    return render_template('glemt_passord.html', title="Glemt Passord", form=form)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "success"
    return "None"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
if __name__ == '__main__':
    app.run(debug=True)