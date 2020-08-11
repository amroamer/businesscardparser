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


def processFile(image):
    nlp = en_core_web_sm.load()
    readImg = cv2.imread(image)
    txt = pytesseract.image_to_string(readImg)
    nlpParsing = nlp(txt)
    

    # with open('txtOuput.txt','w') as f:
    #     f.write(txt)
    #     f.close()
    
    # Extract Full Name
    for x in nlpParsing.ents:
        if x.label_ == 'PERSON' and len(x.text.strip()) > 6:
            fullName = x.text 
            break
        else:
            fullName = 'null'
        
    #regular expression to find emails
    emails = re.search(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+", txt)
    
    #regular expression to find phone numbers
    numbers = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', txt)
    
    # Extracting Country using pycountry from raw text without any tagging
    for country in pycountry.countries:
        if country.name in txt:
            city = country.name
            break
        else:
            city = 'null'

    # cleaning the raw text which is extracted by tesseract
    cleanedText = txt.split("\n") 
    
    

    # make a json object for Extracted Text
    output = {'recognized_elements':{}}
    output['raw_text'] = txt.replace("\n",",")
    if fullName != 'null':
        output['recognized_elements']['FULL_NAME'] = fullName
    else:
        output['recognized_elements']['FULL_NAME'] = None
    if emails:
        output['recognized_elements']['EMAIL'] = emails.group()
    else:
        output['recognized_elements']['EMAIL'] = None
    if numbers:
        output['recognized_elements']['MOBILE'] = numbers.group()
    else:
        output['recognized_elements']['MOBILE'] = None
    if city != 'null':
        output['recognized_elements']['COUNTRY'] = city
        output['recognized_elements']['ADDRESS'] = city
    else:
        for country in nlpParsing.ents:
            if country.label_ == 'GPE':
                output['recognized_elements']['COUNTRY'] = country.text
                output['recognized_elements']['ADDRESS'] = country.text
                break
            else:
                output['recognized_elements']['COUNTRY'] = None
    
    for element in cleanedText:
        if  element == output['recognized_elements']['COUNTRY']  or output['recognized_elements']['EMAIL'] and output['recognized_elements']['EMAIL'] in element or output['recognized_elements']['MOBILE'] and output['recognized_elements']['MOBILE'] in element  or output['recognized_elements']['FULL_NAME'] == element or  element == ' ' or element == '' or element is None:

            cleanedText.remove(element)
    
    remainingElementsString = ",".join(cleanedText)
    
    if output['recognized_elements']['MOBILE'] is not None and output['recognized_elements']['MOBILE'] in remainingElementsString:
        remainingElementsString.replace(output['recognized_elements']['MOBILE'],'')

    output['remaining_text'] = remainingElementsString
    latestOutput = nlp(remainingElementsString)
    print([(x.text,x.label_) for x in latestOutput.ents])
    # Extracting Org
    for org in latestOutput.ents:
        if org.label_ == 'ORG':
            output['recognized_elements']['ORG'] = org.text
            break

    ## Testing NLTK Entities Stuff
    # tokens = nltk.word_tokenize(remainingElementsString)
    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    # print(entities)
        
    # print([(sent.text) for sent in latestOutput.sents])

    return output