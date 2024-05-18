from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    OrderBy,
    RunReportRequest,
)
from jinja2 import Environment, FileSystemLoader

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
SERVICE_ACCOUNT_EMAIL = "analytics@avengerpenguin.iam.gserviceaccount.com"
VIEW_ID = "14172541"


IGNORED_PATHS = (
    "/",
    "/blog/",
)


def main():
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property="properties/352964900",
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
        order_bys=[
            OrderBy(desc=True, metric=OrderBy.MetricOrderBy(metric_name="activeUsers"))
        ],
    )
    response = client.run_report(request)

    # credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    #     json.loads(os.environ["TOKEN"]), scopes=SCOPES
    # )
    # analytics = build("analyticsreporting", "v4", credentials=credentials)
    # response = (
    #     analytics.reports()
    #     .batchGet(
    #         body={
    #             "reportRequests": [
    #                 {
    #                     "viewId": VIEW_ID,
    #                     "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
    #                     "metrics": [{"expression": "ga:pageViews"}],
    #                     "dimensions": [
    #                         {"name": "ga:pagePath"},
    #                         {"name": "ga:pageTitle"},
    #                     ],
    #                     "orderBys": [
    #                         {"fieldName": "ga:pageViews", "sortOrder": "DESCENDING"}
    #                     ],
    #                 }
    #             ]
    #         }
    #     )
    #     .execute()
    # )

    data = [
        (
            row.dimension_values[0].value,
            row.dimension_values[1].value,
            row.metric_values[0].value,
        )
        for row in response.rows
    ]

    pages = [
        {
            "url": f"https://avengerpenguin.com{path}",
            "title": title.split("|")[0].strip(),
        }
        for path, title, visits in data
        if path not in IGNORED_PATHS and "fbclid" not in path and "/search" not in path
    ]

    template_loader = FileSystemLoader(searchpath=".")
    template_env = Environment(loader=template_loader, keep_trailing_newline=True)
    template = template_env.get_template("README-TEMPLATE.md")
    template.render(the="variables", go="here")
    template.stream({"pages": pages[:5]}).dump("README.md")


if __name__ == "__main__":
    main()
