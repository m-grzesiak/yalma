import random
import uuid
from datetime import datetime
from enum import Enum

import requests

import config_loader


class Language(Enum):
    POLISH = 10
    ENGLISH = 11


class LuxmedApiException(Exception):
    pass


__APP_VERSION = "4.29.0"
__CUSTOM_USER_AGENT = f"Patient Portal; {__APP_VERSION}; {str(uuid.uuid4())}; Android; {str(random.randint(23, 29))};" \
                      f" {str(uuid.uuid4())}"
__BASE_DOMAIN = "https://portalpacjenta.luxmed.pl"
__API_BASE_URL = f"{__BASE_DOMAIN}/PatientPortal/NewPortal"
__CONFIG = config_loader.read_configuration("luxmed", ["username", "password", "language"])


def get_cities() -> []:
    print("Retrieving cities from the Luxmed API...")
    return __send_request_for_filters("/Dictionary/cities")


def get_services() -> []:
    print("Retrieving services from the Luxmed API...")
    return __send_request_for_filters("/Dictionary/serviceVariantsGroups")


def get_clinics_and_doctors(city_id: int, service_id: int) -> []:
    print("Retrieving clinics and doctors from the Luxmed API...")
    return __send_request_for_filters(
        f"/Dictionary/facilitiesAndDoctors?cityId={city_id}&serviceVariantId={service_id}")


def get_terms(city_id: int, service_id: int, from_date: datetime, to_date: datetime, language: Language,
              clinic_id: int = None, doctor_id: int = None) -> []:
    print("Getting terms for given search parameters...")

    session = __log_in()

    headers = {
        "Accept": "application/json",
        "accept-language": __CONFIG["language"],
        "host": "portalpacjenta.luxmed.pl",
        "Content-Type": "application/json",
        "x-requested-with": "XMLHttpRequest"
    }
    params = {
        "searchPlace.id": city_id,
        "searchPlace.type": 0,
        "serviceVariantId": service_id,
        "languageId": language.value,
        "searchDateFrom": from_date.strftime("%Y-%m-%d"),
        "searchDateTo": to_date.strftime("%Y-%m-%d"),
        "facilitiesIds": clinic_id,
        "doctorsIds": doctor_id,
        "delocalized": "false"
    }
    response = session.get(f"{__API_BASE_URL}/terms/index", headers=headers, params=params)
    __validate_response(response)

    return response.json()["termsForService"]["termsForDays"]


def __send_request_for_filters(uri: str):
    session = __log_in()
    headers = {
        "Accept": "application/json",
        "accept-language": __CONFIG["language"],
        "host": "portalpacjenta.luxmed.pl",
        "Content-Type": "application/json",
    }
    response = session.get(f"{__API_BASE_URL}{uri}", headers=headers)
    __validate_response(response)
    return response.json()


def __log_in() -> requests.Session:
    access_token = __get_access_token()

    session = requests.Session()
    headers = {
        "authorization": access_token,
        "accept-language": __CONFIG["language"],
        "upgrade-insecure-requests": "1",
        "host": "portalpacjenta.luxmed.pl",
        "Content-Type": "application/json",
        "x-requested-with": "pl.luxmed.pp",
        "Origin": __BASE_DOMAIN
    }
    params = {
        "app": "search",
        "client": 3,
        "paymentSupported": "true",
        "lang": __CONFIG["language"]
    }
    response = session.get(f"{__BASE_DOMAIN}/PatientPortal/Account/LogInToApp", headers=headers, params=params)

    if response.status_code != 200:
        raise LuxmedApiException("Unexpected response code, cannot log in")

    return session


def __get_access_token() -> str:
    headers = {"Api-Version": "2.0",
               "accept-language": __CONFIG["language"],
               "Content-Type": "application/x-www-form-urlencoded",
               "accept-encoding": "gzip",
               "x-api-client-identifier": "Android",
               "User-Agent": "okhttp/3.11.0",
               "Custom-User-Agent": __CUSTOM_USER_AGENT}

    authentication_body = {"username": __CONFIG["username"],
                           "password": __CONFIG["password"],
                           "grant_type": "password",
                           "account_id": str(uuid.uuid4())[:35],
                           "client_id": str(uuid.uuid4())
                           }

    response = requests.post(f"{__BASE_DOMAIN}/PatientPortalMobileAPI/api/token", headers=headers,
                             data=authentication_body)

    __validate_response(response)
    return response.json()["access_token"]


def __validate_response(response: requests.Response):
    if response.status_code == 503:
        raise LuxmedApiException("Service unavailable, probably Luxmed server is down for maintenance")
    if "application/json" not in response.headers["Content-Type"]:
        raise LuxmedApiException("Something went wrong")
    if response.status_code != 200:
        raise LuxmedApiException(response.json())
