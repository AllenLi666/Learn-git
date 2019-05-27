# -*- coding: utf-8 -*-
import re
import json

import scrapy
import urllib

from ..items import HighScoreMovieItem

"""
爬取豆瓣高分电影
"""


class HighScoreMovieSpider(scrapy.Spider):
    name = 'high_score_movie'
    pattern = re.compile(r'[\u4E00-\u9FA5]+')
    tag = '豆瓣高分'
    page_limit = 2
    tag = urllib.parse.quote(tag)
    allowed_domains = ['movie.douban.com']
    base_url = 'https://movie.douban.com/j/search_subjects?' \
               'type=movie&tag={}&sort=recommend&page_limit={}&page_start=0'.format(tag, page_limit)
    start_urls = [base_url]

    def parse(self, response):
        movie_list = json.loads(response.text).get('subjects')
        for movie in movie_list:
            rate = movie.get('rate')
            title = movie.get('title')
            url = movie.get('url')
            playable = movie.get('playable')
            cover = movie.get('cover')
            movie_id = movie.get('id')
            is_new = movie.get('is_new')
            data = {'rate': rate,
                    'title': title,
                    'url': url,
                    'playable': playable,
                    'cover': cover,
                    'id': movie_id,
                    'is_new': is_new}
            yield scrapy.Request(url=url, meta=data, callback=self.parse_movie)

    def parse_movie(self, response):
        item = HighScoreMovieItem()
        sel = response.css('#info')
        sel_text = sel.xpath('./text()').extract()
        sel_text = [i.strip() for i in sel_text if self.pattern.search(i)]
        item['rate'] = response.meta['rate']
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['playable'] = response.meta['playable']
        item['cover'] = response.meta['cover']
        item['movie_id'] = response.meta['id']
        item['is_new'] = response.meta['is_new']
        item['director'] = sel.xpath('./span/span[contains(text(),"导演")]/following-sibling::span[1]/a/text()').extract_first()
        item['screenwriter'] = '/'.join(sel.xpath('./span/span[contains(text(),"编剧")]/following-sibling::span/a/text()').extract())
        item['actor'] = '/'.join(sel.xpath('./span/span[contains(text(),"主演")]/following-sibling::span/a/text()').extract())
        item['movie_type'] = '/'.join(sel.xpath('./span[contains(text(),"类型")]/following-sibling::span[contains(@property, "genre")]/text()').extract())
        item['release_date'] = '/'.join(sel.xpath('./span[contains(text(),"上映日期")]/following-sibling::span[contains(@property, "initialReleaseDate")]/text()').extract())
        item['film_length'] = sel.xpath('./span[contains(text(),"片长")]/following-sibling::span[contains(@property, "runtime")]/text()').extract_first()
        item['imdb_link'] = sel.xpath('./span[contains(text(),"IMDb链接")]/following-sibling::a[@href]/@href').extract_first()
        if len(sel_text) == 0:
            item['production_country'] = ''
            item['language'] = ''
            item['alias'] = ''
        elif len(sel_text) == 1:
            item['production_country'] = sel_text[0]
            item['language'] = ''
            item['alias'] = ''
        elif len(sel_text) == 2:
            item['production_country'] = sel_text[0]
            item['language'] = sel_text[-1]
            item['alias'] = ''
        else:
            item['production_country'] = sel_text[0]
            item['language'] = sel_text[1]
            item['alias'] = sel_text[-1]
        yield item
