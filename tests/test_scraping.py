# import pytest
import sys
from unittest.mock import patch

sys.path.append("../")
from src import scraping

class TestScraping:
    def __init__(self) -> None:
        pass

    # htmlリクエストが失敗した場合
    @patch('src.scraping.Scraping.html_request')
    def test_scraping_request_failed(self, get):
        get.return_value.text = None
        target = scraping.Scraping()
        assert target.scraping(url="hoge") == False

    # htmlリクエストが成功して
    # article_scrapingが失敗した場合
    @patch('src.scraping.Scraping.html_request')
    @patch('src.scraping.Scraping.article_scraping')
    def test_scraping_article_scraping_failed(self, html_request, article_scraping):
        html_request.return_value.text = open("./resource/animate.html")
        article_scraping.return_value = False

        target = scraping.Scraping()
        assert target.scraping(url="hoge") == False

    # 実行成功
    @patch('src.scraping.Scraping.html_request')
    @patch('src.scraping.Scraping.article_scraping')
    def test_scraping(self, html_request, article_scraping):
        html_request.return_value.text = open("./resource/animate.html")
        article_scraping.return_value = False

        target = scraping.Scraping()
        assert target.scraping(url="hoge") == True

    @patch('src.scraping.Scraping.html_request')
    def test_article_scraping(self, html_request):
        html_request.return_value.text = open(
            "./resource/animate_article.html",
            encoding="utf-8"
        )
        target = scraping.Scraping()
        assert target.article_scraping(url="hoge") == True


if __name__ == "__main__":
    test = TestScraping()
    test.test_article_scraping()
