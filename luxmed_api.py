import uuid
import random

import requests

import config_loader


class LuxmedApiException(Exception):
    pass


class LuxmedApi:
    _CUSTOM_USER_AGENT = "Patient Portal; 3.20.5; {}; Android; {}; {}".format(
        str(uuid.uuid4()), str(random.randint(23, 29)), str(uuid.uuid4())
    )
    _API_BASE_URL = "https://portalpacjenta.luxmed.pl/PatientPortalMobileAPI/api"

    @staticmethod
    def _validate_response(response):
        if response.status_code != 200:
            raise LuxmedApiException(response.json())

    @staticmethod
    def _parse_results_from_filters(results: {}):
        return [(item['Id'], item['Name']) for item in results]

    def __init__(self):
        self._config = config_loader.read_configuration("luxmed", ['username', 'password', 'language'])

    def _prepare_authentication_body(self) -> {}:
        return {'username': self._config['username'],
                'password': self._config['password'],
                'grant_type': 'password',
                'account_id': str(uuid.uuid4())[:35],
                'client_id': str(uuid.uuid4())
                }

    def _get_access_token(self) -> str:
        headers = {"Api-Version": "2.0",
                   "accept-language": self._config['language'],
                   "Content-Type": "application/x-www-form-urlencoded",
                   "accept-encoding": "gzip",
                   "x-api-client-identifier": "Android",
                   "User-Agent": "okhttp/3.11.0",
                   "Custom-User-Agent": LuxmedApi._CUSTOM_USER_AGENT}

        authentication_body = self._prepare_authentication_body()

        response = requests.post("%s/token" % LuxmedApi._API_BASE_URL, headers=headers, data=authentication_body)

        LuxmedApi._validate_response(response)
        return response.json()['access_token']

    def _prepare_headers(self, api_version: str):
        access_token = self._get_access_token()

        return {"Authorization": "Bearer " + access_token,
                "Api-Version": api_version,
                "accept-language": self._config['language'],
                "Content-Type": "application/json; charset=UTF-8",
                "accept-encoding": "gzip",
                "x-api-client-identifier": "Android",
                "User-Agent": "okhttp/3.11.0",
                "Custom-User-Agent": LuxmedApi._CUSTOM_USER_AGENT
                }

    def _send_request_for_filters(self, params: {} = ()):
        headers = self._prepare_headers("3.0")

        response = requests.get("%s/visits/available-terms/reservation-filter" % LuxmedApi._API_BASE_URL,
                                headers=headers, params=params)
        LuxmedApi._validate_response(response)
        return response.json()

    def get_cities(self) -> []:
        print("Retrieving cities from the Luxmed API...")

        response_body = self._send_request_for_filters()
        return LuxmedApi._parse_results_from_filters(response_body["Cities"])

    def get_services(self, city_id: int) -> []:
        print("Retrieving services from the Luxmed API...")

        params = {"filter.cityId": city_id}
        response_body = self._send_request_for_filters(params)
        return LuxmedApi._parse_results_from_filters(response_body["Services"])

    def get_clinics(self, city_id: int) -> []:
        print("Retrieving clinics from the Luxmed API...")

        params = {"filter.cityId": city_id}
        response_body = self._send_request_for_filters(params)
        return LuxmedApi._parse_results_from_filters(response_body["Clinics"])

    def get_doctors(self, city_id: int, service_id: int, clinic_id: int = None) -> []:
        print("Retrieving doctors from the Luxmed API...")

        params = {
            "filter.cityId": city_id,
            "filter.serviceId": service_id,
            "filter.clinicId": clinic_id
        }
        response_body = self._send_request_for_filters(params)
        return LuxmedApi._parse_results_from_filters(response_body["Doctors"])

    def get_visits(self, city_id: int, service_id: int, from_date: str, to_date: str, time_of_day: int,
                   clinic_id: int = None, doctor_id: int = None) -> []:
        print("Getting visits for given search parameters...")

        headers = self._prepare_headers("2.0")

        params = {
            "filter.cityId": city_id,
            "filter.serviceId": service_id,
            "filter.clinicId": clinic_id,
            "filter.doctorId": doctor_id,
            "filter.fromDate": from_date,
            "filter.toDate": to_date,
            "filter.timeOfDay": time_of_day
        }
        response = requests.get("%s/visits/available-terms" % LuxmedApi._API_BASE_URL, headers=headers, params=params)
        LuxmedApi._validate_response(response)

        raw_visits = response.json()

        normal_visits = raw_visits['AgregateAvailableVisitTerms']

        found_visits = []

        for visits_in_current_day in normal_visits:
            current_day_visits = []

            for current_visit in visits_in_current_day['AvailableVisitsTermPresentation']:
                visit_time = current_visit['FormattedVisitHour']
                doctor_name = current_visit['Doctor']['Name']
                clinic_name = current_visit['Clinic']['Name']
                visit = {'time': visit_time, 'doctor_name': doctor_name, 'clinic_name': clinic_name}
                current_day_visits.append(visit)

            date_with_time = visits_in_current_day['VisitDate']['StartDateTime']
            visits_in_day = {'date': date_with_time, 'visits': current_day_visits}
            found_visits.append(visits_in_day)

        return found_visits
