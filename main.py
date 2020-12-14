# -*- coding: utf-8 -*-
"""
lmaos
preprocessing
"""
# import libraries
from joblib import dump, load
import pandas as pd
import numpy as np

# Flask
from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route("/home")
@app.route("/")
def home():
    """Home Page"""
    return render_template("index.html")


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            brand = request.form['brand']
            subcategory = request.form['subcategory']
            product_cost = request.form['product_cost']
            listing_price = request.form['listing_price']
            bsp = request.form['base_selling_price']

            dict_client = {}
            dict_client["brand_name"] = brand
            dict_client["subcategory"] = subcategory
            dict_client["product_cost"] = product_cost
            dict_client["listing_price"] = listing_price
            dict_client["base_selling_price"] = bsp
            print(dict_client)
            df = pd.DataFrame.from_dict(dict_client, orient='index').T
            print(df)
            x = ['brand_name', 'subcategory', 'product_cost', 'listing_price', 'base_selling_price']
            x_feature = df[x]
            loaded_scaler = load('scaler.joblib')
            x_normalized = loaded_scaler(x_feature)
            print(df)

            print(x_normalized)
            # load model
            model = load('finalized_model.joblib')
            pred = model.predict(x_normalized)  # calculated value
            print(pred)


        except ValueError as e:
            print(e)
            return 'Please check the values!'

    return render_template('predict.html', prediction=pred)


@app.route("/no_page")
def no_page():
    """Redirect page"""
    return "<h1>The website you are looking for is not found.<h1>"


@app.route("/<name>")
def user(name):
    """This is for <name> or mispelled webpages"""
    return redirect(url_for("no_page"))


# Flask
if __name__ == "__main__":
    #app.run(host='0.0.0.0')
       app.run(debug=True)