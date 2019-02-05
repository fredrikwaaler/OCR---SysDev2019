from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/kjop')
def kjop():
    return render_template('templates/kjop.html')

@app.route('/salg')
def salg():
    return render_template('templates/salg.html')

@app.route('/historikk')
def historikk():
    return render_template('templates/historikk.html')

@app.route('/profil')
def profil():
    return render_template('templates/profil.html')

@app.route('/logg_inn')
def logg_inn():
    return render_template('templates/logg_inn.html')

@app.route('/glemt_passord')
def glemt_passord():
    return render_template('templates/glemt_passord.html')