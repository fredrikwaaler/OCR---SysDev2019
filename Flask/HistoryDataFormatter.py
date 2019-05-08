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
        purchases = self.fiken_manager.get_raw_data_from_fiken("purchases")["_embedded"]["https://fiken.no/api/v1/rel/purchases"]
        return_view = []
        externals = {}
        for purchase in purchases:
            # Open the supplier-link, if any, and add returned json to external.
            if "supplier" in purchase.keys():
                externals["contact"] = self.fiken_manager.make_fiken_get_request(purchase["supplier"])
                # For more easy handling, both sales and purchases are associated with a contact.
                purchase["contact"] = purchase["supplier"]
                purchase.pop("supplier")

            # Retrieve the purchase-type based on 'kind' returned from fiken
            purchase["kind"] = purchase_type[purchase["kind"]]

            # Check whether or not the purchase has a attachment attached.
            # If so, create a key we can use to retrieve it.
            # The key is 'pdf' for pdfs, 'image' for iother images.
            if "_embedded" in purchase.keys():
                if "https://fiken.no/api/v1/rel/attachments" in purchase["_embedded"].keys():
                    url = purchase["_embedded"]["https://fiken.no/api/v1/rel/attachments"][0]["downloadUrl"]
                    if url.endswith('.pdf'):
                        purchase["pdf"] = url
                    else:
                        purchase["img"] = url

            # Edit the product-data
            for product in purchase["lines"]:
                for key in product.keys():
                    # Add comma to all values where it is appropriate (fiken returns numbers without comma)
                    # Money-values should have comma
                    if key in money_values:
                        product[key] = self.comma_adder(product[key])

                # Calculate gross and make presentable
                product['grossPrice'] = "{0:.2f}".format(float(product['vat']) + float(product['netPrice']))

            # Is the purchase paid or not
            if purchase["paid"] == "False":
                purchase["paid"] = "Nei"
            else:
                purchase["paid"] = "Ja"

            # Type for display
            purchase["type"] = "Kjøp"
            return_view.append((purchase, externals))

        return return_view

    def get_sales_for_view(self):
        """
        Returns a list of edited sale-data, ready for display.
        :return: A list of tuples (sale, external).
        Where the sale part is information about the sale itself, while external is
        data about any associated data (for instance data about the contact associated with the sale).
        """
        sales = self.fiken_manager.get_raw_data_from_fiken("sales")["_embedded"]["https://fiken.no/api/v1/rel/sales"]
        return_view = []
        externals = {}
        for sale in sales:
            # Open the customer-link, if any, and add returned json to external.
            if "customer" in sale.keys():
                externals["contact"] = self.fiken_manager.make_fiken_get_request(sale["customer"])
                # For more easy handling, both sales and purchases are associated with a contact.
                sale["contact"] = sale["customer"]
                sale.pop("customer")

            # Retrieve the sale-type based on 'kind' returned from fiken
            sale["kind"] = sale_type[sale["kind"]]

            # Edit the product-data
            for product in sale["lines"]:
                for key in product.keys():
                    # Add comma to all values where it is appropriate (fiken returns numbers without comma)
                    # Money-values should have comma
                    if key in money_values:
                        product[key] = self.comma_adder(product[key])

                # Calculate gross and make presentable
                product['grossPrice'] = "{0:.2f}".format(float(product['vat']) + float(product['netPrice']))

            # Check whether or not the purchase has a attachment attached.
            # If so, create a key we can use to retrieve it.
            # The key is 'pdf' for pdfs, 'image' for iother images.
            if "_embedded" in sale.keys():
                if "https://fiken.no/api/v1/rel/attachments" in sale["_embedded"].keys():
                    url = sale["_embedded"]["https://fiken.no/api/v1/rel/attachments"][0]["downloadUrl"]
                    if url.endswith('.pdf'):
                        sale["pdf"] = url
                    else:
                        sale["img"] = url

            # Is the sale paid or not
            if sale["paid"] == "False":
                sale["paid"] = "Nei"
            else:
                sale["paid"] = "Ja"

            # Type for display
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
