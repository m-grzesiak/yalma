import email_sender
from report import Report


def _notify_about_visits_availability(email_address: str, report: Report):
    notification_message = _create_report_summary(report) + _create_report_details(report)
    email_sender.send_email(email_address, notification_message)


def _create_report_summary(report: Report) -> str:
    generated_report = report.get_report()

    report_summary = "Overall number of visits: " + str(generated_report['overall_count']) + "\n\n"

    for term in generated_report['terms']:
        report_summary += "Date: " + term['date'] + "\n" + "Visits available in that day: " + str(
            term['count']) + "\nNumber of visits in particular clinics: \n"

        for visit in term['visits_in_clinics']:
            report_summary += "* " + visit['clinic_name'] + ": " + str(visit['count']) + "\n"

        report_summary += "\n"

    return report_summary


def _create_report_details(report: Report) -> str:
    generated_report = report.get_report()

    report_details = ""

    for term in generated_report['terms']:
        report_details += "\n" + "Date: " + term['date'] + "\n"

        for visit in term['visits_in_clinics']:
            report_details += "\nClinic name: " + visit['clinic_name'] + "\n"
            for visits_in_day in visit['visits']:
                report_details += "[" + visits_in_day['time'] + "] " + visits_in_day['doctor_name'] + "\n"

    return report_details


def monitor_visits(visits: {}, email_address: str):
    report = Report(visits)

    if report.is_any_visit_available():
        print("Visits have been found. Notification will be sent.")
        _notify_about_visits_availability(email_address, report)
    else:
        print("There are no visits available. Notification will not be sent.")
