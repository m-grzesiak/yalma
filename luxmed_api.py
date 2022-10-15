import random
import uuid
from datetime import datetime

import requests

import config_loader
import utils


class LuxmedApiException(Exception):
    pass


__CUSTOM_USER_AGENT = "Patient Portal; 4.19.0; {}; Android; {}; {}".format(
    str(uuid.uuid4()), str(random.randint(23, 29)), str(uuid.uuid4())
)
__BASE_DOMAIN = "https://portalpacjenta.luxmed.pl"
__API_BASE_URL = "%s/PatientPortal/NewPortal" % __BASE_DOMAIN
__CONFIG = config_loader.read_configuration("luxmed", ['username', 'password', 'language'])


def __validate_response(response: requests.Response):
    if 'application/json' not in response.headers['Content-Type']:
        raise LuxmedApiException('Something went wrong')
    if response.status_code != 200:
        raise LuxmedApiException(response.json())


def __parse_results_from_filters(results):
    return [(item['id'], item['name']) for item in results]


def __prepare_authentication_body() -> {}:
    return "Login=" + __CONFIG['username'] + "&Password=" + __CONFIG['password']


def __get_access_token() -> str:
    headers = {"Api-Version": "2.0",
               "accept-language": __CONFIG['language'],
               "Content-Type": "application/x-www-form-urlencoded",
               "accept-encoding": "gzip",
               "x-api-client-identifier": "Android",
               "User-Agent": "okhttp/3.11.0",
               "Custom-User-Agent": __CUSTOM_USER_AGENT}

    authentication_body = {'username': __CONFIG['username'],
                           'password': __CONFIG['password'],
                           'grant_type': 'password',
                           'account_id': str(uuid.uuid4())[:35],
                           'client_id': str(uuid.uuid4())
                           }

    response = requests.post("%s/PatientPortalMobileAPI/api/token" % __BASE_DOMAIN, headers=headers,
                             data=authentication_body)

    __validate_response(response)
    return response.json()['access_token']


def __log_in() -> requests.Session:
    access_token = __get_access_token()

    session = requests.Session()
    headers = {
        'authorization': access_token,
        'accept-language': __CONFIG['language'],
        'upgrade-insecure-requests': '1',
        'host': 'portalpacjenta.luxmed.pl',
        'Content-Type': 'application/json',
        'x-requested-with': 'pl.luxmed.pp',
        'Origin': __BASE_DOMAIN
    }
    params = {
        "app": "search",
        "client": 3,
        "paymentSupported": "true",
        "lang": __CONFIG['language']
    }
    response = session.get("%s/PatientPortal/Account/LogInToApp" % __BASE_DOMAIN, headers=headers,
                           params=params)

    if response.status_code != 200:
        raise LuxmedApiException("Unexpected response code, cannot log in")

    return session


def __send_request_for_filters(uri: str):
    session = __log_in()
    headers = {
        'Accept': 'application/json',
        'accept-language': __CONFIG['language'],
        'host': 'portalpacjenta.luxmed.pl',
        'Content-Type': 'application/json',
    }
    response = session.get(__API_BASE_URL + uri, headers=headers)
    __validate_response(response)
    return response.json()


def __parse_retrieved_terms(response):
    retrieved_terms = response.json()['termsForService']['termsForDays']
    terms = []
    for visits_in_current_day in retrieved_terms:
        current_day_visits = []
        for current_visit in visits_in_current_day['terms']:
            doctor_details = current_visit['doctor']
            doctor_name = " ".join(filter(None,
                                          [doctor_details['academicTitle'], doctor_details['firstName'],
                                           doctor_details['lastName']]))
            visit_time = utils.convert_string_to_time(current_visit['dateTimeFrom'])
            visit = {'time': visit_time,
                     'doctor_id': doctor_details['id'],
                     'doctor_name': doctor_name, 'clinic_id': current_visit['clinicId'],
                     'clinic_name': current_visit['clinic'], 'part_of_day': current_visit['partOfDay']}
            current_day_visits.append(visit)

        visit_date = utils.convert_string_to_date(visits_in_current_day['day'])
        visits_in_day = {'date': visit_date, 'visits': current_day_visits}
        terms.append(visits_in_day)
    return terms


def get_cities() -> []:
    print("Retrieving cities from the Luxmed API...")

    response = __send_request_for_filters("/Dictionary/cities")

    return __parse_results_from_filters(response)


def get_services() -> []:
    print("Retrieving services from the Luxmed API...")

    response = __send_request_for_filters("/Dictionary/serviceVariantsGroups")

    services = []
    for category in response:
        for service in category['children']:
            if not service['children']:
                services.append({'id': service['id'], 'name': service['name']})
            for subcategory in service['children']:
                services.append({'id': subcategory['id'], 'name': subcategory['name']})

    return __parse_results_from_filters(sorted(services, key=lambda i: i['name']))


def get_clinics(city_id: int, service_id: int) -> []:
    print("Retrieving doctors from the Luxmed API...")

    response = __send_request_for_filters(
        "/Dictionary/facilitiesAndDoctors?cityId=%d&serviceVariantId=%d" % (city_id, service_id))

    clinics = []
    for clinic in response['facilities']:
        clinics.append(
            {'id': clinic['id'],
             'name': clinic['name']}
        )

    return __parse_results_from_filters(clinics)


def get_doctors(city_id: int, service_id: int, clinic_id: int = None) -> []:
    print("Retrieving doctors from the Luxmed API...")

    response = __send_request_for_filters(
        "/Dictionary/facilitiesAndDoctors?cityId=%d&serviceVariantId=%d" % (city_id, service_id))

    sorted_response = sorted(response['doctors'], key=lambda i: i['firstName'])

    doctors = []
    for doctor in sorted_response:
        if any(clinic == clinic_id for clinic in doctor['facilityGroupIds']) or clinic_id is None:
            doctors.append(
                {'id': doctor['id'],
                 'name': " ".join([doctor['academicTitle'], doctor['firstName'], doctor['lastName']])}
            )

    return __parse_results_from_filters(doctors)


def get_visits(city_id: int, service_id: int, from_date: datetime, to_date: datetime, clinic_id: int = None,
               doctor_id: int = None) -> []:
    print("Getting visits for given search parameters...")

    session = __log_in()

    headers = {
        'Accept': 'application/json',
        'accept-language': __CONFIG['language'],
        'host': 'portalpacjenta.luxmed.pl',
        'Content-Type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {
        "cityId": city_id,
        "serviceVariantId": service_id,
        "languageId": 10,
        "searchDateFrom": from_date.strftime("%Y-%m-%d"),
        "searchDateTo": to_date.strftime("%Y-%m-%d"),
        "facilitiesIds": clinic_id,
        "doctorsIds": doctor_id
    }
    response = session.get(__API_BASE_URL + "/terms/index", headers=headers, params=params)
    __validate_response(response)

    return __parse_retrieved_terms(response)
