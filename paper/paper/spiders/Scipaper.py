#!/usr/bin/env Python
# coding=utf-8

import scrapy
import copy
from paper.items import PaperItem
from scrapy.selector import Selector
from scrapy.http import Request
import scrapy
import requests
import copy
from scrapy import Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

Url = 'http://science.sciencemag.org'
headers = {
            "Accept":"*/*",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Cookie":"ARRAffinity=640e8c039577bfc2eba717140df600caa663ec7bae8bb5a6a5091f563581f452"
        } 

class ScipaperSpider(scrapy.Spider):
    name = 'Scipaper'
    allowed_domains = ['sciencemag.org']
    start_urls = ['http://sciencemag.org/']

    # #设置phantomJs
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36")
    dcap["phantomjs.page.settings.cookie"] = ("msacademic=d05c2157-9e54-48ff-ab2b-43864b29430b; ai_user=Ll7Cm|2017-08-29T08:29:14.651Z;ARRAffinity=03dbaf7ebccf3a5270373d2bf50d0eea48778d1e5597aa06ff24fffe7ddcb12c;ai_session=ATGmx|1507543708952.43|1507548269298.4")
    dcap["phantomjs.page.settings.loadImages"] = False

    browser = webdriver.PhantomJS(desired_capabilities=dcap)
    # browser = webdriver.PhantomJS()


    def start_requests(self):

        reqs = []
        for i in range(2016,2017):

        	url = 'http://science.sciencemag.org/content/by/year/' + str(i)

        	req = scrapy.Request(url)
        	reqs.append(req)
        #调度队列
        # i=1990
        # url = 'http://science.sciencemag.org/content/by/year/' + str(i)

        # req = scrapy.Request(url)
        # reqs.append(req)
        return reqs

    def parse(self, response):

        sel = Selector(response)
        JurlList = sel.xpath('//*[@class="highwire-cite-highlight"]/a/@href').extract()
        JList = set(JurlList)
        Lists = []
        for list_ in JList:
            if len(list_.split('/'))==5:###这么区分不行
            	Lists.append(list_)
        for list_ in JList:
            #构造每一期杂志的url
            fullUrl = Url+list_
            # item['url'] = fullUrl #保存即将要解析的网页
            request = scrapy.Request(url=fullUrl, callback=self.parse_fullInfo, headers=headers,  dont_filter=True)
            # meta={'item': copy.deepcopy(item)},
            yield request
    
    def parse_fullInfo(self,response):
    # def parse(self,response):
        #response的是每一期的目录界面

       
        sel = Selector(response)
        #这是每篇文章的url
        PUrllist = sel.xpath('//*[@class="media__body"]/h3/a/@href').extract()
        for L in PUrllist:
            fullUrl = Url + L
            request = scrapy.Request(url=fullUrl, callback=self.parse_PaperInfo, headers=headers,  dont_filter=True)
            yield request
        # fullUrl = 'http://science.sciencemag.org/content/286/5439/509'
        # request = scrapy.Request(url=fullUrl, callback=self.parse_PaperInfo, headers=headers,  dont_filter=True)
        # yield request

    def parse_PaperInfo(self,response):
    	#response的是每一篇论文的article界面
        sel=Selector(response)
    	item = PaperItem()
    	url = response.url
    	item['url'] = url#保存当前论文界面
    	item['Title']=''
    	# title = sel.xpath('//h1[@class="article__headline"]/div/text()').extract()
        title = sel.xpath('//meta[@name="citation_title"]/@content').extract()
    	# if title:
    	# 	title=sel.xpath('//div[@class="highwire-cite-title"]//text()').extract()
    	# if title:
        item['Title']=title[0]

        # abstract = sel.xpath('//div[@class="section abstract"]/p/text()').extract()
        abstract = sel.xpath('//meta[@name="citation_abstract"]/@content').extract()
        item['Abstract'] = ''
        if abstract:
        	item['Abstract']=abstract[0]

        journal = sel.xpath('//meta[@name="citation_journal_title"]/@content').extract()
        item['Journal'] = journal

        # authors = sel.xpath('//meta[@name="DC.Contributor"]/@content').extract()
        authors= sel.xpath('//*[@class="contributor"]/span[@class="name"]/text()').extract()

        # print '------------------------------------------------------------'
        # print authors
        # [u'Albert-L\xe1szl\xf3 Barab\xe1si', u'*', u', ', u'R\xe9ka Albert']
        
        affiliations = sel.xpath('//meta[@name="citation_author_institution"]/@content').extract()
        # if affiliations:
        # affiliations = sel.xpath('//*[@class="aff"]/address/text()').extract()
        # print '------------------------------------------------------------'
        # print affiliations
        # >>> a=response.xpath('//*[@class="aff"]//text()').extract()
        # >>> a
        # [u'Department of Physics, University of Notre Dame, Notre Dame, IN 46556, USA.']

        #很多文章确实没有作者
        item['Authors'] = authors
        item['Affiliations'] = affiliations

        Publisher = sel.xpath('//meta[@name="DC.Publisher"]/@content').extract()
        item['Publisher'] = Publisher

        info = sel.xpath('//*[@class="meta-line"]/text()').extract()
        #info = [u'\n    ', u' 15 Oct 1999:', u'Vol. 286, Issue 5439, pp. 509-512', u'DOI: 10.1126/science.286.5439.509      ']
        item['DOI'] =info[-1]
        #从info中获取日期
        date = info[1]
        Date = date.split(' ')

        d = dict()
        d['day'] = Date[1]
        d['month'] = Date[2]
        d['year'] = Date[3][0:-1]
        item['Date'] = d
        
        #从info中获取发布信息
        pubinfo = info[-2]
        pinfo = pubinfo.split(',')
        # print '--------------------------------------------'
        # print pinfo
        p = dict()
        p['Vol.'] = pinfo[0][4:]
        p['Issue'] = pinfo[1][7:]
        p['pp.'] = pinfo[2][4:]
        item['Pubinfo']=p
        
        # yield item
        #matrice信息
        M = '/tab-article-info'
        Murl = url+M

        request = scrapy.Request(url=Murl, callback=self.parse_MtriceInfo, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)
        yield request
        # yield Request(url=Murl, callback=self.parse_MtriceInfo, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)

    def parse_MtriceInfo(self,response):

    	item = response.meta['item']
        sel = Selector(response)
        
        # a=response.xpath('//a[@class="link-to-altmetric-details-tab"]/text()').extract()
        ##或abstract

        tablehead=sel.xpath('//table[@class="highwire-stats"]/thead//text()').extract()
        tablehead.insert(0,'month&year')

        ###这是Article usage表按列展开的结果[tablehead,..........]
        table = sel.xpath('//tr[@class="odd" or @class="even"]/td/text()').extract()
        # for i in table:
        if tablehead:
        	item['Tablehead'] = tablehead[0:-1]
        if table:
            item['Article_usage']=table
        
        nowurl = response.url
        request = Request(nowurl)
        request.meta['PhantomJS'] = True
        self.browser.get(request.url)
        time.sleep(8)
        # shows = self.browser.find_elements_by_link_text("Show More")
        a=self.browser.find_elements_by_xpath('//*[contains(@href,"citation_id")]')
        self.browser.quit()
        Murl = ''
        if a:
            Murl = a[0].get_attribute('href')
        if Murl:
            request = scrapy.Request(url=Murl, callback=self.parse_SocialInfo, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)
            yield request
        else:
            yield item

        # item['MurlList']=socialurllist
        # u'See more details\n
        # Picked up by 1 news outlets\n
        # Blogged by 8\n
        # Referenced in 5 policy sources\n
        # Tweeted by 8\n
        # Mentioned by 1 peer review sites\n
        # On 1 Facebook pages\n
        # Referenced in 14 Wikipedia pages\n
        # Mentioned in 1 Google+ posts\n
        # 5215 readers on Mendeley\n
        # 195 readers on CiteULike'


        # m = browser.find_elements_by_xpath('//div[@class="altmetric-embed"]')
        # if m:
        #     showmore = m[0].text
        #     tt = showmore.split('\n')




        # item['MurlList'] = sel.xpath('//a[@class="link-to-altmetric-details-tab"]//@href').extract()

        # request = scrapy.Request(url=Murl, callback=self.parse_SocialInfo, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)
        # yield item

    def parse_SocialInfo(self,response):
        #假装已经得到了接口
    	item = response.meta['item']
        sel = Selector(response)
        
        Mentioned = sel.xpath('//*[@class="mention-counts"]//text()').extract()
        item['Mentioned'] = Mentioned
# # [u'news', u'1', u' news outlet', u'\n', u'blogs', u'8', u' blogs', u'\n', u'policy', u'5', u' policy sources', u'\n', u'twitter', u'8', u' tweeters', u'\n', u'peer_reviews', u'1', u' peer review site', u'\n', u'facebook', u'1', u' Facebook page', u'\n', u'wikipedia', u'14', u' Wikipedia pages', u'\n', u'googleplus', u'1', u' Google+ user', u'\n']
        
        Readers = sel.xpath('//*[@class="reader-counts"]//text()').extract()
        item['Readers'] = Readers
        reqs2 = []
    
        
        if 'twitter' in Mentioned:
            turl = response.url  + '/twitter'#https://www.altmetric.com/details/1046171/twitter
            request = scrapy.Request(url=turl, callback=self.parse_twitters, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)
            yield request
        if 'blogs' in Mentioned:
            burl = response.url + '/blogs'
            request = scrapy.Request(url=burl, callback=self.parse_blogs, headers=headers, meta={'item': copy.deepcopy(item)}, dont_filter=True)
            yield request
        yield item
# # [u'mendeley', u'5215', u' Mendeley', u'\n', u'citeulike', u'195', u' CiteULike', u'\n', u'connotea', u'14', u' Connotea', u'\n']
#     	     item['Tweeted'] = 这个也是可以提取的
        # if reqs2:
        #     return reqs2
        # else:
        #     yield item


    def parse_blogs(self,response):
        item = response.meta['item']
        sel = Selector(response)
        summary = sel.xpath('//*[@class="section-summary"]/*[@class="text"]//text()').extract()
        full = dict()
        full["summary"] = summary

        blogs = []
        data = response.body
        soup = BeautifulSoup(data,"lxml")
        bls = soup.find_all('article',"post blogs")
        for tw in bls:
            t = dict()
            title = tw.find('div',"content").h3.get_text()
            publish = tw.find('div',"content").h4.get_text()
            content = tw.find('p',"summary").get_text()
            time = tw.find('time').get_text()
            t["title"]=title
            t["publish"]=publish
            t["content"] = content
            t["time"] = time
            blogs.append(t)
        full['blogs'] = blogs
        item['Blogs']=full
        yield item



    def parse_twitters(self,response):
        #解析推特页

        item = response.meta['item']
        
        sel = Selector(response)
        summary = sel.xpath('//*[@class="section-summary"]/*[@class="text"]//text()').extract()
        # item['Tweeter'] = {'summary':[],'tweeter':[{twitter1},{twitter2}.....]}
        full = dict()
        full["summary"] = summary
        #每一条微博的关注数
        # followers = sel.xpath('//*[@class="post twitter"]//*[@class="follower_count"]/span/text()').extract()
        # #每一条微博的发布者和微博名
        # authors = sel.xpath('//article[@class="post twitter"]//div[@class="header"]/*[@class="author"]/div[@class="name"]/text()').extract()
        # handles = sel.xpath('//article[@class="post twitter"]//div[@class="header"]/*[@class="author"]/div[@class="handle"]/text()').extract()
        #每一条微博的内容,这个内容结构太复杂了
        # contents = sel.xpath('//article[@class="post twitter"]//div[@class="content"]/p').extract()
        twitter = []
        data = response.body
        soup = BeautifulSoup(data,"lxml")
        tws = soup.find_all('article',"post twitter")
        for tw in tws:
            t = dict()
            name = tw.find('div',"name").get_text()
            handle = tw.find('div',"handle").get_text()
            follower = tw.find('div',"follower_count").span.get_text()
            content = tw.find('div',"content").p.get_text()
            time = tw.find('time').get_text()
            t["name"]=name
            t["handle"]=handle
            t["followernum"] = follower
            t["content"] = content
            t["time"] = time
            twitter.append(t)
        full['twitter'] = twitter
        item['Tweeter']=full
        yield item