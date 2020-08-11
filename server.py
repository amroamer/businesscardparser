from flask import Flask , request,url_for,after_this_request,Response
import os
from PIL import Image
import base64
import cv2 
import pytesseract
import asyncio
import json
import re
import pycountry
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
import businessCardParser


# Commented by Yousef Abudakar

app = Flask(__name__)

## route to recieve images as a file
@app.route('/ocr/imgtotext',methods=['POST'])
def recieveImage():
    img = request.files['img']
    img.save('1994.jpg')
    output = businessCardParser.processFile('1994.jpg')
    # response = {'text':'Your Image has been submitted please use this REF No. to check the result : 1994'}
    return Response(json.dumps(output,sort_keys=True,indent=4),mimetype='application/json')

## a route to recieve Image base64 Code 
@app.route('/ocr/img64totext', methods=['POST'])
def recieveBase64():

    # get the base64 from the request args
    code = request.form['base64'].split(",")[1]
    # decode base64 image code to image file
    img = base64.b64decode(code)
    # image name to store in the server to be processed later
    filename = "1995.jpg"
    # writing the decoded base64 image code to image file . 
    with open(filename, 'wb') as f:
        f.write(img)
        f.close()

    output = businessCardParser.processFile('1995.jpg')

    #response json
    # response = {'text':'Your Image has been submitted please use this REF No. to check the result : 1995'}
    return Response(json.dumps(output,sort_keys=True,indent=4),mimetype='application/json')

## process the image and return the result for the user
# @app.route('/result/<id>')
# def ocrResult(id):

#    with open('%s.txt'%id,'r') as result:
#        txt = result.read()
#        result.close()
#        return txt
    

if __name__ == '__main__':
    app.run()