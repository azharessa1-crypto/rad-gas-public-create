from flask import Flask, render_template, request, redirect
import os
import requests

app = Flask(__name__, static_folder='.', static_url_path='')

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw6vQiq932xj6FgwsTiNK5YHu5ICI07n9X2VLutSIe5gy3bk0b3XFWcZg26-ZnsvOWUEA/exec"

stock = {"5kg": 10, "9kg": 10, "14kg": 5, "19kg": 5, "48kg": 3}
orders = []
prices = {"5kg": 200, "9kg": 320, "14kg": 510, "19kg": 710, "48kg": 1750}

@app.route('/')
def dashboard():
    return render_template('index.html', stock=stock, orders=orders)

@app.route('/order')
def order_page():
    return render_template('new_order.html', stock=stock, prices=prices)

@app.route('/new_order')
def new_order_page():
    return render_template('new_order.html', stock=stock, prices=prices)

@app.route('/dashboard')
def dashboard2():
    return render_template('index.html', stock=stock, orders=orders)

@app.route('/place_order', methods=['POST'])
def place_order():
    size = request.form.get('size')
    qty = int(request.form.get('qty',0))
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    if size in stock and stock[size] >= qty:
        stock[size] -= qty
        orders.append({
            "customer": name,
            "phone": phone,
            "address": address,
            "size": size,
            "qty": qty,
            "price": prices.get(size,0)
        })
        # SEND TO GOOGLE SHEET
        try:
            requests.get(GOOGLE_SHEET_URL, params={
                "name": name,
                "phone": phone,
                "address": address,
                "size": size,
                "price": prices.get(size,0),
                "qty": qty
            }, timeout=10)
        except Exception as e:
            print("Sheet error:", e)

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
