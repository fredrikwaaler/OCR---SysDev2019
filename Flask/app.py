from flask_login import LoginManager, login_user, logout_user, login_required, current_user, login_fresh
import os, datetime, json, re

from flask import Flask, render_template, flash, request, redirect, url_for, abort, Markup
from forms import *
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from werkzeug.utils import secure_filename
from HistoryDataFormatter import HistoryDataFormatter
from user import User
from PasswordHandler import PasswordHandler
from FormValidator import validate_new_name, validate_new_email, validate_new_password, validate_new_fiken_user, validate_sign_up
from SalesDataFormatter import SalesDataFormatter
from mailer import Mailer
import smtplib


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

# Get setting for configuration
app.config.from_object('settings')

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
def purchase(image=None, pop=False):
    form = PurchaseForm()
    customer_modal_form = CustomerForm()
    if pop:
        form.invoice_date.data =  string_to_datetime(pop['fakturadato'])
        form.maturity_date.data = string_to_datetime(pop['forfallsdato'])
        form.invoice_number.data = pop['fakturanummer']
        form.text.data = pop['tekst']
        form.gross_amount.data = pop['bruttobelop']
        form.net_amount.data = pop['nettobelop']
    return render_template('purchase.html', title="Kjøp", form=form, customer_modal_form=customer_modal_form,
                           image=image, current_user=current_user)


@app.route('/sale', methods=['GET'])
@login_required
def sale():
    form = SaleForm()
    customer_modal_form = CustomerForm()
    account_modal_form = AccountForm()
    return render_template('sale.html', title="Salg", form=form, customer_modal_form=customer_modal_form,
                           account_modal_form=account_modal_form, current_user=current_user)


@app.route('/sale2', methods=['GET', 'POST'])
def sale2():
    form = SaleForm()
    if request.method == 'POST':
        # TODO - Validate form before sending to SalesDataFormatter
        a = SalesDataFormatter.ready_data_for_invoice(request.form)
        current_user.fiken_manager.post_data_to_fiken(a, "create_invoice")
        # TODO - Give user-feedback on send-in
        return redirect(url_for('sale2'))

    else:
        try:
            # Retrieve all bank_accounts from fiken.
            bank_accounts = current_user.fiken_manager.get_data_from_fiken(data_type="payment_accounts", links=True)
            # Get the bank_accounts in a presentable format
            bank_accounts = SalesDataFormatter.get_account_strings(bank_accounts)

            # Retrieve all contacts from fiken
            contacts = current_user.fiken_manager.get_data_from_fiken(data_type="contacts", links=True)
            # Retrieve the customers in a presentable format.
            customers = SalesDataFormatter.get_customer_strings(contacts)

            # Retrieve all products from fiken
            products = current_user.fiken_manager.get_data_from_fiken(data_type="products", links=True)
            # Retrieve the products in a presentable format
            products = SalesDataFormatter.get_product_strings(products)

        # If we get a ValueError, it means that fiken-manager is not set properly to interact with fiken.
        # Thus, we have no data to retrieve from fiken, and the lists should be empty.
        except ValueError:
            bank_accounts = []
            customers = []
            products = []
        return render_template('sale_widget.html', title="Salg", form=form, products=products,
                               bank_accounts=bank_accounts, customers=customers)


@app.route('/purchase2', methods=['GET', 'POST'])
def purchase2():
    form = PurchaseForm()
    return render_template('purchase_widget.html', title="Kjøp", form=form)


@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    history_presenter = HistoryDataFormatter(current_user.fiken_manager)
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
    confirm_password_form = ConfirmPasswordForm()

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
    return render_template('profile.html', title="Profil", form=form, fiken_modal_form=fiken_modal_form,
                           confirm_password_form=confirm_password_form, name=name, email=email,
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
    return redirect(url_for('log_in'))


@app.route('/sign_up', methods=['GET', 'POST'])
@login_required
def sign_up():
    if not current_user.is_admin:
        abort(401)
    form = SignUpForm()
    if form.is_submitted():
        name = form.data["name"]
        email = form.data["email"]
        admin = form.data["admin"]
        validated, errors = validate_sign_up(name, email)
        if validated:
            new_password = PasswordHandler.generate_random_password()
            hashed_new = PasswordHandler.generate_hashed_password(new_password)
            try:
                mailer = Mailer(app.config["MAIL_LOGIN"], app.config["MAIL_PASSWORD"])
                mailer.open_server()
                mailer.send_new_user(email, new_password)
                mailer.close_server()
                flash("Bruker suksessfullt registrert. Mail sendt til bruker med info.", "success")

                # Create new user and store to DB
                new_user = User(email, hashed_new, name, admin)
                new_user.store_user()
            except smtplib.SMTPException:
                flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
        else:
            for error in errors:
                flash(error)

        return redirect(url_for('sign_up'))

    return render_template('sign_up.html', title='Sign up', form=form)


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
    if form.validate_on_submit():
        email = form.data["email"]
        if User.user_exists(email):
            user = User.get_user(email)
            new_password = user.generate_new_password()

            try:
                mailer = Mailer(app.config["MAIL_LOGIN"], app.config["MAIL_PASSWORD"])
                mailer.open_server()
                mailer.send_password_reset(email, new_password)
                mailer.close_server()
            except smtplib.SMTPException:
                flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
        else:
            flash("Obs: Finner ingen bruker med den angitte epsoten.")

        return redirect(url_for('log_in'))

    return render_template('forgot_password.html', title="Glemt Passord", form=form)


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html', title="Hjelp")


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
            return purchase(image=filename, pop=None)
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


@app.route('/send_sale_form', methods=['POST', 'GET'])
@login_required
def send_sale_form(form):
    send_to_fiken(form, "Sale")

    return render_template("result.html", result = form)


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
        flash("Ditt navn er nå endret til {}.".format(new_name))
    else:
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
        flash("Din epost er nå endret til {}.".format(new_email))
    else:
        for error in errors:
            flash(error)
    return redirect(url_for('profile'))


@app.route('/change_fiken', methods=['POST'])
@login_required
def change_fiken():
    login = request.form["email"]
    password = request.form["password"]

    validated, errors = validate_new_fiken_user(login, password)
    if validated:
        prev_logged_in = current_user.fiken_manager.has_valid_login()
        current_user.fiken_manager.set_fiken_credentials(login, password)
        current_user.store_user()
        if not prev_logged_in:
            flash("Logget inn på fiken som \"{}\"".format(login))
        else:
            flash("Endret fikenbruker til \"{}\"".format(login))
    else:
        for error in errors:
            flash(error)
    return redirect(url_for('profile'))


@app.route('/password', methods=['POST'])
@login_required
def change_password():
    new_pass = request.form["new_password"]
    repeat_pass = request.form["repeat_password"]
    validated, errors = validate_new_password(new_pass, repeat_pass)
    if validated:
        current_user.change_password(new_pass)
        login_user(current_user)
        flash("Passordet er nå endret.")
    else:
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
        new_active_firm = current_user.fiken_manager.get_company_info()[new_active_index][0]
        current_user.fiken_manager.set_company_slug(new_active)
        current_user.store_user()
        flash("{} satt som nytt aktivt selskap i fiken.".format(new_active_firm))
    return redirect(url_for('profile'))


@app.route('/log_out_fiken', methods=['GET'])
@login_required
def log_out_fiken():
    current_user.fiken_manager.set_fiken_credentials(None, None)
    current_user.fiken_manager.reset_slug()
    current_user.store_user()
    flash("Du er nå logget ut av fiken.")
    return redirect(url_for('profile'))


@app.route('/get_user_data', methods=['POST'])
@login_required
def get_user_data():
    return "NONFUNCTIONAL > Get user data"


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if PasswordHandler.compare_hash_with_text(current_user.password, request.form["password"]):
        current_user.delete_user()
        logout_user()
        return redirect(url_for('log_in'))
    else:
        flash("Passordet stemmer ikke. Vennligst prøv på nytt.")
        return redirect(url_for('profile'))


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


@app.route('/widget', methods=['GET'])
@login_required
def widget():
    form = PurchaseForm()
    return render_template("purchase_widget.html", form=form)


@app.route('/widget2', methods=['GET'])
@login_required
def widget2():
    form = SaleForm()
    return render_template("sale_widget.html", form=form)


# checks if the user is logged in
def is_logged_in():
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
    return logged_in

# TODO - view all pages, see that they look ok and behave
# TODO - make sure every page is necessary 
# forbidden page, ex: accessing admin site, admin
@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html', title="403 forbidden page", logged_in=is_logged_in()), 403


# page not found, used when accessing nonsense, eg. /pasta
#@app.app_errorhandler(404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="404 not found", logged_in=is_logged_in()), 404


# method not allowed, ex: when accessing upload_files
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html', title="405 method not allowed", logged_in=is_logged_in()), 405


# file no longer exists, ex: accessing a file that used to exist
# used when ???
# TODO - remove errir code 410
@app.errorhandler(410)
def page_gone(e):
    return render_template('410.html', title="410 not found", logged_in=is_logged_in()), 410


# 415 - unsupported media type, ex: user send a svg image.
# TODO - PORT IT AS A FLASH
@app.errorhandler(415)
def unsupported_media_type(e):
    return render_template('415.html', title="415 unsupported media type", logged_in=is_logged_in()), 415


# internal server error, ex: server is up, but not working right
# used when azure fucks up
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="500 internal server error", logged_in=is_logged_in()), 500


# Web server isn't available, ex: our server is down
# used when azure fucks up
@app.errorhandler(503)
def service_unavailable(e):
    return render_template('503.html', title="503 service unavailable", logged_in=is_logged_in()), 503


# Server failed to communicate with secondary server, ex: fiken or vision fails
# used when vision or fiken fucks up
@app.errorhandler(504)
def gateway_timeout(e):
    return render_template('504.html', title="504 gateway timeout", logged_in=is_logged_in()), 504


# This is just temp routing to make error pages easily accessable for debugging
# TODO - remove the temp routing when error pages have been properly integraed
@app.route('/403', methods=['GET'])
def page_forbidden_page():
    return render_template('403.html', title="400 forbidden page"), 403


@app.route('/404', methods=['GET'])
def page_not_found_page():
    return render_template('404.html', title="404 page not found"), 404


@app.route('/405', methods=['GET'])
def method_not_allowed_page():
    return render_template('405.html', title="405 method not allowed"), 405


@app.route('/415', methods=['GET'])
def unsupported_media_type_page():
    return render_template('415.html', title="415 media type not supported"), 415


@app.route('/500', methods=['GET'])
def internal_server_error_page():
    return render_template('500.html', title="500 internal server error"), 500


@app.route('/503', methods=['GET'])
def service_unavailable_page():
    return render_template('503.html', title="503 service unavailable"), 503


@app.route('/504', methods=['GET'])
def gateway_timeout_page():
    return render_template('504.html', title="504 gateway timeout"), 504

if __name__ == '__main__':
    app.run(debug=True, port="8000")
