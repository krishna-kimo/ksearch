from scrapy import Spider, Request, FormRequest
from datetime import datetime
import json
import os
from scrapy_app.items import DynamicItem
from scrapy_app.utils import log_response, save_response
from scrapy_app.utils import data
from scrapy_app.settings import MAX_RESULTS_PER_QUERY, INPUT_FILE_PATH, INPUT_FILE_DIR
import logging
import glob


class MediumSpider(Spider):
    name = 'medium'
    #mongo_collection = None  # overriden from pipeline
    csv_fields = ['query', 'article_id', 'article_url', 'article_title', 'article_subtitle',
                  'article_created_at', 'article_updated_at', 'article_tags',
                  'count_claps', 'count_responses',
                  'author_url', 'author_name', 'author_username', 'author_bio', 'author_pic',
                  'info_words', 'info_images', 'info_time',
                  'article_text', 'article_links', 'article_images']

    def start_requests(self):

        # Get list of files from the input folder

        queries_list = data.get_keywords()

        for query in queries_list:
            yield from self.make_request(query, page=1)

    def make_request(self, query, page):
        url = 'https://medium.com/search/posts?q=%s' % query
        headers = {
            'x-xsrf-token': '1',
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        form_data = {"page": page, "pageSize": 10}
        meta = {'query': query, 'page': page}
        yield Request(url, method='POST', headers=headers, body=json.dumps(form_data),
                      meta=meta, callback=self.parse_page)

    @log_response('list')
    def parse_page(self, response):
        json_text = response.text.split('</x>', 1)[-1]
        r = json.loads(json_text)
        users_dict = r['payload']['references'].get('User')

        articles_list = r['payload']['value']
        for a in articles_list:
            item = DynamicItem()
            item['query'] = response.meta['query']
            item['article_id'] = a['id']
            item['article_url'] = 'https://medium.com//-{}'.format(item['article_id'])
            item['article_title'] = a['title']
            item['article_subtitle'] = a['virtuals']['subtitle']
            item['article_created_at'] = datetime.fromtimestamp(a['createdAt']/1000)
            item['article_updated_at'] = datetime.fromtimestamp(a['updatedAt']/1000)
            item['article_tags'] = [_['name'] for _ in a['virtuals']['tags']]

            item['count_claps'] = a['virtuals']['totalClapCount']
            item['count_responses'] = a['virtuals']['responsesCreatedCount']

            u = users_dict[a['creatorId']]
            item['author_url'] = 'https://medium.com/@{}'.format(u['username'])
            item['author_name'] = u['name']
            item['author_username'] = u['username']
            item['author_bio'] = u['bio']
            item['author_pic'] = 'https://cdn-images-1.medium.com/fit/c/256/256/%s' % u['imageId']

            item['info_words'] = a['virtuals']['wordCount']
            item['info_images'] = a['virtuals']['imageCount']
            item['info_time'] = a['virtuals']['readingTime']
            
            ## To extract the text by following the article URL
            #yield response.follow(item['article_url'], meta={'item': item}, dont_filter=True,
            #                      callback=self.parse_article, errback=self.parse_error)
            yield item
            ### Instead of Scraping use Newspapaer module to get the text and also get the keywords and summary

        next_page = response.meta['page'] + 1
        max_page = MAX_RESULTS_PER_QUERY / 10
        if articles_list and next_page <= max_page:
            yield from self.make_request(response.meta['query'], next_page)

    def parse_article(self, response):
        item = response.meta['item']
        #section = response.xpath('//div[@data-post-id][contains(@class,"postArticle-content")]/section')
        section = response.xpath('/html/body/div/div/article/div/section')

        item['article_url'] = response.url
        item['article_text'] = ' '.join(section.xpath(
            'descendant-or-self::*[not(self::h1)]/text()[normalize-space()]'
        ).getall())
        item['article_links'] = set(response.urljoin(_) for _ in section.xpath(
            'descendant::a/@href'
        ).getall())
        item['article_images'] = set(response.urljoin(_) for _ in section.xpath(
            'descendant::img/@src'
        ).getall())
        return item

    def parse_error(self, failure):
        self.logger.warning(repr(failure))
        item = failure.request.meta['item']
        item['error'] = repr(failure)
        return item
