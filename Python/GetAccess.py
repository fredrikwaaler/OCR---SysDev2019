import requests
import json
import base64
from google.oauth2 import service_account
from google.cloud import vision

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
        response = client.annotate_image(
            {"image": {"content": content}, "features":
                [{'type': vision.enums.Feature.Type.TEXT_DETECTION}]})

        image = vision.types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        for text in texts:
            print('\n"{}"'.format(text.description) + "")

            vertices = (['({},{})'.format(vertex.x, vertex.y)
                         for vertex in text.bounding_poly.vertices])

            print('bounds: {}'.format(','.join(vertices)))
        print('Texts:')
        print(response)