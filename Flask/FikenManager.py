# Base URL - https://fiken.no/api/v1

from requests import get, post
from DatabaseManager import DatabaseManager
from datetime import datetime


class FikenManager:
    def __init__(self, email, **kwargs):
        """
        The FikenManager class provides means to communicate with fiken via the fiken api.
        The FikenManager needs fiken credentials, which it will get from the provided database connection (kwargs).
        Note: class is used in conjecture with the sysdev app for Sukkertoppen. Specifically for the projects database.
        To properly interact with fiken, the app needs to know on which business's behalf. A single user may be
        associated with several businesses. Hence, the attribute "company_name" is initially None. However,
        a setter is provided to properly set the associated company name,
        and the "get_company_names" method returns the names of all businesses associated with the user.
        :param email: The login email (to the sysdev app).
        :param kwargs: database, host, user, password, port (external)
        :param database: The name of the database to connect to
        :param host: The host address
        :param user: The user logging in to the dbsm
        :param password: Users password for dbsm
        :param port: Port for external host
        """
        self._database_manager = DatabaseManager(**kwargs)
        self._fiken_login = self._get_fiken_login(email)
        self._fiken_pass = self._get_fiken_pass(email)
        self._company_slug = None

    def _get_fiken_login(self, email):
        """
        Returns the fiken login (if existing) of the person with the corresponding email for the sysdev app.
        :param email: The email to get fiken login by.
        :return: The fiken login of the person with corresponding email. If not exists, None.
        """
        query_result = self._database_manager.get_user_info_by_email(email)
        if query_result is not None:
            return query_result[2]
        else:
            return None

    def _get_fiken_pass(self, email):
        """
        Returns the fiken password (if existing) of the person with the corresponding login email for the sysdev app.
        :param email: Login email to sysdev app.
        :return: The fiken password of the person with the corresponding email. If not exists, None.
        """
        query_result = self._database_manager.get_user_info_by_email(email)
        if query_result is not None:
            return query_result[3]
        else:
            return None

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
            elif type(hal_object[key]) is not list:  # If not, safely map the value
                return_dict[key] = hal_object[key]
            else:  # If so, get the hal object in the list, and extract that too
                return_dict.update(self._hal_to_dict(hal_object[key][0]))
        return return_dict

    def get_data_from_fiken(self, data_type, links=False):
        """
        Used to retrieve data of the specific type from fiken using the api. Data is always returned as list of
        dictionaries, where each dict describes a specific entity (ex. an account, a product, a customer etc..)
        :param data_type: The data to retrieve from fiken.
        Legal values is: purchases, contacts, expense_accounts, payment_accounts, companies
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

    def post_data_to_fiken(self, data_type, data):
        """
        Posts the specified data to fiken.
        The data-type need to be specified to instruct the FikenManager what data it is sending.
        I.e. purchases, data to create a invoice, customer-info etc...
        If a data-type of no known type (for the FikenManager) is specified,
        a ValueError will be thrown, displaying what types are valid.
        :param data_type: What data is being sent to fiken.
        :param data: The data that is sent
        """
        allowed_types = {"purchases": "purchases"}

        if data_type not in allowed_types.keys():
            raise ValueError("{} is not a valid data type. Please use one of the following key-words: {}".format(
                data_type, list(allowed_types.keys())))

        self._check_slug()  # Check that the slug is set

        url = "https://fiken.no/api/v1/companies/{}/{}".format(self._company_slug, data_type)
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

    def _is_valid_slug(self, slug):
        """
        Checks whether or not the proposed slug is an actual slug of one of the associated companies.
        :param slug: The proposed slug
        :return: True if it is a valid slug, else False.
        """
        company_info = self.get_company_info()
        slugs = [entry[2] for entry in company_info]
        return slug in slugs

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
        Returns the json-object returned from fiken.
        :param url: The url to post to
        :param post_json: The json-object to post
        :return: The response returned from fiken upon post.
        """
        return post(url=url, auth=(self._fiken_login, self._fiken_pass), json=post_json)

    def _check_slug(self):
        """
        Asserts that the slug is set before interacting with the fiken-api.
        :throws: Throws a ValueError if the slug is not set.
        """
        if self._company_slug is None:
            raise ValueError("The slug must be set for the FikenManager before interacting with the api. "
                             "Use 'set_company_slug'")



