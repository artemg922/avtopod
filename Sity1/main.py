from flask import Flask, render_template, request, redirect, g, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'shop.db'
ADMIN_CODE = '1234567890'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Item'")
        table_exists = cursor.fetchone()
        if not table_exists:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    db = get_db()
    items = query_db('SELECT * FROM Item WHERE isActive = 1')
    return render_template('index.html', items=items)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/autopod')
def autopod():
    return render_template('autopod.html')

@app.route('/diag')
def diag():
    return render_template('diag.html')

@app.route('/exp')
def exp():
    return render_template('exp.html')

@app.route('/new')
def new():
    return render_template('new.html')

@app.route('/bis')
def bis():
    return render_template('bis.html')

@app.route('/prover')
def prover():
    return render_template('prover.html')

@app.route('/inf')
def inf():
    return render_template('inf.html')

@app.route('/work')
def work():
    return render_template('work.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        admin_code = request.form['admin_code']

        if admin_code != ADMIN_CODE:
            flash('Неправильный код администратора', 'danger')
            return redirect('/create')

        db = get_db()
        try:
            db.execute('INSERT INTO Item (title, price, description, isActive) VALUES (?, ?, ?, ?)',
                       (title, price, description, True))
            db.commit()
            flash('Товар успешно добавлен', 'success')
            return redirect('/')
        except Exception as e:
            flash(f"Произошла ошибка: {e}", 'danger')
            return redirect('/create')
    else:
        return render_template('create.html')


@app.route('/delete', methods=['POST'])
def delete():
    item_id = request.form['item_id']
    admin_code = request.form['admin_code']

    if admin_code != ADMIN_CODE:
        flash('Неправильный код администратора', 'danger')
        return redirect('/')

    db = get_db()
    try:
        db.execute('DELETE FROM Item WHERE id = ?', (item_id,))
        db.commit()
        flash('Товар успешно удален', 'success')
    except Exception as e:
        flash(f"Произошла ошибка: {e}", 'danger')

    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)