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
from FormValidator import validate_new_name, validate_new_email, validate_new_password, validate_new_fiken_user, validate_sign_up, validate_sales_form, validate_purchase_form
from SalesDataFormatter import SalesDataFormatter
from PurchaseDataFormatter import PurchaseDataFormatter
from mailer import Mailer
from ImageProcessor import VisionManager, TextProcessor
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

# Initialize image processor
vision_manager = VisionManager('key.json')


@app.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase(image=None):
    form = PurchaseForm()
    customer_modal_form = CustomerForm()
    if request.method == "POST":
        validated, errors = validate_purchase_form(request.form)
        if validated:
            purchase_data = PurchaseDataFormatter.ready_data_for_purchase(request.form)
            post = current_user.fiken_manager.post_data_to_fiken(purchase_data, "purchase")
            if post.status_code == 201:
                flash("Kjøp registrert.")
            else:
                flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
        else:
            flash(errors[0])

        return redirect(url_for('purchase'))

    else:
        try:
            # Retrieve all contacts from fiken
            contacts = current_user.fiken_manager.get_data_from_fiken(data_type="contacts", links=True)
            # Get the suppliers in a presentable format
            suppliers = PurchaseDataFormatter.get_supplier_strings(contacts)

            # Retrieve all accounts from fiken
            accounts = current_user.fiken_manager.get_data_from_fiken(data_type="expense_accounts", links=True)
            # Get the accounts in a presentable format
            accounts = PurchaseDataFormatter.get_account_strings(accounts)

        # If we get a ValueError, it means that fiken-manager is not set properly to interact with fiken.
        # Thus, we have no data to retrieve from fiken, and the lists should be empty.
        except ValueError:
            suppliers = []
            accounts = []

        return render_template('purchase.html', title="Kjøp", form=form, customer_modal_form=customer_modal_form,
                               image=image, current_user=current_user, suppliers=suppliers, accounts=accounts)


@app.route('/purchase2', methods=['GET', 'POST'])
@login_required
def purchase2(image=None, pop=False):
    form = PurchaseForm()
    customer_modal_form = CustomerForm()
    print(pop)
    ocr_line_data = None
    try:
        if pop:
            if 'invoice_number' in pop:
                form.invoice_number.data = pop['invoice_number']
            if 'invoice_date' in pop:
                form.invoice_date.data = pop['invoice_date']
            if 'maturity_date' in pop:
                form.maturity_date.data = pop['maturity_date']
            if 'vat_and_gross_amount' in pop:
                ocr_line_data = pop['vat_and_gross_amount']
    except KeyError:
        print("KeyError")
    return render_template('purchase.html', title="Kjøp2", form=form, customer_modal_form=customer_modal_form,
                           image=image, ocr_line_data=ocr_line_data)


@app.route('/sale', methods=['GET', 'POST'])
@login_required
def sale():
    form = SaleForm()
    customer_modal_form = CustomerForm()
    account_modal_form = AccountForm()
    if request.method == 'POST':
        validated, errors = validate_sales_form(request.form)
        if validated:
            sales_data = SalesDataFormatter.ready_data_for_invoice(request.form)
            post = current_user.fiken_manager.post_data_to_fiken(sales_data, "create_invoice")
            if post.status_code == 201:
                flash("Salg registrert.")
            else:
                flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
        else:
            flash(errors[0])

        return redirect(url_for('sale'))

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
        return render_template('sale.html', title="Salg", form=form, products=products,
                               bank_accounts=bank_accounts, customers=customers, customer_modal_form=customer_modal_form,
                               account_modal_form=account_modal_form)


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
                # In case the company set has active has been deleted in fiken since last time (very unlikely)
                if current_user.fiken_manager.has_valid_login():
                    slugs = [info[2] for info in current_user.fiken_manager.get_company_info()]
                    if current_user.fiken_manager.get_company_slug() not in slugs:
                        current_user.fiken_manager.reset_slug()
                # Store the user
                current_user.store_user()
                next_page = request.args.get("next", url_for('purchase'))
                return redirect(next_page)
            else:
                flash("Brukernavnet eller passordet er feil. Prøv igjen.")
        else:
            flash("Brukernavnet eller passordet er feil. Prøv igjen.")
    return render_template('log_in.html', title="Logg inn", form=form)


@app.route('/log_out')
def log_out():
    logout_user()
    return redirect(url_for('log_in'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
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
                flash("Bruker registrert. Mail sendt til bruker med info.", "success")

                # Create new user and store to DB
                new_user = User(email, hashed_new, name, admin)
                new_user.store_user()
            except smtplib.SMTPException:
                flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
        else:
            for error in errors:
                flash(error)

        return redirect(url_for('admin'))

    return render_template('admin.html', title='Admin', form=form)


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
            # Get image data from image processor
            pop = get_image_data('static/uploads/'+filename)
            # Return purchase page with parsed data
            return purchase2(image=filename, pop=pop)
        else:
            flash("Unsupported media")
            return purchase2()
    return "EMPTY PAGE"


def get_image_data(filename):
    """
    Gets image data from image processor. Checks first if data can be fetched as a receipt,
    before checking if data can be fetched as an invoice.
    :param filename: The file to get the data from
    :return: Data form image processor.
    """
    img_text = vision_manager.get_text_detection_from_img(filename)
    text_processor = TextProcessor(img_text)
    try:
        return text_processor.get_receipt_info()
    except:
        print("This is not a receipt")
        try:
            return text_processor.get_invoice_info()
        except:
            print("This is not an invoice")
    flash("Vi kan dessverre ikke hente data fra det opplastede bildet.")
    return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/send_purchase_form', methods=['POST'])
@login_required
def send_purchase_form():
    result = request.form
    send_to_fiken(result, "Purchase")
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


@app.route('/create_customer', methods=['POST'])
@login_required
def create_customer():
    new_contact_info = request.form

    # if (validate_new_contact(new_contact_info)):
    # Create JSON-HAL for sending to fiken
    contact = {"name": new_contact_info["name"]}
    if not new_contact_info["org_nr"].strip() == '':
        contact["organizationIdentifier"] = new_contact_info["org_nr"]
    if not new_contact_info["email"].strip() == '':
        contact["email"] = new_contact_info["email"]
    if not new_contact_info["telephone"].strip() == '':
        contact["phone"] = new_contact_info["telephone"]
    if not new_contact_info["member_number"].strip() == '':
        contact["memberNumber"] = new_contact_info["member_number"]
    if not new_contact_info["country"].strip() == '':
        contact["address.country"] = new_contact_info["country"]
    if not new_contact_info["address1"].strip() == '':
        contact["address1"] = new_contact_info["address1"]
    if not new_contact_info["address2"].strip() == '':
        contact["address2"] = new_contact_info["address2"]
    if not new_contact_info["zip_code"].strip() == '':
        contact["postalCode"] = new_contact_info["zip_code"]
    if not new_contact_info["postal_area"].strip() == '':
        contact["postalPlace"] = new_contact_info["postal_area"]
    contact["language"] = new_contact_info["language"]
    contact["currency"] = new_contact_info["currency"]
    contact["customer"] = True

    # Send data to fiken to create new contact
    post = current_user.fiken_manager.post_data_to_fiken(contact, "contacts")
    if post.status_code is not 201:
        flash("Kunne ikke oprette kunde. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
    else:
        flash("Ny kunde opprettet.")

    return redirect(url_for('sale'))


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
