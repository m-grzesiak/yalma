import email_sender
from report import Report


def _notify_about_visits_availability(email_address: str, report: Report):
    notification_message = _create_notification_message(report)
    email_sender.send_email(email_address, notification_message)


def _create_notification_message(report: Report) -> str:
    generated_report = report.get_report()

    notification_message = "Overall number of visits: " + str(generated_report['overall_count']) + "\n\n"
    for term in generated_report['terms']:
        notification_message += "Date: " + term['date'] + "\n" + "Visits available in that day: " + str(
            term['count']) + "\nNumber of visits in particular clinics: \n"
        for visit in term['visits_in_clinics']:
            notification_message += "* " + visit['clinic_name'] + ": " + str(visit['count']) + "\n"

        notification_message += "\n"

    return notification_message


def monitor_visits(visits: {}, email_address: str):
    report = Report(visits)

    if report.is_any_visit_available():
        print("Visits have been found. Notification will be sent.")
        _notify_about_visits_availability(email_address, report)
    else:
        print("There are no visits available. Notification will not be sent.")
