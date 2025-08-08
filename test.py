import requests

res = requests.get('https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/p499893800/realtime/pages?params=_u..nav%3Dmaui%26_r.2..sortKey%3DscreenPageViews%26_r.2..selmet%3D%5B%22screenPageViews%22,%22activeUsers%22%5D')

print(res.text)