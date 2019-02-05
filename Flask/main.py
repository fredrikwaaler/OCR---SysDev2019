from flask import Flask, render_template
from forms import ForgotForm

app = Flask(__name__)

@app.route('/')
@app.route('/kjop')
def kjop():
    return render_template('kjop.html')

@app.route('/salg')
def salg():
    return render_template('salg.html')

@app.route('/historikk')
def historikk():
    return render_template('historikk.html')

@app.route('/profil')
def profil():
    return render_template('profil.html')

@app.route('/logg_inn')
def logg_inn():
    return render_template('logg_inn.html')

@app.route('/glemt_passord')
def glemt_passord():
    form = ForgotForm()
    return render_template('glemt_passord.html', form=form)