import sys

from settings.dataset_conf import DatasetConfiguration
from article.nytimes_article import NytimeArticleFetcher


def start_nytimes_crawling(config_path):
    
    # load config
    config = DatasetConfiguration()
    config.load(config_path)
    
    # fetch results
    nytime_article_fetcher = NytimeArticleFetcher(config)
    nytime_article_fetcher.fetch()