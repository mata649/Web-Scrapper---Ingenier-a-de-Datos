from datetime import datetime
import csv
import time
import argparse
import logging
from typing import List
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
import news_page_object as news
from cfg import load_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_config()


def _fetch_article(news_site_uid: str, link: str):
    logger.info(f'Fetching the article {link}')
    article = None
    try:
        article = news.ArticlePage(news_site_uid, link)
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article', exc_info=False)

    if not article.body:
        logging.warning('Invalid article. There is no body')
        return None

    return article


def _save_in_csv(articles: List[news.ArticlePage], news_site_uid):
   
    today_date = datetime.today().date()
    headers = list(
        filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(f'./DB/{news_site_uid}_{today_date}.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for article in articles:
            row = [str(getattr(article, prob)) for prob in headers]
            writer.writerow(row)


def _news_scraper(news_site_uid: str):
    host = config['news_sites'][news_site_uid]['url']
    logger.info(f'Beginning scraper for {host}')
    homepage = news.HomePage(news_site_uid, host)
    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, link)
        time.sleep(0.2)
        if article:
            logger.info('Article Fetched!!')
            articles.append(article)
            print(article.title)
        

    _save_in_csv(articles, news_site_uid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    news_sites_choices = list(config['news_sites'].keys())
    parser.add_argument(
        'news_site',
        help='The news site that you want to scrape',
        type=str,
        choices=news_sites_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site)
