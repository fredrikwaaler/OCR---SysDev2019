from flask_login import LoginManager, login_user, logout_user, login_required, current_user, login_fresh
import os, datetime, json, re
from flask import Flask, render_template, flash, request, redirect, url_for, session, g
from forms import *
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from werkzeug.utils import secure_filename
from HistoryPresenter import HistoryPresenter
from user import User
from PasswordHandler import PasswordHandler
from FormValidator import validate_new_name, validate_new_email, validate_new_password


def create_login_manager():
    """
    Handles the creation of a LoginManager for the app
    :return: A LoginManager for the app to use
    """
    lm = LoginManager()

    @lm.user_loader
    def load_user(email):
        return User.get_user(email)

    return lm


app = Flask(__name__)

#Navbar
nav = Nav(app)
app.config['SECRET_KEY'] = 'secretkey'

navbar = Navbar('',
    View('Kjøp', 'purchase'),
    View('Salg', 'sale'),
    View('Historikk', 'history'),
    View('Profil', 'profile')
)
nav.register_element('nav', navbar)

nav.init_app(app)

# Uploading files to server
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Associated the app with a login-manager
lm = create_login_manager()
lm.init_app(app)
lm.login_view = 'log_in'


@app.route('/purchase', methods=['GET'])
@login_required
def purchase(image='dummy.png', pop=False):
    form = PurchaseForm()
    customer_modal_form = CustomerForm()
    if pop:
        form.invoice_date.data =  string_to_datetime(pop['fakturadato'])
        form.maturity_date.data = string_to_datetime(pop['forfallsdato'])
        form.invoice_number.data = pop['fakturanummer']
        form.text.data = pop['tekst']
        form.gross_amount.data = pop['bruttobelop']
        form.net_amount.data = pop['nettobelop']
    return render_template('purchase.html', title="Kjoop", form=form, customer_modal_form=customer_modal_form, image=image,
                       current_user=current_user)


@app.route('/widget', methods=["GET"])
@login_required
def widget():
    form = PurchaseForm()
    return render_template('purchase_widget.html', form=form)


@app.route('/widget2', methods=["GET"])
@login_required
def widget2():
    form = SaleForm()
    return render_template('sale_widget.html', form=form)


@app.route('/sale', methods=['GET'])
@login_required
def sale():
    form = SaleForm()
    return render_template('sale.html', title="Salg", form=form, current_user=current_user)


@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    history_presenter = HistoryPresenter(current_user.fiken_manager)
    try:
        sales = history_presenter.get_sales_for_view()
        purchases = history_presenter.get_purchases_for_view()
    except ValueError:  # If the fm is not properly set for interaction.
        sales = []
        purchases = []

    # If the method is get, we just retrieved the page with default value "all".
    if request.method == 'GET':
        return render_template('history.html', title="Historikk", entry_view=sales + purchases, current_user=current_user)
    else:
        data_type = request.form["type"]
        if data_type == "all":
            return redirect(url_for('historikk'))
        elif data_type == "purchases":
            return render_template('history.html', title="Historikk", entry_view=purchases, checked="purchases", current_user=current_user)
        elif data_type == "sales":
            return render_template('history.html', title="Historikk", entry_view=sales, checked="sales", current_user=current_user)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    form = ProfileForm()
    fiken_modal_form = FikenModalForm()

    # Retrieve user-specific data
    name = current_user.name
    email = current_user.email

    if current_user.fiken_manager.has_valid_login():
        # Give all companies with each their int-key to the template.
        # Used for deciding which company is set active in the form.
        cmps = current_user.fiken_manager.get_company_info()
        companies = []
        for i in range(len(cmps)):
            companies.append((cmps[i], i))
    else:
        companies = []
    return render_template('profile.html', title="Profil", form=form, fiken_modal_form=fiken_modal_form, name=name, email=email,
                           companies=companies, current_user=current_user)


@app.route('/', methods=['GET', 'POST'])
@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if current_user.is_authenticated:
        return redirect(url_for('purchase'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data["email"]
        user = User.get_user(email)
        if user:
            password = form.data["password"]
            if PasswordHandler.compare_hash_with_text(user.password, password):
                login_user(user)
                current_user.store_user()
                next_page = request.args.get("next", url_for('purchase'))
                return redirect(next_page)
            else:
                flash("Invalid credentials, try again.")
        else:
            flash("Invalid credentials, try again.")
    return render_template('log_in.html', title="Logg inn", form=form)


@app.route('/log_out')
def log_out():
    logout_user()
    return redirect('log_in')


@app.route('/sign_up', methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('log_in'))

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
    if re.match('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$', password):
        return True
    else:
        return False


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotForm()
    return render_template('forgot_password.html', title="Glemt Passord", form=form)


@app.route('/upload_file', methods=['POST'])
@login_required
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
            return purchase(image=filename, pop=parsed_data)
    return "EMPTY PAGE"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/send_purchase_form', methods=['POST'])
@login_required
def send_purchase_form():
    result = request.form
    send_to_fiken(result, "Purchase")
    return render_template("result.html", result = result)


@app.route('/send_sale_form', methods=['POST'])
@login_required
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
@login_required
def change_name():
    new_name = request.form["new_name"].strip()
    validated, errors = validate_new_name(new_name)
    if validated:
        current_user.name = new_name
        current_user.store_user()
    else:
        # TODO - Display flash in html
        for error in errors:
            flash(error)
    return redirect(url_for('profile'))


@app.route('/change_email', methods=['POST'])
@login_required
def change_email():
    new_email = request.form["new_email"].strip()
    validated, errors = validate_new_email(new_email)
    if validated:
        current_user.change_email(new_email)
        login_user(current_user)
    else:
        # TODO - Display flash in html
        for error in errors:
            flash(error)
    return redirect(url_for('profile'))



@app.route('/change_fiken', methods=['POST'])
@login_required
def change_fiken():
    return "NONFUNCTIONAL > Change Fiken"


@app.route('/password', methods=['POST'])
@login_required
def change_password():
    new_pass = request.form["new_password"]
    repeat_pass = request.form["repeat_password"]
    validated, errors = validate_new_password(new_pass, repeat_pass)
    if validated:
        current_user.change_password(new_pass)
        login_user(current_user)
    else:
        # TODO - Display flash in html
        for error in errors:
            flash(error)
    return redirect(url_for('profile'))


@app.route('/set_active_company', methods=['POST'])
@login_required
def set_active_company():
    # In case no button was checked
    if "company_keys" in request.form.keys():
        new_active_index = int(request.form["company_keys"])
        new_active = current_user.fiken_manager.get_company_info()[new_active_index][2]  # Nr 2 in tuple is slug
        current_user.fiken_manager.set_company_slug(new_active)
        current_user.store_user()
    return redirect(url_for('profile'))


@app.route('/get_user_data', methods=['POST'])
@login_required
def get_user_data():
    return "NONFUNCTIONAL > Get user data"


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    return "NONFUNCTIONAL > Delete Account"


@app.route('/create_contact', methods=['POST'])
@login_required
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
