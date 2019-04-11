from FikenManager import FikenManager

money_values = ["amount", "netPrice", "vat"]
sale_type = {"INVOICE": "Faktura"}
purchase_type = {"SUPPLIER": "Kjøp fra leverandør", "CASH_PURCHASE": "Kontantkjøp"}


class HistoryDataFormatter:
    """
    The HistoryDataFormatter retrieves all necessary data to present purchase- and sale history from fiken and
    makes the data presentable for display.
    """
    def __init__(self, fiken_manager: FikenManager):
        """
        The HistoryDataFormatter takes a FikenManager which it uses to retrieve data from fiken.
        :param fiken_manager:
        """
        self.fiken_manager = fiken_manager

    def get_purchases_for_view(self):
        """
        Returns a list of edited purchase-data, ready for display.
        :return: Returns a list of edited purchase-data, ready for display.
        """
        purchases = self.fiken_manager.get_data_from_fiken(data_type="purchases")
        return_view = []
        externals = {}
        for purchase in purchases:
            # Open the supplier-link, if any, and add returned json to external.
            if "supplier" in purchase.keys():
                externals["contact"] = self.fiken_manager.make_fiken_get_request(purchase["supplier"])
                # For more easy handling, both sales and purchases are associated with a contact.
                purchase["contact"] = purchase["supplier"]
                purchase.pop("supplier")

            purchase["kind"] = purchase_type[purchase["kind"]]

            # Check whether or not the purchase has a pdf attached.
            # If so, create a pdf-key we can use to retrieve pdf-link
            if "https://fiken.no/api/v1/rel/attachments" in purchase.keys():
                url = purchase["https://fiken.no/api/v1/rel/attachments"][0]["downloadUrl"]
                if url.endswith('.pdf'):
                    purchase["pdf"] = url
                else:
                    purchase["img"] = url

            for product in purchase["lines"]:
                for key in product.keys():
                    if key in money_values:
                        product[key] = self.comma_adder(product[key])

                product['grossPrice'] = "{0:.2f}".format(float(product['vat']) + float(product['netPrice']))

            if purchase["paid"] == "False":
                purchase["paid"] = "Nei"
            else:
                purchase["paid"] = "Ja"

            purchase["type"] = "Kjøp"
            return_view.append((purchase, externals))
        return return_view

    def get_sales_for_view(self):
        """
        Returns a list of edited sale-dara, ready for display.
        :return: Returns a list of edited sale-data, ready for display.
        """
        sales = self.fiken_manager.get_data_from_fiken(data_type="sales")
        return_view = []
        externals = {}
        for sale in sales:
            # Open the customer-link, if any, and add returned json to external.
            if "customer" in sale.keys():
                externals["contact"] = self.fiken_manager.make_fiken_get_request(sale["customer"])
                # For more easy handling, both sales and purchases are associated with a contact.
                sale["contact"] = sale["customer"]
                sale.pop("customer")

            sale["kind"] = sale_type[sale["kind"]]

            for product in sale["lines"]:
                for key in product.keys():
                    if key in money_values:
                        product[key] = self.comma_adder(product[key])

                product['grossPrice'] = "{0:.2f}".format(float(product['vat']) + float(product['netPrice']))

            # Check whether or not the sale has a pdf attached.
            # If so, create a pdf-key we can use to retrieve pdf-link
            if "https://fiken.no/api/v1/rel/attachments" in sale.keys():
                url = sale["https://fiken.no/api/v1/rel/attachments"][0]["downloadUrl"]
                if url.endswith('.pdf'):
                    sale["pdf"] = url
                else:
                    sale["img"] = url

            if sale["paid"] == "False":
                sale["paid"] = "Nei"
            else:
                sale["paid"] = "Ja"

            sale["type"] = "Salg"

            return_view.append((sale, externals))
        return return_view

    @staticmethod
    def comma_adder(num):
        """
        Fiken returns all numbers without comma.
        This method will add that comma, to make the numbers get their actual value.
        For instance, provided "12300", the function will return "123.00".
        :param num: The number to manipulate.
        :return: The same number that was provided, only with a comma before the last to decimals.
        """
        num = list(str(num))
        if len(num) > 2:
            pre_comma = num[:len(num)-2]
            after_comma = num[-2:]
            return "".join(pre_comma) + "." + "".join(after_comma)
        elif len(num) == 2:
            return "0." + "".join(num)
        else:
            return "0.0" + "".join(num)
