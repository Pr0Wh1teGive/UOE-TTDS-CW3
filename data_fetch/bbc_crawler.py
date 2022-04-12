import sys

from settings.dataset_conf import DatasetConfiguration
from article.bbc_article import BBCArticleFetcher

def start_bbc_crawling(config_path):
    
    # load config
    config = DatasetConfiguration()
    config.load(config_path)
    
    # fetch results
    bbc_article_fetcher = BBCArticleFetcher(config)
    bbc_article_fetcher.fetch()
