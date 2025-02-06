from flask import Flask, request, render_template, send_file
from zillow_pyzill import get_data, generate_df
 
# Flask constructor
app = Flask(__name__)   
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def download_csv():
    if request.method == "POST":
        location = request.form.get("location")
        radius = request.form.get("radius") 
        min_beds = request.form.get("minBeds")
        max_beds = request.form.get("maxBeds")
        min_baths = request.form.get("minBaths")
        max_baths = request.form.get("maxBaths")
        min_price = request.form.get("minPrice")
        max_price = request.form.get("maxPrice")
        try:
            map_results = get_data(
                location, 
                radius, 
                min_beds, 
                max_beds, 
                min_baths, 
                max_baths, 
                min_price,
                max_price
            )
        except Exception as e:
            return render_template(
                'form.html', 
                error=f'No results found.\n(Error: {e})'
            )
        if len(map_results) == 0:
            return render_template('form.html', error='No results found.')

        df = generate_df(map_results)
        df.to_csv("zillow_search_results.csv")
        render_template('form.html')
        return send_file(
            "/home/davinam717/zillow_search_results.csv", 
            as_attachment=True, 
            download_name="zillow_search_results.csv"
        )

    elif request.method=="GET":
        return render_template('form.html')

if __name__=='__main__':
   app.run()