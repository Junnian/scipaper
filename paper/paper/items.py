# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class PaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    ###文章信息
    Title = Field()     ####  有了

    Authors = Field()        ##  有了   有些文章确实没有作者  []
    Affiliations = Field()      ##  有了   有些文章确实没有机构 []
 
    url = Field()               ##有了   
    Abstract = Field()          ##有了   有些文章没有摘要  为[]

    Publisher = Field()


    DOI = Field()                           ## 有了
    Journal = Field() #期刊名称          ##有了
    Date = Field() #保存成一个字典      ##有了
    # Year = Field（）
    # Month = Field()
    # Day = Field()
    Pubinfo = Field()                     ## 有了
    # Vol = Field()
    # Issue = Field()
    # Page = Field()
    
    ###matrices信息
    #以这个为标准http://science.sciencemag.org/content/286/5439/509/tab-article-info
    # Picked up by 1 news outlets
    # Blogged by 8
    # Referenced in 5 policy sources
    # Tweeted by 8
    # Mentioned by 1 peer review sites
    # On 1 Facebook pages
    # Referenced in 14 Wikipedia pages
    # Mentioned in 1 Google+ posts
    # 5215 readers on Mendeley
    # 195 readers on CiteULike

    ###要从这个地方获取https://www.altmetric.com/details/1046171/policy-documents
    #这是接口https://www.altmetric.com/details.php?domain=science.sciencemag.org&citation_id=1046171&tab=news
    ##altmetric信息
    Mentioned = Field()

    Readers = Field()

    Tweeter = Field()    #存每一条推特的信息

    Blogs   = Field()
    MurlList = Field()
    # News_outlets = Field()
    # Blogged = Field()
    # Ps = Field()
    # Tweeted = Field()
    # Pr = Field()
    # Facebook = Field()
    # Wiki = Field()
    # Google = Field()
    # Mend = Field()
    # CiteULike = Field()

    Article_usage = Field()#要存成一个二维数组
    Tablehead = Field()



    pass
