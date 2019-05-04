import datetime


class SalesDataFormatter:

    # Saf-t codes stored with corresponding mva.
    saft_to_VAT = {3: 0.25, 31: 0.15, 32: 0.1111, 33: 0.12, 5: 0, 51: 0, 52: 0, 6: 0, 7: 0}
    # Fiken VAT-types with corresponding saf-t code
    VAT_types_to_saft = {"NONE": 7, "HIGH": 3, "MEDIUM": 31, "RAW_FISH": 32, "LOW": 33, "EXEMPT_IMPORT_EXPORT": 52,
                 "EXEMPT": 5, "OUTSIDE": 6, "EXEMPT_REVERSE": 51}
    saft_to_VAT_types = {7: "NONE", 3: "HIGH", 31: "MEDIUM", 32: "RAW_FISH", 33: "LOW", 52: "EXEMPT_IMPORT_EXPORT",
                         5: "EXEMPT", 6: "OUTSIDE", 51: "EXEMPT_REVERSE" }
    # Maps the values from sale-type in html-form to corresponding expense-account
    sale_type_to_account = {"1": "3000", "2": "3010", "3": "3020"}

    @staticmethod
    def get_customer_strings(contacts):
        """
        Takes a list of contacts and extracts the customers and makes presentable strings for each customer.
        Note: Expects contact-data from fiken.
        :param contacts: The list of contacts to extract customers from.
        :return: Returns presentable strings for each customer in a tuple of the form: "customer_name (adr, postalPlace)"
        Adr and postalPlace are skipped if non-existent for the customer.
        Each tuple also contains all info about the customer, just in case, at index 1.
        """
        customer_strings = []
        customers = []
        # The contacts with a customerNumber are customers.
        for contact in contacts:
            if "customerNumber" in contact.keys():
                customers.append(contact)

        for customer in customers:
            customer_string = customer["name"]
            if "address" in customer.keys():
                if "address1" in customer["address"].keys() and "postalPlace" in customer["address"].keys():
                    customer_string += " ({}, {})".format(customer["address"]["address1"], customer["address"]["postalPlace"])
            customer_strings.append(customer_string)

        return_list = []
        for i in range(len(customers)):
            return_list.append((customer_strings[i], customers[i]))
        return return_list

    @staticmethod
    def get_account_strings(accounts):
        """
        Takes a list of accounts and makes presentable strings for each account.
        Note: Expects account-data from fiken.
        :param accounts: The list of accounts to make presentable.
        :return: Returns presentable strings for each account in a tuple of the form "account_name (account_number)"
        Also returns all info about all accounts in a separate seconds list, in case needed.
        Each tuple also contains all info about the account, just in case.
        """
        return_list = []
        for account in accounts:
            account_string = "{} ({})".format(account["name"], account["bankAccountNumber"])
            return_list.append((account_string, account))
        return return_list

    @staticmethod
    def get_product_strings(products):
        """
        Takes a list of products and makes presentable string for each product.
        Note: Expects product-data from fiken.
        :param products: The list of products to make presentable.
        :return: Returns presentable string for each product in a tuple of the form: "product_name (Pris: price, Beholdning: stock)
        Stock is skipped if not specified for the product.
        Each tuple also contains all info about the customer, just in case.
        """
        return_list = []
        for product in products:
            if "stock" in product.keys():
                product_string = "{} (Pris: {}, Beholdning: {})".format(product["name"],
                                    SalesDataFormatter.comma_adder(product["unitPrice"]), int(product["stock"]))
            else:
                product_string = "{} (Pris: {})".format(product["name"],
                                                        SalesDataFormatter.comma_adder(product["unitPrice"]))

            return_list.append((product_string, product))

        return return_list

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
        num = num[:len(num) - 2]
        return "".join(num) + ".00"

    @staticmethod
    def ready_data_for_invoice(data):
        """
        Readies invoice-data for send-in to fiken.
        Takes a form from the web-pages 'sale (invoice)' page and constructs a JSON-HAL
        object ready for send-in as specified in the fiken API.
        :param data: Pre-validated form from 'sale (invoice)' page.
        :return: Returns the JSON-HAL object based on form-data. Ready for send-in to fiken.
        """
        return_data = {}
        # Add issue date
        return_data["issueDate"] = data["date"]
        # Calculate and add due date based on "days_to_maturity"
        issue_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d")
        due_date = issue_date + datetime.timedelta(days=int(data["days_to_maturity"]))
        return_data["dueDate"] = str(due_date.date())
        # Add invoice-text if present
        if not data["comment"].strip() == '':
            return_data["invoiceText"] = data["comment"]
        # Find and add url of given bank account
        account_url = data["account"]
        return_data["bankAccountUrl"] = account_url
        # Add references if present:
        if not data["our_reference"].strip() == '':
            return_data["ourReference"] = data["our_reference"]
        if not data["their_reference"].strip() == '':
            return_data["yourReference"] = data["their_reference"]
        # Find and add url for each customer
        return_data["customer"] = {"url": data["customer"]}
        # Retrieve product info for each product (non free-text)
        product_info = []
        # Each products href:
        products = data.getlist('product')
        # The value of each product in the html-form is "href, vatType"
        for product in products:
            product_info.append({"productUrl": product.split(',')[0].strip()})
        # Each description
        descriptions = data.getlist('description')
        for i in range(len(descriptions)):
            if not descriptions[i].strip() == '':
                product_info[i]["description"] = descriptions[i]
        # Price info:
        # Get unit-price
        unit_prices = data.getlist('price')
        # Quantity for each product
        quantities = data.getlist('quantity')
        # Get discount for each product
        discounts = data.getlist('discount')
        for i in range(len(products)):
            # Add unit-price for each product
            product_info[i]["unitNetAmount"] = float(unit_prices[i])
            # Add quantity for each product
            product_info[i]["quantity"] = int(quantities[i])
            # Net amount (quantity * unit price)
            product_info[i]["netAmount"] = product_info[i]["unitNetAmount"] * product_info[i]["quantity"]
            # Discount for each product
            product_info[i]["discountPercent"] = float(discounts[i])
            # Calculate and add vat-type and vat-amount
            product_info[i]["vatType"] = products[i].split(',')[1].strip()
            saft_code = SalesDataFormatter.VAT_types_to_saft[product_info[i]["vatType"]]
            mva = SalesDataFormatter.saft_to_VAT[saft_code]
            product_info[i]["vatAmount"] = mva * product_info[i]["netAmount"]
            # Add gross amount
            product_info[i]["grossAmount"] = product_info[i]["netAmount"] + product_info[i]["vatAmount"]
        return_data["lines"] = product_info

        # Retrieve product-info for each free-text product
        product_info_free_text = []
        descriptions = data.getlist('description_free')
        comments = data.getlist('comment_free')
        sale_types = data.getlist('sale_type')
        unit_prices = data.getlist('price_free')
        discounts = data.getlist('discount_free')
        quantities = data.getlist('quantity_free')
        safts = data.getlist('sale_free_saft')
        for i in range(len(descriptions)):
            product_info_free_text.append({})
            product_info_free_text[i]["description"] = descriptions[i]
            if not comments[i].strip() == '':
                product_info_free_text[i]["comment"] = comments[i]
            product_info_free_text[i]["incomeAccount"] = SalesDataFormatter.sale_type_to_account[sale_types[i]]
            product_info_free_text[i]["unitNetAmount"] = float(unit_prices[i])
            product_info_free_text[i]["discountPercent"] = float(discounts[i])
            product_info_free_text[i]["quantity"] = int(quantities[i])
            product_info_free_text[i]["netAmount"] = product_info_free_text[i]["unitNetAmount"] * product_info_free_text[i]["quantity"]
            product_info_free_text[i]["vatType"] = SalesDataFormatter.saft_to_VAT_types[int(safts[i])]
            mva = SalesDataFormatter.saft_to_VAT[int(safts[i])]
            product_info_free_text[i]["vatAmount"] = product_info_free_text[i]["netAmount"] * mva
            product_info_free_text[i]["grossAmount"] = product_info_free_text[i]["netAmount"] + product_info_free_text[i]["vatAmount"]
        return_data["lines"] += product_info_free_text

        return return_data







