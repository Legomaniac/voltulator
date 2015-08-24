import os
import datetime
from voltulator import Voltulator, PriceGrabber
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'D:\TestUpload'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['infile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            now = datetime.datetime.now()
            monthNum = now.strftime("%m")

            priceGrab = PriceGrabber('http://rates.northwesternenergy.com/residentialelectricrates.aspx')
            price = priceGrab.grab()

            calc = Voltulator(os.path.join(app.config['UPLOAD_FOLDER'], filename), price, monthNum)
            output = calc.modifyCSV()

            return render_template('table.html', table=output)

    return render_template('form.html')

if __name__ == '__main__':
    app.debug = True
    app.run()