
import os, datetime, json, re
from flask import Flask, render_template, flash, request, redirect, url_for, session, g
from flask_wtf import FlaskForm
from forms import *
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from werkzeug.utils import secure_filename
from FikenManager import FikenManager
from HistoryPresenter import HistoryPresenter


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

# Create a fiken manager. //TODO Should be created upon log-in.
app.config["FIKEN_MANAGER"] = FikenManager('fredrik.waaler@hotmail.no', host="localhost", database="Sukkertoppen", user="postgres", password="Sebas10an99")
# app.config["FIKEN_MANAGER"] = FikenManager('fredrik.waaler@hotmail.no', host="localhost", database="Sukkertoppen", user="postgres", password="Sebas10an99")
# app.config["FIKEN_MANAGER"].set_company_slug("fiken-demo-glass-og-yoga-as2")


@app.route('/kjoop', methods=['GET'])
def kjoop(image='dummy.png', pop=False):
    form = KjoopForm()
    customer_modal_form = CustomerForm()
    # TODO - Use current_user instead of app
    if pop:
        form.fakturadato.data =  string_to_datetime(pop['fakturadato'])
        form.forfallsdato.data = string_to_datetime(pop['forfallsdato'])
        form.fakturanummer.data = pop['fakturanummer']
        form.tekst.data = pop['tekst']
        form.bruttobelop.data = pop['bruttobelop']
        form.nettobelop.data = pop['nettobelop']
    return render_template('kjoop.html', title="Kjoop", form=form, customer_modal_form=customer_modal_form, image=image, current_user=app)

git
@app.route('/salg', methods=['GET'])
def salg():
    form = SalgForm()
    # TODO - Use current_user instead of app
    return render_template('salg.html', title="Salg", form=form, current_user=app)


@app.route('/historikk', methods=['GET', 'POST'])
def historikk():
    history_presenter = HistoryPresenter(app.config["FIKEN_MANAGER"])
    # TODO - Should use user-specific FM.
    try:
        sales = history_presenter.get_sales_for_view()
        purchases = history_presenter.get_purchases_for_view()
    except ValueError:
        sales = []
        purchases = []
    # TODO - Use current_user instead of app

    # If the method is get, we just retrieved the page with default value "all".
    if request.method == 'GET':
        return render_template('historikk.html', title="Historikk", entry_view=sales + purchases, current_user=app)
    else:
        data_type = request.form["type"]
        if data_type == "all":
            return redirect(url_for('historikk'))
        elif data_type == "purchases":
            return render_template('historikk.html', title="Historikk", entry_view=purchases, checked="purchases", current_user=app)
        elif data_type == "sales":
            return render_template('historikk.html', title="Historikk", entry_view=sales, checked="sales", current_user=app)


@app.route('/profil', methods=['GET'])
def profil():
    form = ProfilForm()
    fiken_modal_form = FikenModalForm()
    # TODO - Get profile data from database
    name = "Ola Normann"
    email = "ola@normann.no"
    # TODO - Should be retrieved from user-specific FM.
    # TODO - current_user should be current_user, not app
    cmps = app.config["FIKEN_MANAGER"].get_company_info()
    companies = []
    for i in range(len(cmps)):
        companies.append((cmps[i], i))
    return render_template('profil.html', title="Profil", form=form, fiken_modal_form=fiken_modal_form, name=name, email=email,
                           companies=companies, current_user=app)


@app.route('/')
@app.route('/logg_inn', methods=['GET', 'POST'])
def logg_inn():
    form = LoginForm()
    if request.method == 'POST':
        return 'POST'

    return render_template('logg_inn.html', title="Logg inn", form=form)

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if request.method == 'POST':
        fault = False
        if not is_filled_out(form):
            flash("Alle felter må fylles ut")
            fault = True
        if not is_valid_email(form.email.data):
            flash("E-post er ikke en gyldig addresse")
            fault = True
        if not is_valid_password(form.password.data):
            flash("Passord er ugyldig (Minst 8 karakterer)")
            if not form.password.data == form.repeat_password.data:
                flash("Passord må være likt")
            fault = True

        if not fault:
            # TODO - Create new user in database
            session['email'] = 'test_value'
            return redirect(url_for('logg_inn'))

    return render_template('sign_up.html', title="Sign up", form=form)


def is_filled_out(form):
    """
    Checks if a form is completely filled out.
    :param form: The form to be checked
    :return: True if form is filled out, False if something is missing
    """
    for entry in form:
        if entry.data == '':
            if not entry.name == 'csrf_token':
                return False
    return True


def is_valid_email(email):
    """
    Checks if an email string is a valid email.
    :param email: The email to be checked
    :return: True if email is valid, False if email is invalid.
    """
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        return True
    else:
        return False


def is_valid_password(password):
    """
    Checks if password is a valid password
    :param password: The password to be checked
    :return: True if password is valid, False if password is invalid.
    """
    if re.match('[A-Za-z0-9@#$%^&+=]{8,}', password):
        return True
    else:
        return False


@app.route('/glemt_passord', methods=['GET', 'POST'])
def glemt_passord():
    form = ForgotForm()
    return render_template('glemt_passord.html', title="Glemt Passord", form=form)


'''
SESSION FUNCTIONS
'''


@app.before_request
def before_request():
    g.user = None
    if 'key' in session:
        g.user = session['key']


@app.route('/set_session_id')
def set_session_id():
    """
    Sets a Test Session ID.
    :return: 'Test Session ID set'
    """
    session['key'] = 'value'
    return 'Test Session ID set'


@app.route('/get_session_id')
def get_session_id():
    """
    Checks if session id for Test Session ID is set
    :return: 'value' if set, 'not set' if not set
    """
    return session.get('key', 'not set')


@app.route('/drop_session')
def drop_session():
    """
    Drops the Test Session
    :return: 'Session dropped'
    """
    session.pop('key', None)
    return 'Session dropped'


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


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


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


@app.route('/set_active_company', methods=['POST'])
def set_active_company():
    # Todo - must be changed to handle user-specific FM
    fm = app.config["FIKEN_MANAGER"]
    new_active_index = int(request.form["company_keys"])
    new_active = fm.get_company_info()[new_active_index][2]  # Nr 2 in tuple is slug
    fm.set_company_slug(new_active)
    return redirect(url_for('profil'))


@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    return "NONFUNCTIONAL > Get user data"



@app.route('/delete_account', methods=['POST'])
def delete_account():
    return "NONFUNCTIONAL > Delete Account"


@app.route('/create_contact', methods=['POST'])
def create_contact():
    return "NONFUNCTIONAL > Create Contact"


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


def string_to_datetime(input_string):
    """
    Changes datatype of string to a datetime object
    :param input_string Date in format YYYY-MM-DD
    """
    split = input_string.split("-")
    date = datetime.datetime(int(split[0]), int(split[1]), int(split[2]))
    print(date)
    return date


if __name__ == '__main__':
    app.run(debug=True, port="8000")
