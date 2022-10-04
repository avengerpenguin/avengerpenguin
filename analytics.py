import json
import os
from jinja2 import Environment, PackageLoader, select_autoescape, \
    FileSystemLoader
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
VIEW_ID = '14172541'


IGNORED_PATHS = (
    '/', '/blog/',
)

def main():
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['TOKEN']), scopes=SCOPES)
    analytics = build('analyticsreporting', 'v4', credentials=credentials)
    response = analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [
                        {'startDate': '30daysAgo', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:pageViews'}],
                    'dimensions': [{'name': 'ga:pagePath'}, {'name': 'ga:pageTitle'}],
                    "orderBys": [
                        {
                            "fieldName": "ga:pageViews",
                            "sortOrder": "DESCENDING"
                        }],
                }]
        }
    ).execute()

    pages = [
        {
            'url': f'https://avengerpenguin.com{path}',
            'title': row['dimensions'][1].split('|')[0].strip(),

        }
        for report in response['reports']
        for row in report['data']['rows']
        for path in [row['dimensions'][0]]
        if path not in IGNORED_PATHS and 'fbclid' not in path and '/search' not in path
    ]

    template_loader = FileSystemLoader(searchpath=".")
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("README-TEMPLATE.md")
    template.render(the="variables", go="here")
    template.stream({'pages': pages[:5]}).dump('README.md')


if __name__ == '__main__':
    main()
