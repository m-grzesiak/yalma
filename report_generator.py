from datetime import datetime
from typing import Callable, Any, Union

import luxmed_api
import monitoring


def __filter_visits_by_dates(visits, from_date, to_date) -> []:
    return list(filter(lambda visit: from_date <= visit['date'] <= to_date, visits))


def __get_filters(clinic_id, doctor_id, part_of_day) -> [Callable[[Any], Union[bool, Any]]]:
    return [
        lambda visit: visit['part_of_day'] == part_of_day if part_of_day != 0 else visit,
        lambda visit: visit['clinic_id'] == clinic_id if clinic_id else visit,
        lambda visit: visit['doctor_id'] == doctor_id if doctor_id else visit
    ]


def __filter_visits_by_criteria(visits: [], part_of_day: int, clinic_id: int = None, doctor_id: int = None) -> []:
    visit_filters = __get_filters(clinic_id, doctor_id, part_of_day)

    filtered_terms = []
    for term in visits:
        filtered_visits = list(
            filter(lambda visit: all([visit_filter(visit) for visit_filter in visit_filters]), term['visits'])
        )
        if filtered_visits:
            filtered_terms.append({'date': term['date'], 'visits': filtered_visits})
    return filtered_terms


def make_report(email: str, city_id: int, service_id: int, from_date: datetime, to_date: datetime, part_of_day: int,
                clinic_id: int = None, doctor_id: int = None):
    visits = luxmed_api.get_visits(city_id, service_id, from_date, to_date)
    ready_terms = __filter_visits_by_dates(visits, from_date, to_date)
    filtered_terms = __filter_visits_by_criteria(ready_terms, part_of_day, clinic_id, doctor_id)
    monitoring.monitor_visits(filtered_terms, email)
