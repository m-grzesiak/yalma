from datetime import datetime
from typing import Callable, Any, Union

import luxmed_api
import utils


def get_cities():
    return luxmed_api.get_cities()


def get_clinics(city_id: int, service_id: int) -> [{}]:
    result = luxmed_api.get_clinics(city_id, service_id)
    return sorted([__convert_clinic(clinic) for clinic in result['facilities']], key=lambda clinic: clinic['name'])


def get_services() -> [{}]:
    result = luxmed_api.get_services()
    services = []
    for category in result:
        for service in category['children']:
            if not service['children']:
                services.append({'id': service['id'], 'name': service['name']})
            for subcategory in service['children']:
                services.append({'id': subcategory['id'], 'name': subcategory['name']})

    return sorted(services, key=lambda i: i['name'])


def get_doctors(city_id: int, service_id: int, clinic_id: int = None) -> [{}]:
    result = luxmed_api.get_doctors(city_id, service_id)
    sorted_result = sorted(result['doctors'], key=lambda i: i['firstName'])

    doctors = []
    for doctor in sorted_result:
        if any(clinic == clinic_id for clinic in doctor['facilityGroupIds']) or clinic_id is None:
            doctors.append(__convert_doctor(doctor))

    return doctors


def get_available_terms(city_id: int, service_id: int, from_date: datetime, to_date: datetime, part_of_day: int,
                        clinic_id: int = None, doctor_id: int = None) -> [{}]:
    result = luxmed_api.get_terms(city_id, service_id, from_date, to_date, clinic_id, doctor_id)
    available_terms = [__parse_terms_for_day(terms_per_day) for terms_per_day in result]
    filtered_terms_by_dates = __filter_terms_by_dates(available_terms, from_date, to_date)
    return __filter_terms_by_criteria(filtered_terms_by_dates, part_of_day, clinic_id, doctor_id)


def __convert_clinic(clinic: {}) -> {}:
    return {
        'id': clinic['id'],
        'name': clinic['name']
    }


def __convert_doctor(doctor: {}) -> {}:
    return {
        'id': doctor['id'],
        'name': __parse_doctor_name(doctor)
    }


def __parse_terms_for_day(terms_in_current_day: {}) -> {}:
    term_date = utils.convert_string_to_date(terms_in_current_day['day'])
    current_day_terms = [__parse_term_for_day(current_term) for current_term in terms_in_current_day['terms']]
    return {
        'date': term_date,
        'visits': current_day_terms
    }


def __parse_term_for_day(current_term: {}) -> {}:
    term_time = utils.convert_string_to_time(current_term['dateTimeFrom'])
    doctor_details = current_term['doctor']
    doctor_name = __parse_doctor_name(doctor_details)
    return {
        'time': term_time,
        'doctor_id': doctor_details['id'],
        'doctor_name': doctor_name, 'clinic_id': current_term['clinicId'],
        'clinic_name': current_term['clinic'], 'part_of_day': current_term['partOfDay']
    }


def __parse_doctor_name(doctor_details: {}) -> str:
    return " ".join(
        filter(None, [doctor_details['academicTitle'], doctor_details['firstName'], doctor_details['lastName']])
    )


def __filter_terms_by_dates(terms: [{}], from_date: datetime, to_date: datetime) -> [{}]:
    return list(filter(lambda term: from_date <= term['date'] <= to_date, terms))


def __filter_terms_by_criteria(terms: [], part_of_day: int, clinic_id: int = None, doctor_id: int = None) -> []:
    terms_filters = __get_term_filters_definitions(clinic_id, doctor_id, part_of_day)

    filtered_terms = []
    for term in terms:
        filtered_terms_for_day = list(
            filter(lambda given_term: all([term_filter(given_term) for term_filter in terms_filters]), term['visits'])
        )
        if filtered_terms_for_day:
            filtered_terms.append({'date': term['date'], 'visits': filtered_terms_for_day})
    return filtered_terms


def __get_term_filters_definitions(clinic_id: int, doctor_id: int, part_of_day: int) -> [Callable[[Any],
                                                                                                  Union[bool, Any]]]:
    return [
        lambda term: term['part_of_day'] == part_of_day if part_of_day != 0 else term,
        lambda term: term['clinic_id'] == clinic_id if clinic_id else term,
        lambda term: term['doctor_id'] == doctor_id if doctor_id else term
    ]
