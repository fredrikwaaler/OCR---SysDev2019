import os, datetime, json
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
def kjoop(image='dummy.png', pop=False):
    form = KjoopForm()
    
    if pop:
        #TODO - Add formatting for datetime from json file
        form.fakturadato.data =  datetime.datetime(2000, 1, 1)
        form.forfallsdato.data = datetime.datetime(3000, 1, 1)
        form.fakturanummer.data = pop['fakturanummer']
        form.tekst.data = pop['tekst']
        form.bruttobelop.data = pop['bruttobelop']
        form.nettobelop.data = pop['nettobelop']
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
            # TODO - Send send image for parsing

            # TODO - Retrieve parsed json data
            # Change filename here when adding own parsed data
            with open('test_population.json', 'r') as f:
                parsed_data = json.load(f)
            return kjoop(image=filename, pop=parsed_data)
    return "EMPTY PAGE"

@app.route('/send_purchase_form', methods=['POST'])
def send_purchase_form():
    result = request.form
    send_to_fiken(result, "Purchase")
    
    return render_template("result.html", result = result)

@app.route('/send_sale_form', methods=['POST'])
def send_sale_form():
    result = request.form
    send_to_fiken(result, "Sale")

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

# Functions that can be moved to different file later
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_to_fiken(data, type):
    if type == "Purchase":
        # TODO - Make HAL json of data and send to Fiken API
        with open('test_purchase.json', 'w') as outfile:
            entry = {data}
            json.dump(data, outfile)
    if type == "Sale":
        with open('test_sale.json', 'w') as outfile:
            entry = {data}
            json.dump(data, outfile)

if __name__ == '__main__':
    app.run(debug=True)