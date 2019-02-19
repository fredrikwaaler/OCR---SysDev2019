# Base URL - https://fiken.no/api/v1

from requests import get
from DatabaseManager import DatabaseManager


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

    def get_prev_purchases(self):
        response = get(url="https://fiken.no/api/v1/companies/{}/purchases".format(self._company_name),
                       auth=(self._fiken_login, self._fiken_pass)).json()
        purchases_info = response["_embedded"]["https://fiken.no/api/v1/rel/purchases"][0].keys()
        print(purchases_info)

    def get_company_info(self):
        """
        Returns the names of all companies associated with the fiken user in a list.
        :return: The names of all companies associated with the fiken user in a list.
        """
        # Perform the HTTP-request and retrieve all associated company names.
        response = get(url="https://fiken.no/api/v1/companies", auth=(self._fiken_login, self._fiken_pass)).json()
        company_info = response["_embedded"]["https://fiken.no/api/v1/rel/companies"]
        company_names = []
        for entry in company_info:
            company_names.append((entry["name"], entry["organizationNumber"], entry["slug"]))
        return company_names

    @staticmethod
    def _format_company_name_for_url(company_name):
        name = company_name.lower().split()  # Obtain all words in the name
        formatted_name = ""
        for word in name:  # If not "-" append the words like this: word-word-word-
            if word != "-":
                formatted_name += word + "-"
        return formatted_name[0:len(formatted_name)-1]  # Return with last hyphen removed

    def set_company_name(self, company_name):
        """
        Sets the company name attribute to the formatted (to work with the url) version of the provided company name.
        :param company_name: The name of the company.
        """
        self._company_slug = self._format_company_name_for_url(company_name)










