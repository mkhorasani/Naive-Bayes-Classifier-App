import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from sklearn.naive_bayes import GaussianNB

import sys
import re
import time

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('/index.html')


def process_file(path, filename):
    #remove_watermark(path, filename)
    association_mining(path, filename)
    # with open(path, 'a') as f:
    #    f.write("\nAdded processed content")




def association_mining(path, filename):

    #Importing dataset
    file = open(path,'r')
    text = file.readlines()

    for i in range(0,len(text)):
        text[i] = text[i].replace('\n','')
        text[i] = text[i].replace('"','')
        text[i] = text[i].replace('[','')
        text[i] = text[i].replace(']','')
        text[i] = text[i].replace("'",'')
        text[i] = text[i].split(',')


        for j in range(0,len(text[i])):
            try:
                text[i][j] = float(text[i][j])
                text[i][-1] = float(text[i][-1])

            except ValueError:
                text[i][j] = None

        text[i] = list(filter((None).__ne__, text[i]))


    disc = len(text[0])

    for i in range(0,len(text)):
        if len(text[i]) < disc:
            index = i
            break


    features = []

    for i in range(0,index):
        features.append(tuple(text[i][0:-1]))

    labels = []

    for i in range(0,index):
        labels.append((text[i][-1]))

    model = GaussianNB()

    model.fit(features,labels)

    for i in range(index,len(text)):
        text[i].append(float(model.predict([text[i]])))
    
    #Saving association mining results to text file
    with open(app.config['DOWNLOAD_FOLDER'] + (filename), 'w') as f:
        for item in text:
            f.write("%s\n" % item)


    

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], (filename), as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
    
#if __name__== '__main__':
#    app.run(debug=True)
