from google.oauth2 import service_account
from google.cloud import vision
from datetime import datetime
import re


class VisionManager:
    __author__ = "Yrian Hovde Øksne"
    def __init__(self, gvision_auth_key_path):
        """
        The class VisionManager serves to interact with Googles Vision API. The class needs a path for the google
        vision authentication key to be able to interact with the api. The key needs to be in a json file.
        Note: class is used in syst.dev. subject to satisfy the owner of @Sukkertoppen's requirements.
        :param gvision_auth_key_path: path of the google vision authentication key. This needs to be a json file.
        """
        '''
        establishes connection with the api
        '''
        self._credentials = service_account.Credentials.from_service_account_file(gvision_auth_key_path)
        self._client = vision.ImageAnnotatorClient(credentials=self._credentials)

    def get_text_detection_from_img(self, image_name):
        """
        gets a json object containing text detection analysis information from the google vision api
        :param img_name: name of the image you want to analyze, needs .fileType annotation, image has to be in the same
        folder as the executed file
        :return: plain text of the text within the image given as parameter
        """
        '''
        Finds the image and converts it to a base64 encoded string
        '''
        with open(image_name, "rb") as image:
            content = image.read()
        '''
        gets and prints response from the api
        '''
        image = vision.types.Image(content=content)
        response = self._client.text_detection(image=image)
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

    def __init__(self, text_string):
        '''
        The TextProcessor class serves as a parser of reciepts and invoices. The class need to be passed a text_string
        made by the ImageProcessor class to function properly.
        Note: class is used in syst.dev. subject to satisfy the owner of @Sukkertoppen's requirements.
        :param text_string: a text string of the receipt or invoice you want to get information from. Needs to come from
        the VisionManager class to work properly.
        '''
        self._text_string = text_string

    def get_invoice_date(self):
        """
        gets invoice date from a text string made by the google vision api
        :param text_string: string of image processed data
        :return: invoice date
        """

        match = re.search(r'\d{2}.\d{2}.\d{4}', self._text_string)
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
        return date

    def get_invoice_number(self):
        """
        gets invoice number from a larger string
        :param test_string: string that contains an invoice number
        :return: invoice number
        """
    def get_total_amount_paid(self):
        """
        gets the total amount paid for within a string of a receipt processed by Google visions api
        :param text_string: processed string from the google vision api
        :return: total amount paid for in NOK
        """
        start = self._text_string.index("NOK\n") +3;
        end = self._text_string.index("GODKJENT\n")
        match = self._text_string[start: end:1]
        return match
        '''
        match2 = text_string.Substring(start, input.IndexOf("GODKJENT") - start);
        '''

vision_manager = VisionManager("key.json")
img_text = vision_manager.get_text_detection_from_img("kvit2.jpg")
text_processor = TextProcessor(img_text)
print("Amount paid:")
print(text_processor.get_total_amount_paid())
print("Invoice date:")
print(text_processor.get_invoice_date())