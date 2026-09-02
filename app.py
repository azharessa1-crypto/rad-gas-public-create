from flask import Flask, render_template, request, redirect
import os
import requests
import urllib.parse

app = Flask(__name__, static_folder='.', static_url_path='')

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw6vQiq932xj6FgwsTiNK5YHu5ICI07n9X2VLutSIe5gy3bk0b3XFWcZg26-ZnsvOWUEA/exec"

# CHANGE THIS TO YOUR WHATSAPP NUMBER + API KEY
WHATSAPP_PHONE = "27746888347" # your number with 27 not 0
CALLMEBOT_APIKEY = "YOUR_API_KEY_HERE" # if you use CallMeBot, put key here

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

@app.route('/place_order', methods=['POST'])
def place_order():
    size = request.form.get('size')
    qty = int(request.form.get('qty',1))
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    price = prices.get(size, 0)
    total = price * qty

    if size in stock and stock[size] >= qty:
        stock[size] -= qty
        orders.append({
            "customer": name, "phone": phone, "address": address,
            "size": size, "qty": qty, "price": price, "total": total
        })

        # 1. SAVE TO GOOGLE SHEET
        try:
            requests.get(GOOGLE_SHEET_URL, params={
                "name": name, "phone": phone, "address": address,
                "size": size, "price": price, "qty": qty
            }, timeout=10)
        except Exception as e:
            print("Sheet error:", e)

        # 2. SEND WHATSAPP WITH PRICE - OLD WORKING FORMAT
        try:
            msg = f"NEW GAS ORDER\nName: {name}\nPhone: {phone}\nAddress: {address}\nSize: {size}\nQty: {qty}\nPrice: R{price}\nTotal: R{total}"
            # If you use CallMeBot
            if CALLMEBOT_APIKEY!= "YOUR_API_KEY_HERE":
                encoded = urllib.parse.quote(msg)
                requests.get(f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={encoded}&apikey={CALLMEBOT_APIKEY}", timeout=10)
        except Exception as e:
            print("WhatsApp error:", e)

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
