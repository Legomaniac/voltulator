#! python
import os
import datetime
from voltulator import Voltulator
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/example")
def returnExample():
    elecPrice = .107423
    gasPrice = 1.99
    calc = Voltulator(os.path.join("/tmp/", "exampleChargingHistory.csv"), elecPrice, gasPrice, None)
    output = calc.modifyCSV()
    return render_template('table.html', table=output['list'], totalCost=output['outCost'], \
                           gasCost=str(output['outGas']), percent=str(output['outPercent']))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['infile']
        centsPrkWhr = request.form['inelec']
        dollarsPrGal = request.form['ingas']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            now = datetime.datetime.now()
            monthNum = now.strftime("%m")

            elecPrice = float(centsPrkWhr)/100
            gasPrice = float(dollarsPrGal)

            calc = Voltulator(os.path.join(app.config['UPLOAD_FOLDER'], filename), elecPrice, gasPrice, None)
            output = calc.modifyCSV()

            return render_template('table.html', table=output['list'], totalCost=output['outCost'], \
                                   gasCost=str(output['outGas']), percent=str(output['outPercent']))

    return render_template('form.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
