# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#Schedule and Time
class ScheduleTimeItem(scrapy.Item):
    # define the fields for your item here like:
    timetable = scrapy.Field()
    current_season = scrapy.Field()

    pass

#Current Season list
class CurrentSeasonItem(scrapy.Item):
    # define the fields for your item here like:
    current_season = scrapy.Field()

    pass

#All Shows list
class AllShowsItem(scrapy.Item):
    # define the fields for your item here like:
    all_shows = scrapy.Field()

    pass


