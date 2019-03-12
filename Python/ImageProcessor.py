import requests
import json
import base64
from google.oauth2 import service_account
from google.cloud import vision
from datetime import datetime
import re
import json


class VisionAPI:
    __author__ = "Yrian Hovde Øksne"
    """
    Made for interacting with the Google Vision API
    """
    key = "3b6baaea984e1382d7528456c19633bbdd949e31"


    @staticmethod
    def get_text_detection_from_img(image_name):
        """
        gets a json object containing text detection analysis information from the google vision api
        :param img_name: name of the image you want to analyze, needs .fileType annotation, image has to be in the same
        folder as the executed file
        :return: json object with text detection analysis details
        """
        '''
        establishes connection with the api
        '''
        credentials = service_account.Credentials.from_service_account_file("key.json")
        client = vision.ImageAnnotatorClient(credentials=credentials)
        '''
        Finds the image and converts it to a base64 encoded string
        '''
        with open(image_name, "rb") as image:
            content = image.read()
        '''
        gets and prints response from the api
        '''

        '''
        response = client.annotate_image(
            {"image": {"content": content}, "features":
                [{'type': vision.enums.Feature.Type.TEXT_DETECTION}]})
        '''

        image = vision.types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        text_string = ""
        for text in texts:
            print('\n"{}"'.format(text.description) + "")
            text_string = text_string + text.description

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                         for vertex in text.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))

        return text_string





class TextProcessor:
    __author__ = "Yrian Hovde Øksne"

    def get_invoice_date(text_string):
        """
        gets invoice date from a text string made by the google vision api
        :param text_string: string of image processed data
        :return: invoice date
        """

        match = re.search(r'\d{2}.\d{2}.\d{4}', text_string)
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
        print(date)

    def get_invoice_number(text_string):
        """
        gets invoice number from a larger string
        :param test_string: string that contains an invoice number
        :return: invoice number
        """
    def get_total_amount_paid(text_string):
        """
        gets the total amount paid for within a string of a receipt processed by Google visions api
        :param text_string: processed string from the google vision api
        :return: total amount paid for in NOK
        """
        start = text_string.index("NOK\n") +3;
        end = text_string.index("GODKJENT\n")
        match = text_string[start: end:1]
        print(match)
        '''
        match2 = text_string.Substring(start, input.IndexOf("GODKJENT") - start);
        '''

img_text = VisionAPI.get_text_detection_from_img("kvit2.jpg")
print("Amount paid:")
amount_paid = TextProcessor.get_total_amount_paid(img_text)
print("Invoice date:")
invoice_date = TextProcessor.get_invoice_date(img_text)