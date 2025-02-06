from flask import Flask, render_template, request, Response, send_file
from zillow_pyzill import get_data, generate_df, fieldnames
import pandas as pd

app = Flask(__name__)

# Sample data for demonstration
map_results = []
df = pd.DataFrame(columns=fieldnames)
radius=0

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		global location 
		location = request.form.get("location")
		global radius 
		radius = request.form.get("radius")
	return render_template("app_index.html", csv_data=map_results, output_file="zillow_search_results.csv")

@app.route("/generate_csv")
def generate_csv():
	if len(map_results) == 0:
		return "No data to generate CSV."

	# Create a CSV string from the user data
	df = generate_df(map_results)

	return render_template("app_index.html", csv_data=df, output_file="zillow_search_results.csv")

@app.route("/download_csv")
def download_csv():
	map_results.extend(get_data(location, radius))	
	df = generate_df(map_results)
	if len(df) == 0:
		return "No data to download."

	# Create a CSV from the data
	df.to_csv("zillow_search_results.csv")

	return send_file("zillow_search_results.csv", as_attachment=True, download_name="zillow_search_results.csv")

@app.route("/download_csv_direct")
def download_csv_direct():
	df = generate_df(map_results)
	if len(df) == 0:
		return "No data to download."

	# Create a CSV from the data
	df.to_csv("zillow_search_results.csv")

	# Create a direct download response with the CSV data and appropriate headers
	response = Response(map_results, content_type="text/csv")
	response.headers["Content-Disposition"] = "attachment; filename=zillow_search_results.csv"

	return response

if __name__ == "__main__":
	app.run(debug=True)
