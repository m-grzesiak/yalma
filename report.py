from datetime import datetime


class Report:

    @staticmethod
    def _generate_report(all_terms: []) -> {}:
        terms = []
        overall_count = 0

        for term in all_terms:
            visits_in_clinics = Report._group_visits_by_clinic(term)

            date = term['date']
            count = len(term['visits'])
            term = {'date': date, 'count': count, 'visits': term['visits'], 'visits_in_clinics': visits_in_clinics}

            terms.append(term)
            overall_count += count

        return {'overall_count': overall_count, 'terms': terms}

    @staticmethod
    def _group_visits_by_clinic(visits: []) -> []:
        visits_in_clinics = []

        raw_grouped_visits = {}
        for visit in visits['visits']:
            clinic_name = visit['clinic_name']
            raw_grouped_visits[clinic_name] = raw_grouped_visits.get(clinic_name, [])
            raw_grouped_visits[clinic_name].append(visit)

        for clinic_name in raw_grouped_visits:
            old_visit_definitions = raw_grouped_visits[clinic_name]
            new_visits_definitions = []

            for definition in old_visit_definitions:
                doctor_name = definition['doctor_name']
                time = definition['time']
                visit_details = {'doctor_name': doctor_name, 'time': time}
                new_visits_definitions.append(visit_details)

            visits_in_clinic_count = len(new_visits_definitions)
            visit_details = {'clinic_name': clinic_name, 'count': visits_in_clinic_count,
                             'visits': new_visits_definitions}
            visits_in_clinics.append(visit_details)

        return visits_in_clinics

    def __init__(self, all_terms):
        self._report = Report._generate_report(all_terms)

    def get_report(self) -> {}:
        return self._report

    def is_any_visit_available(self) -> bool:
        return self._report['overall_count'] > 0
