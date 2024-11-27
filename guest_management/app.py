
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tamil_2005'
app.config['MYSQL_DB'] = 'guest_management'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/guest_details', methods=['GET', 'POST'])
def guest_details():
    # Get the search query from the request
    search_query = request.args.get('search', '').lower()  # Default to empty string if no search term

    # Fetch all guests from the database
    cur = mysql.connection.cursor()

    if search_query:
        # If there's a search query, filter the guests based on it (search by name, email, or phone)
        cur.execute("""
            SELECT * FROM guests
            WHERE LOWER(name) LIKE %s OR LOWER(email) LIKE %s OR phone LIKE %s
        """, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        # Otherwise, just fetch all guests
        cur.execute("SELECT * FROM guests")

    guests = cur.fetchall()

    return render_template('guest_details.html', guests=guests)


@app.route('/add_guest', methods=['GET', 'POST'])
def add_guest():
    # Handle the form for adding a new guest
    if request.method == 'POST':
        guest_id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        # Insert the new guest into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO guests (id, name, email, phone) VALUES (%s, %s, %s, %s)", 
                    (guest_id, name, email, phone))
        mysql.connection.commit()

        
        return redirect(url_for('guest_details'))  # Redirect to the guest list page

    return render_template('add_guest.html')  # Render the Add Guest form template



@app.route('/edit_guest/<int:id>', methods=['GET', 'POST'])
def edit_guest(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM guests WHERE id = %s", (id,))
    guest = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cur.execute("""
            UPDATE guests SET name = %s, email = %s, phone = %s WHERE id = %s
        """, (name, email, phone, id))
        mysql.connection.commit()
        return redirect(url_for('guest_details'))

    return render_template('edit_guest.html', guest=guest)


@app.route('/delete_guest/<int:id>', methods=['POST'])
def delete_guest(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM guests WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect(url_for('guest_details'))

@app.route('/search_guest', methods=['GET'])
def search_guest():
    query = request.args.get('query')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM guests WHERE name LIKE %s OR email LIKE %s", (f'%{query}%', f'%{query}%'))
    guests = cur.fetchall()
    return jsonify(guests)

if __name__ == '__main__':
    app.run(debug=True)
