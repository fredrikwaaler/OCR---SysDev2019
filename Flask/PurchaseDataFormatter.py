class PurchaseDataFormatter:

    safts_to_type = {0: "NONE", 1: "HIGH", 11: "MEDIUM", 12: "RAW_FISH", 13: "LOW"}
    safts_to_vat = {0: 0, 1: 0.25, 11: 0.15, 12: 0.1111, 13: 0.12}

    @staticmethod
    def get_supplier_strings(contacts):
        """
        Takes a list of contacts and extracts the suppliers and makes presentable strings for each supplier.
        Note: Expects contact-data from fiken.
        :param contacts: The list of contacts to extract customers from.
        :return: Returns presentable strings for each supplier in a tuple of the form:"supplier_name (adr, postalPlace)"
        Adr and postalPlace are skipped if non-existent for the supplier.
        Each tuple also contains all info about the customer, just in case, at index 1.
        """
        supplier_strings = []
        suppliers = []
        # The contacts with a supplierNumber are suppliers.
        for contact in contacts:
            if "supplierNumber" in contact.keys():
                suppliers.append(contact)

        for supplier in suppliers:
            supplier_string = supplier["name"]
            if "address" in supplier.keys():
                if "address1" in supplier["address"].keys() and "postalPlace" in supplier["address"].keys():
                    supplier_string += " ({}, {})".format(supplier["address"]["address1"], supplier["address"]["postalPlace"])
            supplier_strings.append(supplier_string)

        return_list = []
        # Add all info to tuple
        for i in range(len(suppliers)):
            return_list.append((supplier_strings[i], suppliers[i]))
        return return_list

    @staticmethod
    def get_account_strings(accounts):
        """
        Takes a list of accounts and makes presentable strings for each account.
        Note: Expects account-data from fiken.
        If there are specified 'favorite-accounts' they will appear first.
        :param accounts: The list of accounts to make presentable.
        :return: Returns presentable strings for each account in a tuple of the form "account_name (account_number)"
        Also returns all info about all accounts in a separate seconds list, in case needed.
        Each tuple also contains all info about the account, just in case.
        """

        favorite_codes = [3000, 3030, 3040, 3220, 3611, 4000, 4030, 4060, 4300, 4600, 6360, 6510, 6520, 6530, 6540, 6553,
                     6560, 6572, 6590, 6800, 6890, 7300, 7321, 7740, 7770]

        favorite_accounts = []
        other_accounts = []
        # Add and format all accounts.
        for account in accounts:
            if ":" not in account["code"]:
                account_string = "{} ({})".format(account["code"], account["name"])
                if int(account["code"]) in favorite_codes:
                    favorite_accounts.append((account_string, account))
                else:
                    other_accounts.append((account_string, account))

        # Sort both by account-code
        favorite_accounts.sort(key=PurchaseDataFormatter._get_code_num)
        other_accounts.sort(key=PurchaseDataFormatter._get_code_num)

        # Add and return accounts together, but with favorites first.
        return favorite_accounts + other_accounts

    @staticmethod
    def _get_code_num(account):
        """
        Retrieves the code of a fiken-account as int
        :param account: The account to retrieve the code for
        :return: The code of the given account
        """
        return int(account[1]["code"])

    @staticmethod
    def ready_data_for_purchase(data):
        """
        Readies purchase-data for send-in to fiken.
        Takes a form from the web-pages 'purchase' page and constructs a JSON-HAL
        object ready for send-in as specified in the fiken API.
        :param data: Pre-validated form from 'purchase' page.
        :return: Returns the JSON-HAL object based on form-data. Ready for send-in to fiken.
        """
        return_data = {}
        # Add date
        return_data["date"] = data["invoice_date"]
        # Add due-date if existent:
        if not data["maturity_date"].strip() == '':
            return_data["dueDate"] = data["maturity_date"]
        # Add purchase type
        if data['purchase_type'] == "1":
            return_data["kind"] = "SUPPLIER"
        else:
            return_data["kind"] = "CASH_PURCHASE"
            # If it is a CASH_PURCHASE, payment-info must be appended
            return_data["paymentAccount"] = data["payment-account"]
            return_data["paymentDate"] = data["invoice_date"]
            # Get total:
            total_amount = 0
            for gross in data.getlist('gross_amount'):
                total_amount += float(gross)
            return_data["paymentAmount"] = PurchaseDataFormatter.fiken_number_formatter(total_amount)
        # Add identifier if existent:
        if not data["invoice_number"].strip() == '':
            return_data["identifier"] = data["invoice_number"]
        # Retrieve product info and add product lines:
        # Descriptions
        descriptions = data.getlist('description')
        # Gross amounts
        gross_amounts = data.getlist('gross_amount')
        # Safts (Code for VAT)
        product_safts = data.getlist('vat')
        # Accounts
        accounts = data.getlist('billing_account')
        # Retrieve vatValues and vatTypes based on safts
        vat_percentages = []
        vats = []
        vat_types = []
        for saft in product_safts:
            vat_percentages.append(PurchaseDataFormatter.safts_to_vat[int(saft)])
            vat_types.append(PurchaseDataFormatter.safts_to_type[int(saft)])
        # Calculate net from vatPercentages
        # Need one overview of net_amounts to calculate vats
        net_amounts = []
        # Need one overview of net-amounts that will be sent to fiken (formatting "123.00" as "12300")
        net_amounts_to_fiken = []
        for i in range(len(gross_amounts)):
            net_amounts.append(float(gross_amounts[i]) / (1 + vat_percentages[i]))
            net_amounts_to_fiken.append(PurchaseDataFormatter.fiken_number_formatter(round(float(gross_amounts[i]) /
                                                                                  (1 + vat_percentages[i]), 2)))
            # Calculate vat-values
            vats.append(PurchaseDataFormatter.fiken_number_formatter(round(float(gross_amounts[i]) -
                                                                           float(net_amounts[i]), 2)))
        # Create product-lines for each product
        products = []
        for i in range(len(descriptions)):  # As many products as descriptions
            product_line = {"description": descriptions[i], "netPrice": net_amounts_to_fiken[i],
                            "vat": vats[i], "account": accounts[i], "vatType": vat_types[i]}
            products.append(product_line)
        # Add product-lines
        return_data["lines"] = products
        # Add supplier (not on cash_purchases)
        if data["purchase_type"] == '1':
            return_data["supplier"] = data["supplier"]

        return return_data

    @staticmethod
    def ready_payments(data):
        """
        Readies payment-data for send-in to fiken.
        The payments are structured in a json-hal manner such as specified in the fiken api documentation.
        Payments are returned in a list.
        :param data: The form-data to extract payments from
        :return: Returns a list of dictionaries describing each payment as specified in the fiken api-doc.
        """
        # Retrieve data for all payments.
        payment_accounts = data.getlist('payment-account')
        payment_amounts = data.getlist('payment-amount')
        payment_dates = data.getlist('payment-date')

        # Store payments in this list
        payments = []

        # Should be one account for each payment
        for i in range(len(payment_accounts)):
            payment = {"account": payment_accounts[i], "amount":
                PurchaseDataFormatter.fiken_number_formatter(payment_amounts[i]), "date": payment_dates[i]}
            payments.append(payment)

        return payments

    @staticmethod
    def ready_attachment(filepath, filename ):
        dict_string = '{{"filename":"{}", "attachToPurchase": true, "attachToPayment": false}}'.format(filename)

        return {'AttachmentFile': (filename, open(filepath, 'rb')), 'PurchaseAttachment': (None,
                                            '{}'.format(dict_string)), }

    @staticmethod
    def fiken_number_formatter(num):
        """
        Fiken formats numbers in a very special way.
        For instance "123.00" should be sent as 12300, and "44.8" should be sent as "4480".
        This function manipulates a number such that fiken will perceive its original value.
        :param num: The number to manipulate.
        :return: The number input manipulated in such a way that fiken understands it.
        """
        num = str(num)
        num_split = num.split('.')
        # Meaning there are no commas in the number
        if len(num_split) == 1:
            return num + "00"
        # Meaning there are commas in the number
        else:
            if len(num_split[1]) == 1:
                return num_split[0] + num_split[1] + "0"
            else:
                return num_split[0] + num_split[1]



