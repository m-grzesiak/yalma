import email_sender
import utils
from report import Report


def make_report(terms: {}, email_address: str):
    report = Report(terms)

    if report.is_any_visit_available():
        print("Terms have been found. Notification will be sent.")
        __notify_about_visits_availability(email_address, report)
    else:
        print("There are no terms available. Notification will not be sent.")


def __notify_about_visits_availability(email_address: str, report: Report):
    notification_message = __create_report_summary(report) + __create_report_details(report)
    email_sender.send_email(email_address, notification_message)


def __create_report_summary(report: Report) -> str:
    generated_report = report.get_report()

    report_summary = "Overall number of visits: " + str(generated_report["overall_count"]) + "\n\n"

    for term in generated_report["terms"]:
        report_summary += "Date: " + utils.make_date_human_ready(term["date"]) + "\n" + \
                          "Visits available in that day: " + str(
            term["count"]) + "\nNumber of visits in particular clinics: \n"

        for visit in term["visits_in_clinics"]:
            report_summary += "* " + visit["clinic_name"] + ": " + str(visit["count"]) + "\n"

        report_summary += "\n"

    return report_summary


def __create_report_details(report: Report) -> str:
    generated_report = report.get_report()

    report_details = "\n\n--------- REPORT DETAILS ---------"

    for term in generated_report["terms"]:
        report_details += "\n" + "Date: " + utils.make_date_human_ready(term["date"]) + "\n"

        for visit in term["visits_in_clinics"]:
            report_details += "\nClinic name: " + visit["clinic_name"] + "\n"
            for visits_in_day in visit["visits"]:
                report_details += "[" + utils.make_time_human_ready(visits_in_day["time"]) + "] " \
                                  + visits_in_day["doctor_name"] + "\n"

    return report_details
