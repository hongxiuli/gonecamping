from flask import Flask, request, render_template, jsonify
import model_cos

app = Flask(__name__)

@app.route("/")
def homepage():
    all_sites = list(model_cos.pv_campground_rv['name'])
    print(all_sites)
    return render_template('index.html', all_sites = all_sites)

@app.route("/recommendations", methods=['POST'])
def recommendations():
    data = request.json
    print(data)
    rec = model_cos.get_recommendations(data)
    return jsonify(rec)

if __name__ == '__main__':  # Script executed directly?
    app.run(host='0.0.0.0', port = 8080, debug=True)
    