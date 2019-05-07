# coding=utf-8
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os, datetime, json, re
from flask import Flask, render_template, flash, request, redirect, url_for, abort, Markup, make_response, send_file
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
from datetime import timedelta
from FikenManager import FikenManager


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

# Navbar
nav = Nav(app)
app.config['SECRET_KEY'] = 'secretkey'

navbar = Navbar('',
    View('Kjøp', 'purchase'),
    View('Salg', 'sale'),
    View('Historikk', 'loader', href='history'),
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
def purchase(image=None, pop=None):
    form = PurchaseForm()
    customer_modal_form = CustomerForm()
    ocr_line_data = None
    ocr_supplier = None
    print(pop)
    if pop:
        if 'invoice_number' in pop:
            form.invoice_number.data = pop['invoice_number']
        if 'invoice_date' in pop:
            form.invoice_date.data = pop['invoice_date']
        if 'maturity_date' in pop:
            form.maturity_date.data = pop['maturity_date']
        if 'vat_and_gross_amount' in pop:
            ocr_line_data = pop['vat_and_gross_amount']
        if 'organization_number' in pop:
            ocr_supplier = pop['organization_number']
    try:
        # Retrieve all contacts from fiken
        contacts = current_user.fiken_manager.get_data_from_fiken(data_type="contacts", links=True)
        # Get the suppliers in a presentable format
        suppliers = PurchaseDataFormatter.get_supplier_strings(contacts)

        # Retrieve all accounts from fiken
        accounts = current_user.fiken_manager.get_data_from_fiken(data_type="expense_accounts", links=True)
        # Get the accounts in a presentable format
        accounts = PurchaseDataFormatter.get_account_strings(accounts)

        # Retrieve all payment-accounts from fiken
        payment_accounts = current_user.fiken_manager.get_data_from_fiken(data_type="payment_accounts", links=True)
        # Get the accounts in a presentable format
        payment_accounts = SalesDataFormatter.get_account_strings(payment_accounts)

    # If we get a ValueError, it means that fiken-manager is not set properly to interact with fiken.
    # Thus, we have no data to retrieve from fiken, and the lists should be empty.
    except ValueError:
        suppliers = []
        accounts = []
        payment_accounts = []

    return render_template('purchase.html', title="Kjøp", form=form, customer_modal_form=customer_modal_form,
                           image=image, current_user=current_user, suppliers=suppliers, accounts=accounts,
                           contact_type="leverandør", payment_accounts=payment_accounts,
                           ocr_line_data=ocr_line_data, ocr_supplier=ocr_supplier)


@app.before_request
def before_request():
    """
    If a user is inactive for 30 minutes, log him/her out.
    """
    app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/register_purchase', methods=['GET', 'POST'])
@login_required
def register_purchase():
    validated, errors = validate_purchase_form(request.form)
    if validated:
        purchase_data = PurchaseDataFormatter.ready_data_for_purchase(request.form)
        print(purchase_data)
        post = current_user.fiken_manager.post_data_to_fiken(purchase_data, "purchases")

        if post.status_code == 201:
            # Get the purchase-info from fiken for later reference
            # The purchase in question is at index 0, since it is the most recent
            purchase = current_user.fiken_manager.get_raw_data_from_fiken("purchases")["_embedded"][
                "https://fiken.no/api/v1/rel/purchases"][0]
            # If it is a supplier-purchase, register any payments
            if request.form["purchase_type"] == '1':
                # The purchase in question is at 0 index, since it is the most recent
                payment_post_url = purchase["_links"]["https://fiken.no/api/v1/rel/payments"]["href"]
                payments = PurchaseDataFormatter.ready_payments(request.form)
                # Post the payments
                for payment in payments:
                    current_user.fiken_manager.make_fiken_post_request(payment_post_url, payment)

            # Post any attachments
            if 'filename' in request.form.keys():
                # Ready file for send-in to fiken
                filename = request.form["filename"]
                if filename is not 'None':
                    file_path = '{}/static/uploads/{}'.format(os.getcwd(), filename)
                    file = PurchaseDataFormatter.ready_attachment(file_path, filename)
                    # Retrieve the link for registering attachments to the purchase
                    attachment_post_url = purchase["_links"]["https://fiken.no/api/v1/rel/attachments"]["href"]
                    # Post the attachment
                    current_user.fiken_manager.make_fiken_post_request_files(attachment_post_url, file)
                    # Delete the file from server
                    os.remove(file_path)

            flash("Kjøp registrert.")
        # Interpret this as some kind of error with VAT.
        elif post.status_code == 400 and "vat" in post.text.lower():
            flash("VAT-type ikke kompatibel med utgiftskonto. Prøv på nytt.")
        else:
            flash("Noe gikk galt. Prøv igjen senere eller kontakt oss om problemet vedvarer.")
    else:
        flash(errors[0])

    return redirect(url_for('purchase'))


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
                               account_modal_form=account_modal_form, contact_type="kunde")


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
        entries = sales + purchases
        entries.sort(key=_get_entry_date)
        entries.reverse()
        return render_template('history.html', title="Historikk", entry_view=entries, current_user=current_user)
    else:
        data_type = request.form["type"]
        if data_type == "all":
            return redirect(url_for('history'))
        elif data_type == "purchases":
            entries = purchases
            entries.sort(key=_get_entry_date)
            entries.reverse()
            return render_template('history.html', title="Historikk", entry_view=entries, checked="purchases", current_user=current_user)
        elif data_type == "sales":
            entries = sales
            entries.sort(key=_get_entry_date)
            entries.reverse()
            return render_template('history.html', title="Historikk", entry_view=entries, checked="sales", current_user=current_user)


def _get_entry_date(entry):
    """
    Returns the date of a ledger-entry from fiken.
    Used for sorting entries by date.
    :param entry: The entry
    :return: The date of the entry
    """
    return entry[0]["date"]


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    form = ProfileForm()
    fiken_modal_form = FikenModalForm()
    confirm_password_form = ConfirmPasswordForm()
    user_data = get_user_data()

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
                           companies=companies, current_user=current_user, user_data = user_data)


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
                login_user(user, remember=False)
                # In case the company set has active has been deleted in fiken since last time (very unlikely)
                if not current_user.fiken_manager:
                    current_user.fiken_manager = FikenManager()
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
    abort(401)
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
            flash("Obs: Finner ingen bruker med den angitte eposten.")

        return redirect(url_for('log_in'))

    return render_template('forgot_password.html', title="Glemt Passord", form=form)


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html', title="Hjelp")


@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
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
        return purchase(image=filename, pop=pop)
    else:
        flash("Unsupported media")
        return purchase()


def get_image_data(filename):
    """
    Gets image data from image processor. Checks first if data can be fetched as a receipt,
    before checking if data can be fetched as an invoice.
    :param filename: The file to get the data from
    :return: Data form image processor.
    """
    img_text = vision_manager.get_text_detection_from_img(filename)
    text_processor = TextProcessor(img_text)
    types = text_processor.define_invoice_or_receipt()
    try:
        if types == "receipt":
            return text_processor.get_receipt_info()
        elif types == "invoice":
            return text_processor.get_invoice_info()
    except:
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


@app.route('/get_user_data', methods=['GET', 'POST'])
def get_user_data():
    filename = 'bruker_data.txt'
    f = open(filename,"w+")
    f.write("This is your email: " + current_user.email + "\n")
    f.write("This is your name: " + current_user.name + "\n")
    f.write("This is your admin status: {}".format(current_user.admin) + "\n")
    f.write("This is your account activity status: {}".format(current_user.active) + "\n")
    f.write("This is your fiken-account: {}".format(current_user.fiken_manager.get_fiken_login()) + "\n")
    f.write("This is your active company: {}".format(current_user.fiken_manager.get_company_slug()) + "\n")
    f.close()
    return send_file('bruker_data.txt', as_attachment=True)

    
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


@app.route('/create_contact/<contact_type>', methods=['POST'])
@login_required
def create_contact(contact_type):
    new_contact_info = request.form

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
    contact[contact_type] = True
    contact["language"] = new_contact_info["language"]
    contact["currency"] = new_contact_info["currency"]
    contact["customer"] = True

    if contact_type == "supplier":
        contact_type_no = "leverandør"
    else:
        contact_type_no = "kunde"

    # Send data to fiken to create new contact
    post = current_user.fiken_manager.post_data_to_fiken(contact, "contacts")
    if post.status_code is not 201:
        flash("Kunne ikke oprette {}. Prøv igjen senere eller kontakt oss om problemet vedvarer.".format(contact_type_no))
    else:
        flash("Ny {} opprettet.".format(contact_type_no))

    # Customers are created on sales-page
    if contact_type == "customer":
        return redirect(url_for('sale'))
    # Suppliers are created on purchase-page
    elif contact_type == "supplier":
        return redirect(url_for('purchase'))


@app.route('/loader/<href>')
def loader(href=None):
    return render_template('loader.html', href=href)


def temporary_loader():
    return render_template(url_for('loader'))


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
# unauthorized error page, ex: accessing admin site, admin
@app.errorhandler(401)
def page_forbidden(e):
    return render_template('401.html', title="401 forbidden page", logged_in=is_logged_in()), 401


# page not found, used when accessing nonsense, eg. /pasta
#@app.app_errorhandler(404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="404 not found", logged_in=is_logged_in()), 404


# method not allowed, ex: when accessing upload_files
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html', title="405 method not allowed", logged_in=is_logged_in()), 405


# 415 - unsupported media type, ex: user send a svg image.
# TODO - PORT IT AS A FLASH
@app.errorhandler(415)
def unsupported_media_type(e):
    return render_template('415.html', title="415 unsupported media type", logged_in=is_logged_in()), 415


# TODO - make sure that these display when respective service fails
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


if __name__ == '__main__':
    app.run(debug=False, port="8000")
