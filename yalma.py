from datetime import date

import click
from tabulate import tabulate

import booking_service
import config_loader
import report_service


@click.group()
def main():
    config_loader.initialize_app_configuration()


@main.command(help='get a list of available cities')
def cities():
    retrieved_cities = booking_service.get_cities()
    __display_results(retrieved_cities, ["city ID", "city name"])


@main.command(help='get a list of available clinics')
@click.option('-c', '--city-id', type=int, required=True, help='return a list of clinics for the given city ID')
@click.option('-s', '--service-id', type=int, required=True, help='a service that doctors should be specialized in')
def clinics(city_id, service_id):
    retrieved_clinics = booking_service.get_clinics(city_id, service_id)
    __display_results(retrieved_clinics, ["clinic ID", "clinic name"])


@main.command(help='get a list of available doctors')
@click.option('-c', '--city-id', type=int, required=True, help='a city where doctors should be located')
@click.option('-s', '--service-id', type=int, required=True, help='a service that doctors should be specialized in')
@click.option('-cl', '--clinic-id', type=int, help='a clinic where you are looking for doctors')
def doctors(city_id, service_id, clinic_id):
    retrieved_doctors = booking_service.get_doctors(city_id, service_id, clinic_id)
    __display_results(retrieved_doctors, ["doctor ID", "doctor name"])


@main.command(help='get a list of available services')
def services():
    retrieved_services = booking_service.get_services()
    __display_results(retrieved_services, ["service ID", "service name"])


@main.command(help='monitor the availability of visits for the given criteria')
@click.option('-e', '--email', type=str, required=True, help='send monitoring report to the given email address')
@click.option('-c', '--city-id', type=int, required=True, help='monitor visits in the given city')
@click.option('-s', '--service-id', type=int, required=True, help='monitor visits for the given service')
@click.option('-f', '--from-date', type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today()),
              show_default=True,
              help="start from the given date. The date should be in a year-month-day format. Example: 2020-11-30. "
                   "If the user does not specify the date, today's date will be chosen")
@click.option('-t', '--to-date', type=click.DateTime(formats=["%Y-%m-%d"]), required=True,
              help='finish on the given date. The date should be in a year-month-day format. '
                   'Example: 2020-11-30')
@click.option('-td', '--time-of-day', type=click.IntRange(0, 3),
              default=0, show_default=True,
              help='time of day. If not provided, all day will be considered. Possible values: '
                   '0 - all day, '
                   '1 - until 12:00, '
                   '2 - from 12:00 to 17:00, '
                   '3 - after 17:00')
@click.option('-l', '--language', type=click.Choice(['pl', 'eng'], case_sensitive=False), default='pl',
              show_default=True, help='the language in which the doctor communicates')
@click.option('-d', '--doctor-id', type=int, help='monitor visits for the given doctor')
@click.option('-cl', '--clinic-id', type=int, help='monitor visits in the given clinic')
def monitor(email, city_id, service_id, from_date, to_date, time_of_day, language, clinic_id=None, doctor_id=None):
    parsed_from_date = from_date.date()
    parsed_to_date = to_date.date()
    available_terms = booking_service.get_available_terms(city_id, service_id, parsed_from_date, parsed_to_date,
                                                          time_of_day, language, clinic_id, doctor_id)
    report_service.make_report(available_terms, email)


def __display_results(results: {}, headers: [str]):
    if results:
        parsed_results = [(item['id'], item['name']) for item in results]
        table_view = tabulate(parsed_results, headers=headers, tablefmt="psql")
        print(table_view)
    else:
        print("No results have found for given criteria")


if __name__ == '__main__':
    main()
