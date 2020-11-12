from datetime import date

import click
from tabulate import tabulate

import monitoring
from luxmed_api import LuxmedApi


def _prepare_table_view(data, headers):
    return tabulate(data, headers=headers, tablefmt="psql")


@click.group()
def main():
    pass


@main.command(help='get a list of available cities')
def cities():
    api = LuxmedApi()
    access_token = api.get_access_token()
    cities = api.get_cities(access_token)
    table_view = _prepare_table_view(cities, ["city ID", "city name"])
    print(table_view)


@main.command(help='get a list of available services')
@click.option('-c', '--city-id', type=int, required=True, help='return a list of services for the given city ID')
def services(city_id):
    api = LuxmedApi()
    access_token = api.get_access_token()
    services = api.get_services(access_token, city_id)
    table_view = _prepare_table_view(services, ["service ID", "service name"])
    print(table_view)


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
def monitor(email, city_id, service_id, from_date, to_date):
    parsed_from_date = from_date.date()
    parsed_to_date = to_date.date()
    api = LuxmedApi()
    access_token = api.get_access_token()
    visits = api.get_visits(access_token, city_id, service_id, parsed_from_date, parsed_to_date)
    monitoring.monitor_visits(visits, email)


if __name__ == '__main__':
    main()
