from flask import Flask, render_template, redirect
from markupsafe import escape
from flask_wtf import FlaskForm
from dotenv import load_dotenv
import requests
import os

API_BASE_URL = os.getenv("UPHOST_API_BASE_URL")

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route('/', methods=["GET", "POST"])
def home():
	form = FlaskForm()
	if form.validate_on_submit():
		return redirect('/destinations/dubai')

	return render_template('home.html', form=form)


@app.route('/destinations/<destination>')
def destination(destination):
	destination = escape(destination)
	destination = requests.get(f"{API_BASE_URL}/destinations").json()[0]
	key = str(int(destination["lastScraped"]))
	features = destination["features"][key]["0"]
	features["nListings"] = len(features["listingsByDescendingOccupancy"])
	features["maxPrice"] = "{:,}".format(list(features["maxPrice"].values())[0])
	features["minPrice"] = "{:,}".format(list(features["minPrice"].values())[0])
	features["avgPrice"] = "{:,}".format(int(features["avgPrice"]))
	top_listings = features["listingsByDescendingOccupancy"][:5]
	ids=','.join(top_listings)
	params={
		"ids":ids
	}
	top_listings = requests.get(f"{API_BASE_URL}/listings", params=params).json()
	reformatted_top_listings = []
	for listing  in top_listings:
		listing_dict = {
			"_id" : listing["_id"]
		}
		for feature, value in listing["features"][list(listing["features"].keys())[0]]["0"].items():
			listing_dict[feature] = value

		reformatted_top_listings.append(listing_dict)

	return render_template('destination.html', destination_str = "Dubai, UAE", features=features, top_listings=reformatted_top_listings)
