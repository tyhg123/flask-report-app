from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# API lấy tỷ giá
def get_cny_to_vnd_rate(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    data = response.json()
    if data["result"] == "success":
        cny_rate = data["conversion_rates"].get("CNY")
        vnd_rate = data["conversion_rates"].get("VND")
        return vnd_rate / cny_rate
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        products = request.form.getlist("products[]")
        quantities = request.form.getlist("quantities[]")
        prices = request.form.getlist("prices[]")
        rate = request.form.get("rate")
        try:
            rate = float(rate) if rate else get_cny_to_vnd_rate("62bb25140e08315be6830be3")
            report = []
            total_vnd = 0
            for name, quantity, price in zip(products, quantities, prices):
                quantity = int(quantity)
                price = float(price)
                total_cny = quantity * price
                total_vnd_item = total_cny * rate
                total_vnd += total_vnd_item
                report.append(f"{name}: {quantity} x {price} = {total_cny:.2f} x {rate:.2f} = {total_vnd_item:,.2f} VND")
            report.append(f"=> Tổng: {total_vnd:,.2f} VND")
            return render_template("index.html", report="\n".join(report))
        except Exception as e:
            return render_template("index.html", error=f"Lỗi: {e}")
    return render_template("index.html")

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
