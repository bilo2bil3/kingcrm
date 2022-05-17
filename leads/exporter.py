import csv
from django.shortcuts import HttpResponse


def export_csv(header, rows):
    """return an http response representing a csv file/stream
    that contains input/passed data."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="agents-stats.csv"'
    writer = csv.DictWriter(response, fieldnames=header)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return response
