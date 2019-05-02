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
        self._credentials = service_account.Credentials.from_service_account_file(gvision_auth_key_path)
        self._client = vision.ImageAnnotatorClient(credentials=self._credentials)

    def get_text_detection_from_img(self, image_name):
        """
        gets a json object containing text detection analysis information from the google vision api
        :param image_name: name of the image you want to analyze, needs .fileType annotation, image has to be in the same
        folder as the executed file
        :return: plain text of the text within the image given as parameter
        """
        with open(image_name, "rb") as image:
            content = image.read()
        image = vision.types.Image(content=content)
        response = self._client.text_detection(image=image)
        texts = response.text_annotations
        text_string = ""
        for text in texts:
            #print('\n"{}"'.format(text.description) + "")
            text_string = text_string + text.description
            vertices = (['({},{})'.format(vertex.x, vertex.y)
                         for vertex in text.bounding_poly.vertices])
            #print('bounds: {}'.format(','.join(vertices)))

        return text_string


class TextProcessor:
    __author__ = "Yrian Hovde Øksne"

    def __init__(self, text_string):
        '''
        The TextProcessor class serves as a parser of receipts and invoices. The class need to be passed a text_string
        made by the ImageProcessor class to function properly.
        Note: class is used in syst.dev. subject to satisfy the owner of @Sukkertoppen's requirements.
        :param text_string: a text string of the receipt or invoice you want to get information from. Needs to come from
        the VisionManager class to work properly.
        '''
        self._text_string = text_string
        self._invoice_suppliers = ['proteinfabrikken', 'MARISOL KAKEDESIGN BARRETO', 'Best Emballasje AS']
        self._receipt_suppliers = ['KIWI HATLANE', "KITCH'N MOA", "Blomster Gården AS"]

    def get_receipt_info(self):
        """
        gets a suggestion for all the receipt information needed to register a purchase. Fields where the data is
        not found on the receipts, None will be returned.
        :return: a suggestion for all the receipt information needed to register a purchase. Fields where the data is
        not found on the receipts, None will be returned.
        """
        receipt_info = {"supplier": self.get_supplier_for_receipts(),
                        "invoice_date": self.get_invoice_date(),
                        "maturity_date": self.get_invoice_date(),
                        "vat_and_gross_amount": self.get_total_vat_and_amount(),
                        "organization_number": self.get_organization_number_for_receipt()
                        }

        return receipt_info

    def get_invoice_info(self):
        """
        gets a suggestion for all the invoice information needed to register a purchase. None will be returned if the
        fields were not found on the invoice.
        :return: a suggestion for all the invoice information needed to register a purchase.  None will be returned if
        the fields were not found on the invoice.
        """
        invoice_info = {"supplier": self.get_supplier_from_invoice(),
                        "organization_number": self.get_org_nr_from_invoice(),
                        "invoice_number": self.get_invoice_number(),
                        "invoice_date": self.get_invoice_date(),
                        "maturity_date": self.get_invoice_date()
                        }

        return invoice_info

    def define_invoice_or_receipt(self):
        """
        refines if the text string given is from a receipt or an invoice. Can get two different strings from this
        method. Either you get; <String>invoice<String> or <String>receipt<String>
        :return: two different strings from this method. Either you get; <String>invoice<String> or
        <String>receipt<String>
        """
        return_string = ""
        if "faktura" in self._text_string:
            return_string = "invoice"
        if "salgskvittering" in self._text_string:
            return_string = "receipt"
        if "faktura" or "salgskvittering" not in self._text_string:
            return_string = "receipt"
        else:
            return_string = "receipt"
        return return_string

    def get_org_nr_from_invoice(self):
        """
        Gets a suggestion for the organization number og the company delivering the invoice given as class parameter.
        Returns None if the field is not found.
        :return: a suggestion for the organization number og the company delivering the invoice given as class parameter.
        Returns None if the field is not found.
        """
        if "proteinfabrikken" in self._text_string:
            start = self._text_string.index("MVA-numme\n") + 10
            end = self._text_string.index("Kvittering\n") - 4
            match = self._text_string[start: end:1]
            return match
        if "org. nr" in self._text_string:
            start = self._text_string.index("org. nr") + 7
            match = self._text_string[start: start + 12:1]
            return match
        if "organisasjonsnummer" in self._text_string:
            start = self._text_string.index("organisasjonsnummer\n") + 19
            match = self._text_string[start: start + 12:1]
            return match
        if "Organisasjonsnr" in self._text_string:
            start = self._text_string.index("Organisasjonsnr\n") + 15
            match = self._text_string[start: start + 12:1]
            return match
        else:
            return None

    def get_invoice_date(self):
        """
        gets a suggestion og the invoice date from the text string given as class parameter. Returns None if there is
        no match.
        :return: a suggestion og the invoice date from the text string given as class parameter. Returns None if there is
        no match.
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
                try:
                    match = re.search(r'\d{2}.\d{2}.\d{2}', self._text_string)
                    date = datetime.strptime(match.group(), '%d.%m.%y').date()
                    return date
                except ValueError:
                    print("ValueError occurred")
                except AttributeError:
                    match = re.search(r'\d{2}.\d{2}.\d{2}', self._text_string)
                    date = datetime.strptime(match.group(), '%d.%m.%y').date()
                    return date
            except AttributeError:
                match = re.search(r'\d{2}.\d{2}.\d{2}', self._text_string)
                date = datetime.strptime(match.group(), '%d.%m.%y').date()
                return date
        except AttributeError:
            match = re.search(r'\d{2}.\d{2}.\d{2}', self._text_string)
            date = datetime.strptime(match.group(), '%d.%m.%y').date()
            return date

    def get_invoice_number(self):
        """
        gets a suggestion og the invoice number from the text string given as class parameter. Returns None if there is
        no match.
        :return: a suggestion og the invoice number from the text string given as class parameter. Returns None if there is
        no match.
        """
        if "proteinfabrikken" in self._text_string:
            start = self._text_string.index("Fakturanummer\n") + 14
            end = start + 14
            match = self._text_string[start: end:1]
            return match
        if "Best Emballasje AS" in self._text_string:
            start = self._text_string.index("EMBALLASJE\n")
            end = self._text_string.index("Faktura\n")
            match = self._text_string[start: end:1]
            list = match.split("\n")
            invoice_number = list[2]
            return invoice_number
        else:
            list = self._text_string.split("\n")
            index_of_invoice_number = list.index("Fakturanummer")
            if index_of_invoice_number is None:
                index_of_invoice_number = list.index("Faktura")
            try:
                list_plus_ten = list[index_of_invoice_number + 1: index_of_invoice_number + 10: 1]
                list_minus_ten = list[index_of_invoice_number - 10: index_of_invoice_number: 1]
            except IndexError:
                list_plus_ten = list[index_of_invoice_number: len(list), 1]
                list_minus_ten[list[0], index_of_invoice_number, 1]
            for x in list_plus_ten:
                try:
                    if isinstance(int(x), int):
                        invoice_number = int(x)
                        if invoice_number is None:
                            for y in list_minus_ten:
                                if isinstance(int(y), int):
                                    invoice_number = int(y)
                                    break
                        return invoice_number
                except ValueError:
                    pass

    def get_total_amount_paid(self):
        """
        gets a suggestion of what the total amount paid is on a receipt text given as class parameter. Returns None if
        nothing was found.
        :return: a suggestion of what the total amount paid is on a receipt text given as class parameter. Returns None if
        nothing was found.
        """
        try:
            start = self._text_string.index("NOK\n") + 4
            end = self._text_string.index("GODKJENT\n") - 1
            match = self._text_string[start: end:1]
            return match
        except ValueError:
            print("ValueError occurred")

    def get_supplier_for_receipts(self):
        """
        gets a suggestion of who the supplier of a receipt is from the text string given as class parameter. Returns
        None if there is no recognizable supplier.
        :return: a suggestion of who the supplier of a receipt is from the text string given as class parameter. Returns
        None if there is no recognizable supplier.
        """
        current_supplier = None
        for supplier in self._receipt_suppliers:
            if supplier in self._text_string:
                current_supplier = supplier
        if current_supplier is None:
            supplier = self._text_string.partition(' ')[0]
            if ("AS" in supplier):
                supplier = supplier.split("AS")[0] + "AS"
            if ("Salaskvitterins" or "Salgskvittering" in supplier):
                if "Salaskvitterins" in supplier:
                    supplier = supplier.replace('Salaskvitterins', '')
                if "Salgskvittering" in supplier:
                    supplier = supplier.replace('Salgskvittering', '')
                return supplier
            else:
                return supplier
        else:
            return current_supplier

    def get_individual_supplies(self):
        """
        gets a suggestion of the individual supplies that where listed on the given receipt. NOTE: Not sure if this
        is needed yet.
        :return: a dictionary of the individual supplies that where listed on the given receipt.
        """
        if self.get_supplier().lower() == "kiwi":
            return self.get_individual_supplies_from_kiwi()
        else:
            return_string = "Could not find supplies"
            return return_string

    def get_total_vat_and_amount(self):
        """
        Gets a suggestion of what the total amount paid is per vat percentage of receipts from the stores "Kiwi",
        "Kitch'n" and "Blomster Gården". Returns None if these fields are not found.
        :return: a suggestion of what the total amount paid is per vat percentage of receipts from the stores "Kiwi",
        "Kitch'n" and "Blomster Gården". Returns None if these fields are not found.
        """
        if "KIWI" in self.get_supplier_for_receipts():
            if "25%" not in self._text_string:
                paired_vat_and_amount = {"15": self.get_total_amount_paid()}
                return paired_vat_and_amount
            else:
                try:
                    start = self._text_string.index("Grunnlag\n") + 9
                    end = self._text_string.index("Mva\n") - 1
                    match = self._text_string[start: end:1]
                    vat = match.split('\n')
                    new_start = end - 3
                    new_string = self._text_string[new_start:len(self._text_string)]
                    new_string = new_string.split('\n')
                    amount1 = new_string[4]
                    amount2 = new_string[5]
                    paired_vat_and_amount = {vat[0]: amount1, vat[1]: amount2}
                    return paired_vat_and_amount
                except ValueError:
                    print("ValueError occurred")
        if "KITCH'N" in self._text_string:
            start = self._text_string.index("NOk\n") + 4
            end = self._text_string.index("GODKJENT\n") - 1
            match = self._text_string[start: end:1]
            amount1 = match
            paired_vat_and_amount = {"25": amount1}
            return paired_vat_and_amount
        if "BlomstesGarden" in self._text_string:
            vat_and_gross_amount = {"25": self.get_total_amount_paid()}
            return vat_and_gross_amount
        else:
            return None

    def get_individual_supplies_from_kiwi(self):
        """
        gets a suggestion of the individual supplies that were listed in the given receipt.
        Note: This only works for receipts from the Kiwi company, not sure if this method is needed yet.
        :return: returns a list of the suggested individual supplies that were listen in the given receipt.
        """
        try:
            start = self._text_string.index("OperNr:") + 11
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
                    pass
            supply_list = temp_supply_list[:end]
            return supply_list
        except ValueError:
            print("ValueError occurred")

    def get_organization_number_for_receipt(self):
        """
        gets a suggestion for the organization number of the supplier on the receipt given as text string in the class
        parameter. Returns None if the field is not found.
        :return: a suggestion for the organization number of the supplier on the receipt given as text string in the class
        parameter. Returns None if the field is not found.
        """
        if "kiwi" in self._text_string:
            try:
                start = self._text_string.index("ORG. NR.") + 9
                end = self._text_string.index("MVA")
                match = self._text_string[start: end:1]
                return match
            except ValueError:
                print("ValueError occurred")

        if "kiwi" not in self._text_string:
            try:
                match = re.search(r'\d{3} \d{3} \d{3}', self._text_string)
                org_nr = match.group(0)
                return org_nr
            except ValueError:
                print("ValueError occurred")
        else:
            return None

    def get_supplier_from_invoice(self):
        """
        gets a suggestion for the supplier on the invoice given as text string in the class parameter. Returns None if
        the field is not found.
        :return: a suggestion for the supplier on the invoice given as text string in the class parameter. Returns None if
        the field is not found.
        """
        current_supplier = None
        for supplier in self._invoice_suppliers:
            if supplier in self._text_string:
                current_supplier = supplier
        return current_supplier

    def add_invoice_supplier(self, invoice_supplier):
        """
        adds a supplier to the list of suppliers who'm specifically uses invoices
        :param invoice_supplier: the supplier you wish to add to the list of suppliers who'm specifically uses invoices
        """
        self._invoice_suppliers.append(invoice_supplier)

    def add_receipt_supplier(self, receipt_supplier):
        """
        adds a supplier to the list of suppliers who'm specifically uses receipts
        :param receipt_supplier: the supplier you wish to add to the list of suppliers who'm specifically uses receipts
        """
        self._receipt_suppliers.append(receipt_supplier)

    def get_maturity_date_from_invoice(self):
        """
        gets a suggestion for the maturity date of the invoice given as a text string in the class parameter. Returns
        None if the field is not found.
        :return: a suggestion for the maturity date of the invoice given as a text string in the class parameter. Returns
        None if the field is not found.
        """
        start = self._text_string.index("Forfall") + 7
        end = len(self._text_string)
        new_string = self._text_string[start: end:1]
        try:
            match = re.search(r'\d{2}.\d{2}.\d{4}', new_string)
            date = datetime.strptime(match.group(), '%d.%m.%Y').date()
            return date
        except ValueError:
            try:
                match = re.search(r'\d{2}.\d{2}.\d{2}', new_string)
                date = datetime.strptime(match.group(), '%d.%m.%y').date()
                return date
            except ValueError:
                print("ValueError occurred...")


#Presentation
vision_manager = VisionManager("key.json")
img_text = vision_manager.get_text_detection_from_img("fakt1.jpg")
text_processor = TextProcessor(img_text)
invoice_info = text_processor.get_invoice_info()
#print(img_text)
