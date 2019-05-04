# Base URL - https://fiken.no/api/v1

from requests import get, post
from DatabaseManager import DatabaseManager
from datetime import datetime


class FikenManager:
    def __init__(self):
        """
        The FikenManager class provides means to communicate with fiken via the fiken api.
        The FikenManager needs fiken credentials to know on which users behalf it will act.
        To properly interact with fiken, the app needs to know on which business's behalf. A single user may be
        associated with several businesses. Hence, the attribute "company_slug" is initially None. However,
        a setter is provided to properly set the associated company slug.
        The slug is a specific variant of the company name (i.e. glass-og-yoga-as for Glass og Yoga AS)
        that is handled to the fiken-api to indicate what company is acted on behalf of.
        Method "get_company_info" returns tuples with info of all associated companies, including the companies slug.
        """
        self._fiken_login = None
        self._fiken_pass = None
        self._company_slug = None

    def set_fiken_credentials(self, username, password):
        """
        Sets the fiken credentials for the FM to the provided params.
        :param username: The new fiken-username.
        :param password: The new fiken-password.
        :return:
        """
        self._fiken_login = username
        self._fiken_pass = password

    def get_fiken_login(self):
        """
        Returns the login for fiken-account associated with the fiken-manager
        :return: The login for the fiken-account associated with the fiken-manager
        """
        return self._fiken_login

    def get_company_slug(self):
        """
        Returns the company slug
        :return: The company slug
        """
        return self._company_slug

    def has_valid_login(self):
        """
        Checks whether or not the manager has been set with valid login for fiken.
        :return: True if valid login. False if not.
        """
        response = get(url="https://fiken.no/api/v1/whoAmI", auth=(self._fiken_login, self._fiken_pass))
        return response.status_code == 200

    def _hal_to_dict(self, hal_object, links=False):
        """
        Converts the hal-json object provided from fiken into a python dictionary, mapping keys with values.
        If a key holds another hal-json document as its value, we are interested in the values inside that hal-json
        object, and will add those values to the dictionary as if they were in the provided hal-json object itself.
        Note: pr.default links is excluded from the returned dictionary. If you want links included, set links to True.
        :param hal_object: The hal-json object we want to make a dictionary of.
        :param links: Whether or not the returned dict should include links.
        :return: Returns a dictionary where all the keys from the hal-json object are mapped with its values.
        If the value of a key is another hal-json object, we map the belonging values to the returned dict and
        drop the key having hal-json object as value.
        """
        return_dict = {}
        for key in hal_object.keys():
            if key == "_links" and not links:
                pass
            elif type(hal_object[key]) is dict:  # If value is another hal-object, extract it.
                return_dict.update(self._hal_to_dict(hal_object[key]))
            # If not dict, check whether or not the value is a list
            else:
                return_dict[key] = hal_object[key]

        return return_dict

    def get_data_from_fiken(self, data_type, links=False):
        """
        Used to retrieve data of the specific type from fiken using the api. Data is always returned as list of
        dictionaries, where each dict describes a specific entity (ex. an account, a product, a customer etc..)
        :param data_type: The data to retrieve from fiken.
        :param links: Whether or not the returned data should include links.
        :return: A list of dictionaries. Each dict describes an object of the set data-type.
        If there are no data of the given type, return None.
        """
        allowed_types = {"purchases": "purchases", "contacts": "contacts", "expense_accounts":
            "accounts/{}".format(datetime.now().year), "payment_accounts": "bank-accounts", "companies": "companies",
                 "products": "products", "sales": "sales"}

        if data_type not in allowed_types.keys():  # Check if the provided data-type is valid.
            raise ValueError("{} is not a valid data type. Please use one of the following key-words: {}".format(
                data_type, list(allowed_types.keys())))

        else:  # If so, try to get the data
            self._check_slug()  # Check that the slug is set
            response = self.make_fiken_get_request("https://fiken.no/api/v1/companies/{}/{}".format(
                self._company_slug, allowed_types[data_type]))

            # We are only interested in the embedded data. Always retrieved from the following link:
            try:
                return_list = []
                response = response["_embedded"]["https://fiken.no/api/v1/rel/{}".format(allowed_types[data_type].
                                                                                         split("/")[0])]
                for resp in response:
                    return_list.append(self._hal_to_dict(resp, links))
                return return_list
            except KeyError:
                # If a key error, the response does not contains embedded, and we consider the response empty.
                return []

    def get_raw_data_from_fiken(self, endpoint):
        """
        Used to retrieve data of the specific type from fiken using the api.
        Data is returned exactly as it is returned from the api.
        :param endpoint: The url-endpoint to use against the api.
        A request is thus done to "https://fiken.no/api/v1/companies/company_slug/endpoint
        :return: A dictionary with the data exactly as it is returned from fiken-api.
        """
        self._check_slug()
        response = self.make_fiken_get_request("https://fiken.no/api/v1/companies/{}/{}".format(
            self._company_slug, endpoint))
        return response

    def post_data_to_fiken(self, data, data_type):
        """
        Posts the specified data to fiken.
        The data-type need to be specified to instruct the FikenManager what data it is sending.
        I.e. purchases, data to create a invoice, customer-info etc...
        If a data-type of no known type (for the FikenManager) is specified,
        a ValueError will be thrown, displaying what types are valid.
        :param data_type: What data is being sent to fiken.
        :param data: The data that is sent
        """
        allowed_types = {"purchases": "purchases", "create_invoice": "create-invoice-service", "contacts": "contacts"}

        if data_type not in allowed_types.keys():
            raise ValueError("{} is not a valid data type. Please use one of the following key-words: {}".format(
                data_type, list(allowed_types.keys())))

        self._check_slug()  # Check that the slug is set

        url = "https://fiken.no/api/v1/companies/{}/{}".format(self._company_slug, allowed_types[data_type])
        return self.make_fiken_post_request(url, data)

    def get_company_info(self):
        """
        Returns basic information about all the companies associated with the "logged in" fiken account.
        This is returned in a list, with tuples containing company-name, org-number and associated slug.
        This is separated from "get_data_from_fiken", because it should be used to retrieve the possible slugs
        before setting it and making more requests to fiken.
        :return: Basic information (company-name, org-number, slug) of the companies associated with the
        "logged-in" fiken user. Returned as tuples in a list.
        """
        # Perform the HTTP-request and retrieve all associated company info.
        response = get(url="https://fiken.no/api/v1/companies", auth=(self._fiken_login, self._fiken_pass)).json()
        companies = response["_embedded"]["https://fiken.no/api/v1/rel/companies"]
        company_info = []
        for entry in companies:
            company_info.append((entry["name"], entry["organizationNumber"], entry["slug"]))
        return company_info

    def set_company_slug(self, slug):
        """
        Sets the "company_slug" attribute. This is used in links when making requests to the fiken-api.
        The method ensures that the slug is a valid slug of one of the associated companies.
        If not, a ValueError is thrown.
        """
        if self._is_valid_slug(slug):
            self._company_slug = slug
        else:
            raise ValueError("{} is not a valid slug. Please use get_company_info to see what is".format(slug))

    def reset_slug(self):
        """
        Sets the slug to None. Used for teardown on logout.
        """
        self._company_slug = None

    def _is_valid_slug(self, slug):
        """
        Checks whether or not the proposed slug is an actual slug of one of the associated companies.
        :param slug: The proposed slug
        :return: True if it is a valid slug, else False.
        """
        company_info = self.get_company_info()
        slugs = [entry[2] for entry in company_info]
        return slug in slugs

    def get_active_company_name(self):
        """
        Returns the name of the company associated with the active slug
        :return: The name of the company associated with the active slug.
        If there is no active company, return None.
        """
        for company in self.get_company_info():
            if company[2] == self._company_slug:
                return company[0]
        return None

    def make_fiken_get_request(self, url):
        """
        Performs a basic get request to the provided url. Returns the json object returned from fiken.
        :param url: The url to send a request to
        :return: Returns the json-object passed when performing a get-request to the url.
        """
        response = get(url=url, auth=(self._fiken_login, self._fiken_pass))
        return response.json()

    def make_fiken_post_request(self, url, post_json):
        """
        Performs a HTTP(S) post request to the provided url with a json-object as data.
        Returns the response returned from fiken.
        :param url: The url to post to
        :param post_json: The json-object to post
        :return: The response returned from fiken upon post.
        """
        return post(url=url, auth=(self._fiken_login, self._fiken_pass), json=post_json)

    def make_fiken_post_request_files(self, url, files):
        """
        Performs a HTTP(S) post request to the provided url with the given files.
        Returns the response returned from fiken.
        :param url: The url to post to
        :param files: The files to post to
        :return: The response returned from fiken upon post.
        """
        return post(url=url, auth=(self._fiken_login, self._fiken_pass), files=files)

    def _check_slug(self):
        """
        Asserts that the slug is set before interacting with the fiken-api.
        :throws: Throws a ValueError if the slug is not set.
        """
        if self._company_slug is None:
            raise ValueError("The slug must be set for the FikenManager before interacting with the api. "
                             "Use 'set_company_slug'")

    def get_bank_account_url(self, account_nr):
        """
        Returns the url of the bank-account resource associated with the given account number.
        :param account_nr: The account number of the associated account.
        :return: The url of the bank-account resource associated with the given account number.
        If none is found, or if the fiken manager is not set properly for interaction with fiken, None is returned.
        """
        try:
            accounts = self.get_data_from_fiken("payment_accounts", links=True)
            for account in accounts:
                if account['bankAccountNumber'] == account_nr:
                    return account['href']
            return None
        except ValueError:
            return None


    @staticmethod
    def is_valid_credentials(login, password):
        response = get(url="https://fiken.no/api/v1/whoAmI", auth=(login, password))
        return response.status_code == 200


