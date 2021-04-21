import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import WwestpacItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'
base = 'https://www.westpac.com.au/about-westpac/media/media-releases/{}/'

class WwestpacSpider(scrapy.Spider):
	name = 'westpac'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [base.format(year)]

	def parse(self, response):
		articles = response.xpath('//table[@class="media-release-list"]//tr')
		for article in articles:
			date = article.xpath('.//td[@class="dt"]/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		if self.year > 2010:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2//text()').get()
		content = response.xpath('//div[@class="bodycopy"]//*[position()>2]//text()').getall()
		match = re.match(r'\d+\s?\w+\,?\s\d+',''.join(content))
		if match:
			content = content[1:]
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=WwestpacItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
