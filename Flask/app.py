import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from forms import LoginForm, ForgotForm, KjoopForm, SalgForm, ProfilForm
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
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
@app.route('/kjoop', methods=['GET'])
def kjoop(image=None):
    form = KjoopForm()
    return render_template('kjoop.html', title="Kjoop", form=form, image=image)


@app.route('/salg', methods=['GET'])
def salg():
    form = SalgForm()
    return render_template('salg.html', title="Salg", form=form)


@app.route('/historikk')
def historikk():
    return render_template('historikk.html', title="Historikk")


@app.route('/profil', methods=['GET'])
def profil():
    form = ProfilForm()
    #TODO - Get profile data from database
    name = "Ola Normann"
    email = "ola@normann.no"
    return render_template('profil.html', title="Profil", form=form, name=name, email=email)


@app.route('/logg_inn', methods=['GET', 'POST'])
def logg_inn():
    form = LoginForm()

    if form.validate_on_submit():
        return "Login-form validated"

    return render_template('logg_inn.html', title="Logg inn", form=form)


@app.route('/glemt_passord', methods=['GET', 'POST'])
def glemt_passord():
    form = ForgotForm()
    return render_template('glemt_passord.html', title="Glemt Passord", form=form)

'''
POST FUNCTIONS
'''
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
            return kjoop(image=filename)
    return "EMPTY PAGE"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/send_purchase_form', methods=['POST'])
def send_purchase_form():
    result = request.form
    return render_template("result.html", result = result)

@app.route('/send_sale_form', methods=['POST'])
def send_sale_form():
    result = request.form
    return render_template("result.html", result = result)

@app.route('/change_name', methods=['POST'])
def change_name():
    return "NONFUNCTIONAL > Change Name"

@app.route('/change_email', methods=['POST'])
def change_email():
    return "NONFUNCTIONAL > Change Email"

@app.route('/change_fiken', methods=['POST'])
def change_fiken():
    return "NONFUNCTIONAL > Change Fiken"

@app.route('/password', methods=['POST'])
def change_password():
    return "NONFUNCTIONAL > Change Password"

@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    return "NONFUCNTIONAL > Get user data"

@app.route('/delete_account', methods=['POST'])
def delete_account():
    return "NONFUCTIONAL > Delete Account"

if __name__ == '__main__':
    app.run(debug=True)