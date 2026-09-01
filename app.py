from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

# Simple in-memory - perfect for Solo Boss
stock = {"5kg": 10, "9kg": 10, "14kg": 5, "19kg": 5, "48kg": 3}
orders = []
prices = {"5kg": 200, "9kg": 320, "14kg": 510, "19kg": 710, "48kg": 1750}

@app.route('/')
def dashboard():
    return render_template('index.html', stock=stock, orders=orders)

@app.route('/new_order')
def new_order():
    return render_template('new_order.html', stock=stock)

@app.route('/place_order', methods=['POST'])
def place_order():
    size = request.form.get('size','').split(' - ')[0].split(' ')[0] # handles "5kg - R200"
    if 'kg' not in size:
        size = request.form.get('size','5kg')
    customer = request.form.get('customer','')
    phone = request.form.get('phone','')
    address = request.form.get('address','')
    # reduce stock
    if stock.get(size,0) > 0:
        stock[size] -= 1
    orders.append({
        "customer": customer,
        "phone": phone,
        "address": address,
        "size": size,
        "price": prices.get(size,0)
    })
    return redirect('/')

@app.route('/add_stock', methods=['POST'])
def add_stock():
    size = request.form.get('size')
    qty = int(request.form.get('qty',0))
    if size in stock:
        stock[size] += qty
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
