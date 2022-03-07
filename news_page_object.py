from typing import List
from urllib import response
import requests
import bs4
from cfg import load_config

class NewsPage:
    def __init__(self, news_site_uid, url) -> None:
        self._config = load_config()['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None
        self._visit(url)
        self.url = url
    
    
    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        response = requests.get(url)
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')

class HomePage(NewsPage):

    def __init__(self, news_site_uid, url) -> None:
       super().__init__(news_site_uid, url)

    
    @property
    def article_links(self):
        tags = self._select(self._queries['homepage_article_links'])
        link_list = [str(tag['href']) for tag in tags]
        parsed_links = []
        for link in link_list:
            if not self.url in link:
                link = self.url+link
            parsed_links.append(link)
        return set(parsed_links)

   
class ArticlePage(NewsPage):
    
    def __init__(self, news_site_uid, url) -> None:
        super().__init__(news_site_uid, url)
    
 
    @property
    def title(self):
        title = self._select(self._queries['article_title'])
        
        return  title[0].text if len(title) > 0 else '' 

    @property
    def body(self):
        body_tags = self._select(self._queries['article_body'])
        body = [p.text for p in body_tags]
        text = ' '.join(body)
        return text
    
    @property
    def date(self):
        date = self._select(self._queries['article_date'])
        return date[0]['datetime'] if len(date) > 0 else ''

    @property
    def autor(self):
     
        autor = self._select(self._queries['article_autor'])
        return autor[0].text if len(autor) > 0 else ''