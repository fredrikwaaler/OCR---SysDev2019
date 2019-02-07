from flask import Flask, render_template
from flask_wtf import FlaskForm
from forms import LoginForm, ForgotForm, KjopForm, SalgForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

@app.route('/')
@app.route('/kjøp', methods=['GET', 'POST'])
def kjop():
    form = KjopForm()

    if form.validate_on_submit():
        return "Kjøp-form validated"

    return render_template('kjøp.html', title="Kjøp", form=form)

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

if __name__ == '__main__':
    app.run(debug=True)