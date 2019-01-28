from flask import Flask, request, render_template, jsonify
import model_cos

app = Flask(__name__)

@app.route("/")
def homepage():
    all_sites = list(model_cos.campsite_list_rv['name'])
    return render_template('index.html', all_sites = all_sites)

@app.route("/recommendations")
def recommendations():
    name = request.args.get('name')
    rec = model_cos.get_recommendations(name)
    return jsonify(rec)

if __name__ == '__main__':  # Script executed directly?
    app.run(host='0.0.0.0', port = 8080, debug=True)
    