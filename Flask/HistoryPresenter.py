from FikenManager import FikenManager

money_values = ["amount", "netPrice", "vat"]


class HistoryPresenter:
    def __init__(self, fiken_manager: FikenManager):
        self.fiken_manager = fiken_manager

    def get_purchases_for_view(self):
        purchases = self.fiken_manager.get_data_from_fiken(data_type="purchases")
        return_view = []
        externals = {}
        for purchase in purchases:
            # Open the supplier-link, if any, and add returned json to external.
            if 'supplier' in purchase.keys():
                externals["supplier"] = self.fiken_manager.make_fiken_get_request(purchase["supplier"])

            for key in purchase.keys():
                if key in money_values:
                    purchase[key] = self.comma_adder(purchase[key])

            if purchase["paid"] == "False":
                purchase["paid"] = "Nei"
            else:
                purchase["paid"] = "Ja"

            purchase["type"] = "Kjøp"
            return_view.append((purchase, externals))
        return return_view

    def get_sales_for_view(self):
        sales = self.fiken_manager.get_data_from_fiken(data_type="sales")
        return_view = []
        externals = {}
        for sale in sales:
            if "customer" in sale.keys():
                externals["customer"] = self.fiken_manager.make_fiken_get_request(sale["customer"])

            for key in sale.keys():
                if key in money_values:
                    sale[key] = self.comma_adder(sale[key])

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
        num = num[:len(num)-2]
        return "".join(num) + ".00"
