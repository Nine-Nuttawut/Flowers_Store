from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'flowers_store.db')

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    flowers = conn.execute('''
        SELECT f.*, c.name as category_name
        FROM Flowers f
        JOIN Categories c ON f.category_id = c.category_id
        WHERE f.is_available = 1
        ORDER BY f.name
    ''').fetchall()
    conn.close()
    return render_template('index.html', flowers=flowers)

@app.route('/categories')
def categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        conn = get_db_connection()
        conn.execute('INSERT INTO Categories (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        conn.close()
        flash('Category added successfully!')
        return redirect(url_for('categories'))
    return render_template('add_category.html')

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM Categories WHERE category_id = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        conn.execute('UPDATE Categories SET name = ?, description = ? WHERE category_id = ?', (name, description, id))
        conn.commit()
        conn.close()
        flash('Category updated successfully!')
        return redirect(url_for('categories'))
    conn.close()
    return render_template('edit_category.html', category=category)

@app.route('/delete_category/<int:id>')
def delete_category(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Categories WHERE category_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Category deleted successfully!')
    return redirect(url_for('categories'))

@app.route('/flowers')
def flowers():
    conn = get_db_connection()
    flowers = conn.execute('''
        SELECT f.*, c.name as category_name
        FROM Flowers f
        JOIN Categories c ON f.category_id = c.category_id
        ORDER BY f.name
    ''').fetchall()
    conn.close()
    return render_template('flowers.html', flowers=flowers)

@app.route('/add_flower', methods=['GET', 'POST'])
def add_flower():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']
        color = request.form['color']
        is_available = 1 if request.form.get('is_available') else 0
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        conn.execute('INSERT INTO Flowers (name, price, stock, category_id, color, is_available, image) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, float(price), int(stock), int(category_id), color, is_available, image))
        conn.commit()
        conn.close()
        flash('Flower added successfully!')
        return redirect(url_for('flowers'))
    conn.close()
    return render_template('add_flower.html', categories=categories)

@app.route('/edit_flower/<int:id>', methods=['GET', 'POST'])
def edit_flower(id):
    conn = get_db_connection()
    flower = conn.execute('SELECT * FROM Flowers WHERE flower_id = ?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM Categories ORDER BY name').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category_id']
        color = request.form['color']
        is_available = 1 if request.form.get('is_available') else 0
        
        # Handle image upload
        image = flower['image']  # default to current
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        conn.execute('UPDATE Flowers SET name = ?, price = ?, stock = ?, category_id = ?, color = ?, is_available = ?, image = ? WHERE flower_id = ?',
                     (name, float(price), int(stock), int(category_id), color, is_available, image, id))
        conn.commit()
        conn.close()
        flash('Flower updated successfully!')
        return redirect(url_for('flowers'))
    conn.close()
    return render_template('edit_flower.html', flower=flower, categories=categories)

@app.route('/delete_flower/<int:id>')
def delete_flower(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Flowers WHERE flower_id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Flower deleted successfully!')
    return redirect(url_for('flowers'))

if __name__ == '__main__':
    app.run(debug=True)