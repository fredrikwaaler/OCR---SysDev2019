import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from forms import LoginForm, ForgotForm, KjoopForm, SalgForm, ProfilForm
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
app.config["FIKEN_MANAGER"].set_company_slug("fiken-demo-glass-og-yoga-as2")




@app.route('/')
@app.route('/kjoop', methods=['GET'])
def kjoop(image=None):
    form = KjoopForm()
    return render_template('kjoop.html', title="Kjoop", form=form, image=image)


@app.route('/salg', methods=['GET'])
def salg():
    form = SalgForm()
    return render_template('salg.html', title="Salg", form=form)


@app.route('/historikk', methods=['GET', 'POST'])
def historikk():
    history_presenter = HistoryPresenter(app.config["FIKEN_MANAGER"])
    sales = history_presenter.get_sales_for_view()
    purchases = history_presenter.get_purchases_for_view()
    a = sales + purchases
    b = sales

    # If the method is get, we just retrieved the page with default value "all".
    if request.method == 'GET':
        return render_template('historikk.html', title="Historikk", entry_view=sales + purchases)
    else:
        data_type = request.form["type"]
        if data_type == "all":
            return redirect(url_for('historikk'))
        elif data_type == "purchases":
            return render_template('historikk.html', title="Historikk", entry_view=purchases, checked="purchases")
        elif data_type == "sales":
            return render_template('historikk.html', title="Historikk", entry_view=sales, checked="sales")


@app.route('/profil', methods=['GET'])
def profil():
    form = ProfilForm()
    return render_template('profil.html', title="Profil", form=form)


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

@app.route('/password', methods=['POST'])
def change_password():
    return "NONFUNCTIONAL > Change Password"


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


if __name__ == '__main__':
    app.run(debug=True)