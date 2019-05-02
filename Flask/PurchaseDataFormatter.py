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
        :param accounts: The list of accounts to make presentable.
        :return: Returns presentable strings for each account in a tuple of the form "account_name (account_number)"
        Also returns all info about all accounts in a separate seconds list, in case needed.
        Each tuple also contains all info about the account, just in case.
        """

        # TODO - Favorites should be added here.
        favorites = []

        return_list = []
        # Add and format all accounts not already in favorites.
        for account in accounts:
            if account["code"] not in favorites and ":" not in account["code"]:
                account_string = "{} ({})".format(account["code"], account["name"])
                return_list.append((account_string, account))

        # Sort by account-code
        return_list.sort(key=PurchaseDataFormatter._get_code_num)

        return return_list

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
        return_data = {}
        # Add date
        return_data["date"] = data["invoice_date"]
        # Add due-date if existent:
        if not data["maturity_date"].strip() == '':
            return_data["dueDate"] = data["maturity_date"]
        # Add purchase type
        if data['purchase_type'] == "0":
            return_data["kind"] = "SUPPLIER"
        else:
            return_data["kind"] = "CASH_PURCHASE"
        # Add identifier if existent:
        if not data["invoice_number"].strip() == '':
            return_data["identifier"] = data["invoice_number"]
        # TODO - ADD "PAID". Hør med klaus hvorfor den ikke er i request.form
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
        net_amounts = []
        for i in range(len(gross_amounts)):
            net_amounts.append(float(gross_amounts[i]) / (1 + vat_percentages[i]))
            # Calculate vat-values
            vats.append(float(gross_amounts[i]) - float(net_amounts[i]))
        # Create product-lines for each product
        products = []
        for i in range(len(descriptions)):  # As many products as descriptions
            product_line = {"description": descriptions[i], "netPrice": net_amounts[i],
                            "vat": vats[i], "account": accounts[i], "vatType": vat_types[i]}
            products.append(product_line)
        # Add product-lines
        return_data["lines"] = products
        # Add supplier
        return_data["supplier"] = data["supplier"]

        # TODO - Registering av betaling
        # TODO - Registrering av attachment








