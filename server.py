from flask import Flask, request, render_template, jsonify
import model_cos

app = Flask(__name__)

#prepare the model
model = model_cos.GC_Model()
print('model is ready')

@app.route("/")
def homepage():
    all_sites = list(model.all_campground['name'])
    return render_template('index.html', all_sites = all_sites)

@app.route("/recommendations", methods=['POST'])
def recommendations():
    data = request.json
    print('##### start getting recommendations')
    rec = model.get_recommendations(data)
    print('##### done getting recommendations')
    return jsonify(rec)

if __name__ == '__main__':  # Script executed directly?
    app.run(host='0.0.0.0', port = 8080, debug=True)
    