import csv
import requests
from lxml import html

MAX_URLS = 5

visited_urls = []


def scrape_page(url, writer):
    visited_urls.append(url)

    page = requests.get(url)
    tree = html.fromstring(page.content)

    non_working_days = tree.xpath('//*[@color="gray"]/text()')

    if non_working_days and all(non_working_day not in visited_urls for non_working_day in non_working_days):
        visited_urls.extend(non_working_days)
        for non_working_day in non_working_days:
            print('%s is a non-working day.' % non_working_day)

    date_elements = tree.xpath('//center/b/text()')
    if date_elements:
        date = date_elements[0]
    else:
        date = 'Unknown Date'

    for tr in tree.xpath('//tr[position() > 2 and count(td) >= 5]'):
        row_data = [td.text_content() for td in tr.xpath('.//td')]
        if len(row_data) == 6:
            company, symbol, eps, time, add, conf_call = row_data
        else:
            company, symbol, eps, time, add = row_data
            conf_call = ''

        print(company + '  |  ' + symbol + '  |  ' + time + '  |  ' + date)

        writer.writerow([company, symbol, time, date, conf_call])

    next_day_urls = tree.xpath('//center/b/following-sibling::a/@href')[0:-1]

    for next_day_url in next_day_urls:
        if len(visited_urls) == MAX_URLS:
            break

        absolute_url = 'http://biz.yahoo.com' + next_day_url
        if absolute_url not in visited_urls:
            scrape_page(absolute_url, writer)


with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Company', 'Symbol', 'Time', 'Date', 'Conf Call'])
    scrape_page('http://biz.yahoo.com/research/earncal/today.html', writer)

    if len(visited_urls) < MAX_URLS:
        page = requests.get(visited_urls[-1])
        tree = html.fromstring(page.content)

        next_week_url = tree.xpath('//center/b/following-sibling::a/@href')[-1]
        absolute_next_week_url = 'http://biz.yahoo.com' + next_week_url
        scrape_page(absolute_next_week_url, writer)
