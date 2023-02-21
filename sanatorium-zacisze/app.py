from flask import Flask, render_template, request, session, redirect, url_for
from flaskext.mysql import MySQL
import pymysql

app = Flask(__name__)
app.secret_key = 'pass123'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass123'
app.config['MYSQL_DATABASE_DB'] = 'sanatorium'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('home'))


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    # actual login part
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM klienci WHERE Pesel = %s AND Haslo = %s', (username, password))
        account = cursor.fetchone()

        # logic after user give us data
        if account:
            session['loggedin'] = True
            session['id'] = account['IDklient']
            session['username'] = account['Imie']

            return redirect(url_for('user_panel'))
        else:
            msg = 'Niepoprawne hasło lub login!'

    return render_template('user_login.html', msg=msg)


@app.route('/worker_login', methods=['GET', 'POST'])
def worker_login():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    # actual login part
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM pracownicy WHERE Pesel = %s AND Haslo = %s', (username, password))
        account = cursor.fetchone()

        # logic after user give us data
        if account:
            session['loggedin'] = True
            session['id'] = account['idpracownicy']
            session['username'] = account['Imie']

            return redirect(url_for('worker_panel'))
        else:
            msg = 'Niepoprawne hasło lub login!'

    return render_template('worker_login.html', msg=msg)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    # actual login part
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM pracownicy WHERE Pesel = %s AND Haslo = %s AND Czy_admin = 1',
                       (username, password))
        account = cursor.fetchone()

        # logic after user give us data
        if account:
            session['loggedin'] = True
            session['id'] = account['idpracownicy']
            session['username'] = account['Imie']

            return redirect(url_for('admin_panel'))
        else:
            msg = 'Niepoprawne hasło lub login!'

    return render_template('admin_login.html', msg=msg)


@app.route('/user_panel', methods=['GET', 'POST'])
def user_panel():
    # checking if user is logged 
    if 'loggedin' in session:
        return render_template('user_panel.html', username=session['username'])
    else:
        return redirect(url_for('user_login'))


@app.route('/worker_panel', methods=['GET', 'POST'])
def worker_panel():
    # checking if worker is logged 
    if 'loggedin' in session:
        return render_template('worker_panel.html', username=session['username'])
    else:
        return redirect(url_for('worker_login'))


@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    # checking if worker is logged 
    if 'loggedin' in session:
        return render_template('admin_panel.html', username=session['username'])
    else:
        return redirect(url_for('worker_login'))


# usuwanie
@app.route('/remove_employee', methods=['GET', 'POST'])
def remove_employee():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'pesel' in request.form:
        pesel = request.form['pesel']
        id = request.form['id']

        query = "SELECT * FROM pracownicy WHERE pesel = %s"
        values = (pesel,)
        cursor.execute(query, values)

        deleting = cursor.fetchone()

        if deleting:
            query = "DELETE FROM pracownicy WHERE pesel = %s"
            cursor.execute(query, values)
            db.commit()
            msg = 'Usunięto pracownika'
        else:
            msg = 'Nie znaleziono takiego pracownika'

    return render_template('removing_employee.html', msg=msg)


# dodawanie wizyt danego pacjenta
@app.route('/add_patient_treatment', methods=['GET', 'POST'])
def add_patient_treatment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'pesel' in request.form:
        pesel = request.form['pesel']

        query = "SELECT * FROM klienci WHERE pesel = %s"
        values = (pesel,)
        cursor.execute(query, values)

        klient = cursor.fetchone()
        if klient:
            id = request.form['id']
            termin = request.form['termin']
            rodzaj = request.form['rodzaj']
            id_prac = request.form['id_pracownika']
            id_pacj = request.form['id_pacjenta']

            query = "INSERT INTO terminarz_zabiegow (ID_wizyty, Termin, Rodzaj_zabiegu, ID_pracownika, ID_pacjenta) VALUES (%s, %s, %s, %s, %s)"
            values = (id, termin, rodzaj, id_prac, id_pacj)
            cursor.execute((query, values))
            db.commit()
            msg = 'Dodano zabieg'
        else:
            msg = 'Nie znaleziono takiego pacjenta'

    return render_template('add_patient_treatment.html', msg=msg)

# usuwanie wizyt danego pacjenta
@app.route('/delete_patient_treatment', methods=['GET', 'POST'])
def delete_patient_treatment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'pesel' in request.form:
        pesel = request.form['pesel']

        query = "SELECT * FROM klienci WHERE pesel = %s"
        values = (pesel,)
        cursor.execute(query, values)

        klient = cursor.fetchone()
        if klient:
            query = "SELECT * FROM terminarz_zabiegow WHERE ID_pacjenta = %s"
            values = (klient['IDklient'],)
            cursor.execute(query, values)

            zabiegi = cursor.fetchall()

            if zabiegi:
                query = "DELETE FROM terminarz_zabiegow WHERE ID_pacjenta = %s"

                values = (klient['IDklient'],)
                cursor.execute(query, values)

                db.commit()
                msg = 'Usunięto zabiegi dla tego pacjenta'
            else:
                msg = 'Brak zabiegów dla tego pacjenta'

        else:
            msg = 'Nie znaleziono takiego pacjenta'

    return render_template('delete_patient_treatment.html', msg=msg)


# wyświetlanie zabiegów danego lekarza
@app.route('/show_doctor_treatments', methods=['GET'])
def show_doctor_treatments():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ID_pracownika = request.args.get('ID_pracownika')

    # Retrieve the patient's treatment history
    query = """
        SELECT t.termin, t.ID_wizyty 
        FROM pracownicy p 
        JOIN terminarz_zabiegow t ON p.idpracownicy = t.ID_pracownika 
        WHERE p.idpracownicy = %s 
        ORDER BY t.termin DESC
    """
    values = (ID_pracownika,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    treatment_schedule = []
    for row in result:
        treatment_schedule.append({
            'termin': row['termin'],
            'id': row['ID_wizyty']
        })

    return render_template('showing_doc_treatments.html', employee_id=ID_pracownika, treatment_schedule=treatment_schedule)


# wyświetlanie wszystkich zabiegów danego pacjenta
from flask import Flask, render_template


@app.route('/treatment_history', methods=['GET'])
def treatment_history():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ID_pacjenta = request.args.get('ID_pacjenta')

    # Retrieve the patient's treatment history
    query = """
        SELECT t.termin, l.nazwa_zabiegu
        FROM terminarz_zabiegow t
        JOIN leczenie l ON t.rodzaj_zabiegu = l.ID_zabiegu
        WHERE t.ID_pacjenta = %s
        ORDER BY t.termin DESC
    """
    values = (ID_pacjenta,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    treatment_history = []
    for row in result:
        treatment_history.append({
            'termin': row['termin'],
            'zabieg': row['nazwa_zabiegu']
        })

    return render_template('treatment_history.html', patient_id=ID_pacjenta, treatment_history=treatment_history)


# wyświtlanie wszystkich chorób danego pacjenta
@app.route('/patient_illnesses', methods=['GET'])  # [NOT SURE]
def patient_illnesses():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ID_pacjenta = request.args.get('ID_pacjenta')

    query = """
        SELECT k.pesel, c.nazwa_choroby
        FROM klienci k
        JOIN terminarz_zabiegow t ON t.ID_pacjenta = k.idklient
        JOIN leczenie l ON t.rodzaj_zabiegu = l.ID_zabiegu
        JOIN choroby c ON l.choroba = c.ID_choroby
        WHERE t.ID_pacjenta = %s
        ORDER BY t.termin DESC
    """
    values = (ID_pacjenta,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    illnesses = []
    for row in result:
        illnesses.append({
            'pesel': row['pesel'],
            'choroba': row['nazwa_choroby']
        })

    return render_template('patient_illnesses.html', patient_id=ID_pacjenta, illnesses=illnesses)

# dodawanie stanowisk
@app.route('/add_position', methods=['POST', 'GET'])
def add_position():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'nazwa_stanowiska' in request.form:
        nazwa = request.form['nazwa_stanowiska']
        query = "SELECT * FROM stanowiska WHERE Nazwa_stanowiska=%s"
        cursor.execute(query, (nazwa,))
        existing_position = cursor.fetchone()
        if existing_position:
            msg = 'Stanowisko o podanej nazwie już istnieje w bazie danych'
        else:
            query = "SELECT ID_stanowiska FROM stanowiska ORDER BY ID_stanowiska DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                last_id = result['ID_stanowiska']
            else:
                last_id = 0
            id = last_id + 1
            stawka = request.form['stawka']
            if not stawka.isdigit():
                msg = 'Stawka musi byc liczba'
            else:
                rodzaj = request.form['rodzaj_zatrudnienia']
                query = "INSERT INTO stanowiska (ID_stanowiska, Nazwa_stanowiska, Stawka, Rodzaj_zatrudnienia) VALUES (%s, %s, %s, %s)"
                values = (id, nazwa, stawka, rodzaj)
                cursor.execute(query, values)
                db.commit()
                msg = 'Dodano stanowisko'

    return render_template('adding_position.html', msg=msg)


# usuwanie stanowisk
@app.route('/remove_position', methods=['GET', 'POST'])
def remove_position():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'nazwa_stanowiska' in request.form:
        nazwa_stanowiska = request.form['nazwa_stanowiska']

        # Check if the position is a foreign key in the zabiegi table
        query = "SELECT COUNT(*) AS count FROM zabiegi WHERE specjalista = %s"
        values = (nazwa_stanowiska,)
        cursor.execute(query, values)

        foreign_key_count = cursor.fetchone()['count']

        if foreign_key_count > 0:
            msg = 'Nie mozna usunac stanowiska, poniewaz jest one używane w tabeli zabiegi.'
        else:
            # Check if the position exists in the database
            query = "SELECT * FROM stanowiska WHERE nazwa_stanowiska = %s"
            values = (nazwa_stanowiska,)
            cursor.execute(query, values)

            deleting = cursor.fetchone()

            if deleting:
                # Delete the position from the database
                query = "DELETE FROM stanowiska WHERE nazwa_stanowiska = %s"
                cursor.execute(query, values)
                db.commit()
                msg = 'Usunieto stanowisko'
            else:
                msg = 'Nie znaleziono takiego stanowiska'

    return render_template('removing_position.html', msg=msg)


# wyswietlanie wszystkich stanowisk
@app.route('/show_positions', methods=['GET', 'POST'])
def show_positions():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    positions = []

    query = "SELECT * FROM stanowiska"
    cursor.execute(query)

    result = cursor.fetchall()

    for position in result:
        positions.append(position)

    return render_template('showing_positions.html', positions=positions)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''
    error_msg = ''

    # Get all possible job names from the 'stanowiska' table
    cursor.execute("SELECT Nazwa_stanowiska FROM stanowiska")
    job_names = [row['Nazwa_stanowiska'] for row in cursor.fetchall()]

    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        pesel = request.form['pesel']
        stanowisko = request.form['stanowisko']
        pensja = request.form['pensja']
        haslo = request.form['haslo']
        email = request.form['email']
        tel = request.form['tel']
        czy_admin = request.form['czy_admin']

        # Get the largest value of 'idpracownicy'
        cursor.execute("SELECT MAX(idpracownicy) FROM pracownicy")
        max_id = cursor.fetchone()['MAX(idpracownicy)']

        # Increment the largest value of 'idpracownicy' by one and assign it to 'idpracownicy'
        idpracownicy = max_id + 1

        # Check if 'pesel' already exists in the 'pracownicy' table
        cursor.execute("SELECT Pesel FROM pracownicy WHERE Pesel = %s", (pesel,))
        existing_pesel = cursor.fetchone()
        if existing_pesel:
            error_msg = "Pracownik z takim numerem PESEL już istnieje."

        # Validate that 'czy_admin' is either 1 or 0
        if czy_admin not in ['0', '1']:
            error_msg = "Wartość pola 'czy_admin' może być tylko 1 lub 0."

        if not error_msg:
            query = "INSERT INTO pracownicy (`idpracownicy`, `Pesel`, `Imie`, `Nazwisko`, `Haslo`, `Email`, `Numer_telefonu`, `Stanowisko`, `Czy_admin`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (idpracownicy, pesel, imie, nazwisko, haslo, email, tel, stanowisko, czy_admin)
            cursor.execute(query, values)
            db.commit()
            msg = 'Dodano pracownika'

    return render_template('adding_employee.html', job_names=job_names, msg=msg, error_msg=error_msg)


# wyswietlanie pracowników
@app.route('/show_employees', methods=['GET', 'POST'])
def show_employees():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    query = "SELECT * FROM pracownicy"
    cursor.execute(query)
    employees = cursor.fetchall()

    return render_template('view_employees.html', employees=employees)

# wyswietlanie konkretnego pracownika
@app.route('/show_employee', methods=['GET', 'POST'])
def show_employee():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'id' in request.form:

        id = request.form['id']
        query = "SELECT * FROM pracownicy WHERE idpracownicy = %s"
        values = (id,)
        cursor.execute(query, values)
        employee = cursor.fetchone()

        if employee:
            msg = f"Informacje o pracowniku o id {id}:"
            for key, value in employee.items():
                msg += f"\n{key.capitalize()}: {value}"
        else:
            msg = 'Nie znaleziono pracownika o podanym ID'

    return render_template('view_employee.html', msg=msg)


# dodawanie i usuwanie sprzętu medycznego
@app.route('/add_medical_equipment', methods=['POST', 'GET'])
def add_medical_equipment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'rodzaj' in request.form and 'pokoj' in request.form:
        rodzaj = request.form['rodzaj']
        pokoj = request.form['pokoj']

        marka = request.form['marka'] if 'marka' in request.form else None
        model = request.form['model'] if 'model' in request.form else None
        zastosowanie = request.form['zastosowanie'] if 'zastosowanie' in request.form else None
        termin_ostatniego_serwisu = request.form[
            'termin_ostatniego_serwisu'] if 'termin_ostatniego_serwisu' in request.form else None
        okres_serwisu = request.form['okres_serwisu'] if 'okres_serwisu' in request.form else None

        # Get the highest ID and increment it by 1
        query = "SELECT MAX(ID_sprzetu) AS max_id FROM sprzet_medyczny"
        cursor.execute(query)
        result = cursor.fetchone()
        next_id = 1 if result['max_id'] is None else int(result['max_id']) + 1

        # Get the available room numbers from the 'sale' table
        query = "SELECT Numer_sali FROM sale"
        cursor.execute(query)
        room_numbers = [row['Numer_sali'] for row in cursor.fetchall()]

        query = "INSERT INTO sprzet_medyczny (ID_sprzetu, Rodzaj_urzadzenia, Marka, Model, Zastosowanie, Pokoj, Termin_ostatniego_seriwsu, Okres_serwisu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (next_id, rodzaj, marka, model, zastosowanie, pokoj, termin_ostatniego_serwisu, okres_serwisu)
        cursor.execute(query, values)

        db.commit()
        msg = 'Dodano sprzęt medyczny'

    # Get the available room numbers from the 'sale' table to display in the dropdown list
    query = "SELECT Numer_sali FROM sale"
    cursor.execute(query)
    room_numbers = [row['Numer_sali'] for row in cursor.fetchall()]

    return render_template('adding_medical_equipment.html', msg=msg, room_numbers=room_numbers)


# usuwanie
@app.route('/delete_equipment', methods=['GET', 'POST'])
def delete_equipment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'id' in request.form:
        id = request.form['id']

        query = "SELECT * FROM sprzet_medyczny WHERE ID_sprzetu = %s"
        values = (id,)
        cursor.execute(query, values)

        deleting = cursor.fetchone()

        if deleting:
            query = "DELETE FROM sprzet_medyczny WHERE ID_sprzetu = %s"
            cursor.execute(query, values)
            db.commit()
            msg = 'Usunieto sprzęt medyczny'
        else:
            msg = 'Nie znaleziono takiego sprzętu'

    return render_template('removing_equipment.html', msg=msg)


# wyswietlanie sprzętu w kolejności najbardziej potrzebujących serwisu
import datetime


@app.route('/show_equipment', methods=['GET', 'POST'])
def show_equipment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    today = datetime.date.today()
    positions = []

    query = """
        SELECT ID_sprzetu, Pokoj, Termin_ostatniego_seriwsu, 
            DATE_ADD(Termin_ostatniego_seriwsu, INTERVAL okres_serwisu DAY) AS Termin_nastepnego_seriwsu
        FROM sprzet_medyczny
        ORDER BY ABS(DATEDIFF(Termin_nastepnego_seriwsu, %s)), ID_sprzetu
    """
    cursor.execute(query, (today,))

    sprzety = cursor.fetchall()

    msg = "<table><tr><th>ID sprzętu</th><th>Pokój</th><th>Ostatni serwis</th><th>Następny serwis</th></tr>"
    for sprzet in sprzety:
        msg += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            sprzet["ID_sprzetu"], sprzet["Pokoj"], sprzet["Termin_ostatniego_seriwsu"],
            sprzet["Termin_nastepnego_seriwsu"]
        )
    msg += "</table>"

    cursor.close()
    db.close()

    return render_template('showing_equipment.html', msg=msg)


# dodawanie  sal
@app.route('/add_treatment_room', methods=['POST', 'GET'])
def add_treatment_room():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'numer' in request.form:
        numer = request.form['numer']
        rodzaj = request.form['rodzaj'] if 'rodzaj' in request.form else None

        # Check if the treatment room already exists in the database
        query = "SELECT numer_sali FROM sale WHERE numer_sali = %s"
        cursor.execute(query, numer)
        result = cursor.fetchone()

        if result:
            msg = 'Sala o podanym numerze już istnieje.'
        else:
            # Insert the new treatment room into the database
            query = "INSERT INTO sale (numer_sali, rodzaj_zabiegu) VALUES (%s, %s)"
            values = (numer, rodzaj)
            cursor.execute(query, values)
            db.commit()
            msg = 'Dodano salę.'

    return render_template('adding_treatment_room.html', msg=msg)


# usuwanie sal zabiegowych
@app.route('/delete_treatment_room', methods=['GET', 'POST'])
def delete_treatment_room():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'numer' in request.form:
        numer = request.form['numer']

        query = "SELECT * FROM sale WHERE numer_sali = %s"
        values = (numer,)
        cursor.execute(query, values)

        deleting = cursor.fetchone()

        if deleting:
            query = "DELETE FROM sale WHERE numer_sali = %s"
            cursor.execute(query, values)
            db.commit()
            msg = 'Usunieto sale'
        else:
            msg = 'Nie znaleziono takiej sali'

    return render_template('deleting_treatment_room.html', msg=msg)


# wyswietlanie
@app.route('/show_treatment_rooms', methods=['GET', 'POST'])
def show_treatment_rooms():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    positions = []

    query = "SELECT * FROM sale"
    cursor.execute(query)

    sale = cursor.fetchall()

    result = ""
    for sala in sale:
        result += str(sala) + "\n"

    msg = result

    return render_template('showing_treatment_rooms.html', msg=msg)

# wyswietlanie 2
@app.route('/show_rooms_equipment', methods=['GET', 'POST'])
def show_rooms_equipment():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg=''

    query = "SELECT pokoj, rodzaj_urzadzenia FROM sprzet_medyczny"
    cursor.execute(query)

    sale = cursor.fetchall()

    result = ""
    for sala in sale:
        result += str(sala) + "\n"

    msg = result

    return render_template('showing_treatment_rooms.html', msg=msg)


# dodawanie chorob
@app.route('/add_illness', methods=['POST', 'GET'])
def add_illness():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'nazwa' in request.form:
        nazwa = request.form['nazwa']
        objawy = request.form['objawy'] if 'objawy' in request.form else None
        opis = request.form['opis'] if 'opis' in request.form else None

        # Retrieve the maximum value of 'id_choroby' from the database
        cursor.execute('SELECT MAX(id_choroby) AS max_id FROM choroby')
        result = cursor.fetchone()
        max_id = result['max_id']

        # Increment the maximum value by one to create a new 'id_choroby' value
        new_id = max_id + 1 if max_id is not None else 1

        # Insert the new illness into the database with the new 'id_choroby' value
        query = "INSERT INTO choroby (id_choroby, nazwa_choroby, objawy, opis) VALUES (%s, %s, %s, %s)"
        values = (new_id, nazwa, objawy, opis)
        cursor.execute(query, values)
        db.commit()

        msg = 'Dodano chorobe'

    # Close the database connection and return the response
    cursor.close()
    db.close()
    return render_template('adding_illness.html', msg=msg)


# usuwanie chorob
@app.route('/delete_illness', methods=['GET', 'POST'])
def delete_illness():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'id' in request.form:
        id = request.form['id']

        # Check if the illness is used in any treatments
        query = "SELECT * FROM leczenie WHERE Choroba = %s"
        values = (id,)
        cursor.execute(query, values)
        treatment = cursor.fetchone()

        if treatment:
            msg = 'Nie można usunąć choroby, ponieważ jest używana w leczeniu.'
        else:
            # Delete the illness from the table
            query = "SELECT * FROM choroby WHERE id_choroby = %s"
            values = (id,)
            cursor.execute(query, values)
            deleting = cursor.fetchone()

            if deleting:
                query = "DELETE FROM choroby WHERE id_choroby = %s"
                cursor.execute(query, values)
                db.commit()
                msg = 'Usunięto chorobę'
            else:
                msg = 'Nie znaleziono takiej choroby'

    return render_template('deleting_illness.html', msg=msg)


# wyswietlanie chorob
@app.route('/show_illnesses', methods=['GET'])
def show_illnesses():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    positions = []

    query = "SELECT * FROM choroby"
    cursor.execute(query)

    choroby = cursor.fetchall()

    result = ""
    for choroba in choroby:
        result += str(choroba) + "\n"

    msg = result

    return render_template('showing_illnesses.html', msg=msg)

# wyswietlanie opisow chorob
@app.route('/show_illness_desc', methods=['GET'])
def show_illness_desc():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ID_choroby = request.args.get('ID_choroby')

    # Retrieve the patient's treatment history
    query = "SELECT Nazwa_choroby, Opis FROM choroby WHERE ID_choroby = %s"
    values = (ID_choroby,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    illnesses = []
    for row in result:
        illnesses.append({
            'nazwa': row['Nazwa_choroby'],
            'opis': row['Opis']
        })

    return render_template('show_illness_desc.html', illness_id=ID_choroby, illnesses=illnesses)

# wyswietlanie opisow zabiegow
@app.route('/show_treatment_desc', methods=['GET'])
def show_treatment_desc():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ID_zabiegu = request.args.get('ID_zabiegu')

    # Retrieve the patient's treatment history
    query = "SELECT nazwa_zabiegu, Opis FROM leczenie WHERE ID_zabiegu = %s"
    values = (ID_zabiegu,)
    cursor.execute(query, values)
    result = cursor.fetchall()
    treatments = []
    for row in result:
        treatments.append({
            'nazwa': row['nazwa_zabiegu'],
            'opis': row['Opis']
        })

    return render_template('show_treatment_desc.html', treatment_id=ID_zabiegu, treatments=treatments)


# dodawanie leczenia
@app.route('/add_healing', methods=['GET', 'POST'])
def add_healing():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'nazwa' in request.form:
        # Get the maximum existing id_zabiegu value
        msg = 'test'
        cursor.execute('SELECT MAX(id_zabiegu) as max_id FROM leczenie')
        result = cursor.fetchone()
        max_id = result['max_id'] if result['max_id'] else 0

        # Automatically assign the next id_zabiegu value
        id = str(max_id + 1)
        nazwa = request.form['nazwa']

        # Check if choroba is a number
        choroba = request.form['choroba'] if 'choroba' in request.form and request.form['choroba'].isdigit() else None
        if choroba is None:
            msg = 'Choroba musi być wyrażona przez cyfrę'
        else:
            query = "INSERT INTO leczenie (ID_zabiegu, Nazwa_zabiegu, Choroba) VALUES (%s, %s, %s)"
            values = (id, nazwa, choroba)
            cursor.execute(query, values)
            db.commit()

            msg = 'Dodano leczenie'

    return render_template('adding_healing.html', msg=msg)


# usuwanie leczenia
@app.route('/delete_healing', methods=['GET', 'POST'])
def delete_healing():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST' and 'id' in request.form:
        id = request.form['id']

        # Check if the id_zabiegu value is present in the zabiegi table
        query = "SELECT * FROM zabiegi WHERE id_zabieg = %s"
        values = (id,)
        cursor.execute(query, values)
        zabieg = cursor.fetchone()

        if zabieg:
            # If the id_zabiegu value is present in the zabiegi table, prevent deletion
            msg = 'Nie można usunąć leczenia, ponieważ odpowiada mu zabieg w tabeli zabiegi'
        else:
            # If the id_zabiegu value is not present in the zabiegi table, proceed with deletion
            query = "SELECT * FROM leczenie WHERE id_zabiegu = %s"
            cursor.execute(query, values)
            deleting = cursor.fetchone()

            if deleting:
                query = "DELETE FROM leczenie WHERE id_zabiegu = %s"
                cursor.execute(query, values)
                db.commit()
                msg = 'Usunięto leczenie'
            else:
                msg = 'Nie znaleziono takiego leczenia'

    return render_template('deleting_healing.html', msg=msg)


# wyswietlanie leczenia
@app.route('/show_healing', methods=['GET'])
def show_healing():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    positions = []

    query = "SELECT * FROM leczenie"
    cursor.execute(query)

    leczenia = cursor.fetchall()

    result = ""
    for leczenie in leczenia:
        result += str(leczenie) + "\n"

    msg = result

    return render_template('showing_healings.html', msg=msg)


@app.route('/add_client', methods=['POST', 'GET'])
def add_client():
    db = mysql.connect()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    msg = ''
    pesel = request.form.get('pesel')
    imie = request.form.get('imie')
    nazwisko = request.form.get('nazwisko')
    data_urodzenia = request.form.get('data_urodzenia')
    id_turnusu = request.form.get('ID_turnusu')
    IDklient = request.form.get('IDklient')
    id_rezerwacji_parkingu = request.form.get('id_rezerwacji_parkingu')
    numer_pokoju = request.form.get('numer_pokoju')
    adres = request.form.get('adres')

    # Sprawdzanie, czy klient o podanym Peselu już istnieje w bazie
    query = "SELECT COUNT(*) FROM klienci WHERE Pesel = %s"
    cursor.execute(query, (pesel,))
    result = cursor.fetchone()
    if result['COUNT(*)'] > 0:
        msg = 'Błąd: Klient o podanym Peselu już istnieje w bazie'
        return render_template('adding_client.html', msg=msg)

    # Sprawdzanie, czy pokój o podanym numerze i turnusie już jest zajęty
    query = "SELECT COUNT(*) FROM klienci WHERE Numer_pokoju = %s AND ID_turnusu = %s"
    cursor.execute(query, (numer_pokoju, id_turnusu))
    result = cursor.fetchone()
    if result['COUNT(*)'] > 0:
        msg = 'Błąd: Pokój o podanym numerze i turnusie jest już zajęty'
        return render_template('adding_client.html', msg=msg)

    # Pobieranie dostępnych wartości ID_turnusu i Numer_pokoju
    query = "SELECT ID_turnusu FROM terminarz_noclegów"
    cursor.execute(query)
    available_id_turnusu = [row['ID_turnusu'] for row in cursor.fetchall()]

    query = "SELECT Numer_pokoju FROM pokoje"
    cursor.execute(query)
    available_numer_pokoju = [row['Numer_pokoju'] for row in cursor.fetchall()]

    if id_turnusu not in available_id_turnusu:
        id_turnusu = None
    if numer_pokoju not in available_numer_pokoju:
        numer_pokoju = None

    if pesel is None:
        msg = 'Błąd: brak wartości PESEL w formularzu'
        return render_template('adding_client.html', msg=msg)

    query = "INSERT INTO klienci (IDklient, Pesel, Imie, Nazwisko, Data_urodzenia, Adres, id_rezerwacji_parkingu, ID_turnusu, Numer_pokoju) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (IDklient, pesel, imie, nazwisko, data_urodzenia, adres, id_rezerwacji_parkingu, id_turnusu, numer_pokoju)
    cursor.execute(query, values)
    db.commit()

    msg = 'Dodano klienta'

    return render_template('adding_client.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
