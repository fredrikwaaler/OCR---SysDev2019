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
        :return: invoice date
        """
        try:
            match = re.search(r'\d{2}.\d{2}.\d{4}', self._text_string)
            date = datetime.strptime(match.group(), '%d.%m.%Y').date()
            return date
        except ValueError:
            try:
                match = re.search(r'\d{2}/\d{2}/\d{4}', self._text_string)
                date = datetime.strptime(match.group(), '%d/%m/%Y').date()
                return date
            except ValueError:
                print("ValueError occured")

    def get_invoice_number(self):
        """
        gets invoice number from a larger string
        :return: invoice number
        """
    def get_total_amount_paid(self):
        """
        gets the total amount paid for within a string of a receipt processed by Googles vision api
        :return: total amount paid for in NOK, returns None if the total amount is not found.
        """
        try:
            start = self._text_string.index("NOK\n") +3;
            end = self._text_string.index("GODKJENT\n")
            match = self._text_string[start: end:1]
            return match
        except ValueError:
            print("ValueError occured")

    def get_supplier(self):
        """
        gets a suggestion of the name of the supplier from a a text string of a receipt processed by Googles vision api
        the text string needs to come from the VisionManager class to work properly
        :return: the name of the supplier, returns None if the supplier is not found
        """
        supplier = self._text_string.partition(' ')[0]
        if("AS" in supplier):
            supplier = supplier.split("AS")[0] + "AS"
        if("Salaskvitterins" or "Salgskvittering" in supplier):
            new_supplier = supplier.replace('Salaskvitterins', '')
            return new_supplier
        else:
            return supplier

    def get_inidvidual_supplies(self):
        """
        gets a suggestion of the individual supplies that where listed on the given receipt.
        :return: a dictionary of the individual supplies that where listed on the given receipt.
        """


    def get_individual_supplies_from_kiwi(self):
        """
        gets a suggestion of the individual supplies that were listed in the given receipt.
        Note: This only works for receipts from the Kiwi company
        :return: returns a list of the suggested individual supplies that were listen in the given receipt.
        """
        try:
            start = self._text_string.index( "OperNr:") + 11
            new_text_string = self._text_string[start: len(self._text_string)]
            end = None
            temp_supply_list = new_text_string.split("\n")
            for string in temp_supply_list:
                new_string = string.replace(",", ".")
                try:
                    if isinstance(float(new_string), float) and not (new_string == "15" or new_string == "25"):
                        end = temp_supply_list.index(string)
                        break
                except ValueError:
                    one = 1
            supply_list = temp_supply_list[:end]
            return supply_list
        except ValueError:
            print("ValueError occured")
            print(ValueError.with_traceback())


vision_manager = VisionManager("key.json")
img_text = vision_manager.get_text_detection_from_img("kvit.jpg")
print(img_text)
text_processor = TextProcessor(img_text)
print("Amount paid:")
print(text_processor.get_total_amount_paid())
print("Invoice date:")
print(text_processor.get_invoice_date())
print("Supplier:")
print(text_processor.get_supplier())
print("Individual supplies:")
for string in text_processor.get_individual_supplies_from_kiwi():
    print(string)