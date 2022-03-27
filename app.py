from flask import Flask, render_template, request, abort
from flask.helpers import make_response, url_for
from werkzeug.utils import redirect
import requests
from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import urljoin
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Restaurant

IRIS_BASE_URL = os.environ["IRIS_BASE_URL"]
IRIS_AUTH_KEY = os.environ["IRIS_AUTH_KEY"]

headers = {"x-api-key": IRIS_AUTH_KEY, "accept": "application/fhir+json"}

severity_mapping = {
    "low": 1,
    "med": 2,
    "high": 3
}

def get_user_allergies(user_id):
    allergies_r = requests.get(urljoin(IRIS_BASE_URL, "AllergyIntolerance"), headers=headers, params={"patient": user_id}).json()
    allergies_list = []
    if allergies_r["total"]:
        allergies_raw = allergies_r["entry"]
        allergies_list = list(map(lambda x: (x["resource"]["code"]["text"], x["resource"]["criticality"]), filter(lambda x: x["resource"]["type"] == "allergy" and "food" in x["resource"]["category"], allergies_raw)))
    return allergies_list


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        user_id = request.args.get("user_id") or request.cookies.get("user_id")
        if not user_id:
            return render_template("index.jinja2")
        resp = make_response(redirect(url_for("allergies")))
        resp.set_cookie("user_id", user_id)
        return resp

@app.route("/logout", methods=["GET"])
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("user_id")
    return resp

@app.route("/allergies", methods=["GET", "POST", "DELETE"])
def allergies():
    if request.method == "GET":
        if "user_id" not in request.cookies:
            return redirect(url_for("index"))
        user_id = request.cookies["user_id"]
        user_r = requests.get(urljoin(IRIS_BASE_URL, f"Patient/{user_id}"), headers=headers).json()
        user_name = f"{user_r['name'][0]['given'][0]} {user_r['name'][0]['family']}"

        return render_template("user.jinja2", user_name=user_name, allergies_list=get_user_allergies(user_id))

    if request.method == "POST":
        requests.post(urljoin(IRIS_BASE_URL, "AllergyIntolerance"), data=request.data, headers=headers)
        return redirect(url_for("allergies"))

    if request.method == "DELETE":
        requests.delete(urljoin(IRIS_BASE_URL, "AllergyIntolerance"), data=request.data, headers=headers)
        return redirect(url_for("allergies"))

@app.route("/menu/<int:id>", methods=["GET"])
def menu(id):
    if "user_id" not in request.cookies:
        return redirect(url_for("index"))
    user_id = request.cookies["user_id"]
    allergies = get_user_allergies(user_id)
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return abort(404)
    items = restaurant.items
    res = []
    for i in items:
        severity = 0
        for ingredient in i.ingredients:
            for allergy in allergies:
                if ingredient.lower() in allergy[0].lower():
                    severity = max(severity, severity_mapping[allergy[1]])
        res.append((i, severity))
    return render_template("menu.jinja2", menu=res, name=restaurant.name)

# @app.route('/restaurant/<restaurant>')
# def menu(restaurant):
#     test_items = [
#         Item("Shrimp Scampi", 24, "Shrimp sauteed in olive oil served with pasta", 2),
#         Item("Caesar Salad", 14, "Caesar diff", 0),
#         Item("Mushroom Soup", 16, "soup diff", 0),
#         Item("Pepperoni Pizza", 18, "The House Special", 1)
#     ]

#     return render_template('menu.html', menu=test_items)

if __name__ == '__main__':
    app.run()
