from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "fast-nati-secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# =====================================
# IDENTIFIANTS ADMIN
# =====================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "fastnati123"

# =====================================
# TABLE ETUDIANT
# =====================================

class Etudiant(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    matricule = db.Column(db.String(50), unique=True)

    nom = db.Column(db.String(100))

    prenom = db.Column(db.String(100))

    email = db.Column(db.String(100))

    password = db.Column(db.String(300))

# =====================================
# TABLE FILIERE
# =====================================

class Filiere(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100))

# =====================================
# TABLE MATIERE
# =====================================

class Matiere(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100))

    credit = db.Column(db.Integer)

    filiere = db.Column(db.String(100))

# =====================================
# TABLE NOTE
# =====================================

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(50))

    matiere = db.Column(db.String(100))

    note = db.Column(db.Float)

    credit = db.Column(db.Integer)

# =====================================
# CREATION DATABASE
# =====================================

with app.app_context():

    db.create_all()

    if Filiere.query.count() == 0:

        filieres = [

            "MI",
            "PC",
            "Chimie"

        ]

        for f in filieres:

            nouvelle = Filiere(nom=f)

            db.session.add(nouvelle)

        db.session.commit()

    if Matiere.query.count() == 0:

        matieres = [

            ("Math", 6, "MI"),
            ("Physique", 3, "PC"),
            ("Anglais", 4, "MI"),
            ("SVT", 8, "PC"),
            ("Chimie Organique", 2, "Chimie")

        ]

        for m in matieres:

            nouvelle = Matiere(

                nom=m[0],
                credit=m[1],
                filiere=m[2]

            )

            db.session.add(nouvelle)

        db.session.commit()

    if Etudiant.query.count() == 0:

        etudiants = [

            ("11249STI24", "SODJINOU", "Emmanuel"),
            ("11249STI25", "KIKI", "Jean"),
            ("11249STI26", "AHOLOU", "Paul"),
            ("11249STI27", "DOSSOU", "Kevin"),
            ("11249STI28", "TOSSA", "David"),
            ("11249STI29", "YOVO", "Sarah"),
            ("11249STI30", "HOUNKPATI", "Grace"),
            ("11249STI31", "ZINSOU", "Brice"),
            ("11249STI32", "ATINDEHOU", "Carine"),
            ("11249STI33", "KPASSI", "Esther"),
            ("11249STI24","OROU","Pascale"),

        ]

        for e in etudiants:

            nouveau = Etudiant(

                matricule=e[0],
                nom=e[1],
                prenom=e[2],
                email=e[0] + "@fastnati.com",
                password=generate_password_hash("1234")

            )

            db.session.add(nouveau)

        db.session.commit()

# =====================================
# PAGE ACCUEIL
# =====================================
@app.route('/')
def index():

    return render_template('index.html')

# =====================================
# INSCRIPTION
# =====================================

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():

    if request.method == 'POST':

        matricule = request.form['matricule']

        nom = request.form['nom']

        prenom = request.form['prenom']

        email = request.form['email']

        password = request.form['password']

        password_hash = generate_password_hash(password)

        user = Etudiant(

            matricule=matricule,
            nom=nom,
            prenom=prenom,
            email=email,
            password=password_hash

        )

        db.session.add(user)

        db.session.commit()

        return redirect('/connexion')

    return render_template('inscription.html')

# =====================================
# CONNEXION ETUDIANT
# =====================================

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():

    if request.method == 'POST':

        matricule = request.form['matricule']

        password = request.form['password']

        user = Etudiant.query.filter_by(
            matricule=matricule
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session['matricule'] = matricule

            return redirect('/resultat')

    return render_template('connexion.html')

# =====================================
# CONNEXION ADMIN
# =====================================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    erreur = ""

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session['admin'] = True

            return redirect('/admin')

        else:

            erreur = "Identifiant ou mot de passe incorrect"

    return render_template(
        'admin_login.html',
        erreur=erreur
    )

# =====================================
# ADMIN
# =====================================

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if 'admin' not in session:

        return redirect('/admin-login')

    if request.method == 'POST':

        action = request.form['action']

        if action == "ajouter_filiere":

            nom = request.form['nom_filiere']

            nouvelle = Filiere(nom=nom)

            db.session.add(nouvelle)

            db.session.commit()

        elif action == "ajouter_matiere":

            nom = request.form['nom_matiere']

            credit = int(request.form['credit_matiere'])

            filiere = request.form['filiere']

            nouvelle = Matiere(

                nom=nom,
                credit=credit,
                filiere=filiere

            )

            db.session.add(nouvelle)

            db.session.commit()

        elif action == "ajouter_note":

            matricule = request.form['matricule']

            matiere = request.form['matiere']

            note = float(request.form['note'])

            credit = int(request.form['credit'])

            nouvelle = Note(

                matricule=matricule,
                matiere=matiere,
                note=note,
                credit=credit

            )

            db.session.add(nouvelle)

            db.session.commit()

    notes = Note.query.all()

    filieres = Filiere.query.all()

    matieres = Matiere.query.all()

    etudiants = Etudiant.query.all()

    resultats = []

    for e in etudiants:

        notes_etudiant = Note.query.filter_by(matricule=e.matricule).all()

        total = 0
        total_credit = 0

        for n in notes_etudiant:
            total += n.note * n.credit
            total_credit += n.credit

        moyenne = round(total / total_credit, 2) if total_credit > 0 else 0

        resultats.append({
            "matricule": e.matricule,
            "nom": e.nom,
            "prenom": e.prenom,
            "credit": total_credit,
            "moyenne": moyenne,
            "statut": "ADMIS" if moyenne >= 10 else "AJOURNÉ"
        })

    return render_template(

        'admin.html',

        notes=notes,

        filieres=filieres,

        matieres=matieres,
        etudiants=etudiants,
        resultats=resultats

    )

# =====================================
# RESULTATS
# =====================================

@app.route('/resultat')
def resultat():

    if 'matricule' not in session:

        return redirect('/connexion')

    matricule = session['matricule']

    notes = Note.query.filter_by(
        matricule=matricule
    ).all()

    total = 0

    total_credit = 0

    for n in notes:

        total += n.note * n.credit

        total_credit += n.credit

    moyenne = 0

    if total_credit > 0:

        moyenne = total / total_credit

    return render_template(

        'resultat.html',

        notes=notes,

        moyenne=round(moyenne, 2)

    )

# =====================================
# LOGOUT
# =====================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# =====================================
# SUPPRIMER MATIERE
# =====================================

@app.route('/supprimer-matiere/<int:id>')
def supprimer_matiere(id):

    if 'admin' not in session:

        return redirect('/admin-login')

    matiere = Matiere.query.get_or_404(id)

    db.session.delete(matiere)

    db.session.commit()

    return redirect('/admin')
# =====================================
# SUPPRIMER ETUDIANT
# =====================================

@app.route('/supprimer-etudiant/<int:id>')
def supprimer_etudiant(id):

    # VERIFICATION ADMIN
    if 'admin' not in session:

        return redirect('/admin-login')

    # RECHERCHE ETUDIANT
    etudiant = Etudiant.query.get_or_404(id)

    # SUPPRESSION DES NOTES
    notes = Note.query.filter_by(
        matricule=etudiant.matricule
    ).all()

    for n in notes:

        db.session.delete(n)

    # SUPPRESSION ETUDIANT
    db.session.delete(etudiant)

    # VALIDATION
    db.session.commit()

    return redirect('/admin')

if __name__ == '__main__':

    app.run(debug=True)