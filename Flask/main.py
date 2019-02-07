from flask import Flask, render_template
from flask_wtf import FlaskForm
from forms import ForgotForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

@app.route('/')
@app.route('/kjop')
def kjop():
    return render_template('kjop.html', title="Kjøp")

@app.route('/salg')
def salg():
    return render_template('salg.html', title="Salg")

@app.route('/historikk')
def historikk():
    return render_template('historikk.html', title="Historikk")

@app.route('/profil')
def profil():
    return render_template('profil.html', title="Profil")

@app.route('/logg_inn')
def logg_inn():
    return render_template('logg_inn.html', title="Logg inn")

@app.route('/glemt_passord', methods=['GET', 'POST'])
def glemt_passord():
    form = ForgotForm()

    if form.validate_on_submit():
        return "Form is validated"
    return render_template('glemt_passord.html', title="Glemt Passord", form=form)

if __name__ == '__main__':
    app.run(debug=True)