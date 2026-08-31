from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import urllib.parse

app = Flask(__name__)
SIZES = ['5kg','9kg','14kg','19kg','48kg']
KG_MAP = {'5kg':5, '9kg':9, '14kg':14, '19kg':19, '48kg':48}
PRICE_MAP = {'5kg':200, '9kg':320, '14kg':510, '19kg':710, '48kg':1750}
COST_MAP = {'5kg':150, '9kg':250, '14kg':400, '19kg':580, '48kg':1450}

def get_db():
    conn = sqlite3.connect('lpg.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY, size TEXT UNIQUE, qty INTEGER, kg_total INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer_name TEXT, customer_phone TEXT, address TEXT, size TEXT, qty INTEGER, price INTEGER, driver TEXT, created_at TEXT)')
    for s in SIZES:
        conn.execute('INSERT OR IGNORE INTO stock (size, qty, kg_total) VALUES (?,?,?)', (s, 0, 0))
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def index():
    conn = get_db()
    stocks = conn.execute('SELECT * FROM stock').fetchall()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC LIMIT 20').fetchall()
    conn.close()
    stock_list = []
    for st in stocks:
        stock_list.append({'size': st['size'], 'qty': st['qty'], 'price': PRICE_MAP.get(st['size'], 0)})
    return render_template('index.html', stocks=stock_list, orders=orders, price_map=PRICE_MAP)

@app.route('/add_stock', methods=['GET','POST'])
def add_stock():
    if request.method == 'POST':
        size = request.form.get('size')
        qty = int(request.form.get('qty', 0))
        conn = get_db()
        cur = conn.execute('SELECT qty FROM stock WHERE size=?', (size,))
        row = cur.fetchone()
        new_qty = (row['qty'] if row else 0) + qty
        conn.execute('UPDATE stock SET qty=?, kg_total=? WHERE size=?', (new_qty, new_qty * KG_MAP[size], size))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_stock.html', sizes=SIZES)

@app.route('/new_order', methods=['GET','POST'])
def new_order():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_phone = request.form.get('customer_phone')
        address = request.form.get('address')
        size = request.form.get('size')
        qty = int(request.form.get('qty', 1))
        driver = request.form.get('driver', 'Ziyaad')
        price_per = PRICE_MAP.get(size, 0)
        total_price = price_per * qty
        conn = get_db()
        conn.execute('INSERT INTO orders (customer_name, customer_phone, address, size, qty, price, driver, created_at) VALUES (?,?,?,?,?,?,?,?)', (customer_name, customer_phone, address, size, qty, total_price, driver, datetime.now().strftime('%Y-%m-%d %H:%M')))
        conn.execute('UPDATE stock SET qty = qty -?, kg_total = kg_total -? WHERE size=?', (qty, qty * KG_MAP[size], size))
        conn.commit()
        conn.close()
        message = "NEW LPG ORDER\n\nCustomer: " + customer_name + "\nPhone: " + customer_phone + "\nAddress: " + address + "\nOrder: " + size + " x " + str(qty) + "\nTotal: R" + str(total_price) + "\nDriver: " + driver + "\nDate: " + datetime.now().strftime('%d/%m %H:%M') + "\n\nPlease deliver ASAP!"
        encoded = urllib.parse.quote(message)
        whatsapp_url = "https://wa.me/?text=" + encoded
        return redirect(whatsapp_url)
    return render_template('new_order.html', sizes=SIZES, price_map=PRICE_MAP)

@app.route('/daily_report')
def daily_report():
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    orders = conn.execute('SELECT * FROM orders WHERE created_at LIKE?', (today+'%',)).fetchall()
    total_sales = sum([o['price'] for o in orders]) if orders else 0
    total_profit = 0
    for o in orders:
        cost = COST_MAP.get(o['size'], 0) * o['qty']
        total_profit += o['price'] - cost
    conn.close()
    return render_template('daily_report.html', orders=orders, total_sales=total_sales, total_profit=total_profit, date=today)

if __name__ == '__main__':
    app.run(debug=True, port=5000)