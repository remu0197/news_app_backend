from bs4 import BeautifulSoup
import requests

class Scraping:
    def __init__(self) -> None:
        pass

    def html_request(self, url) -> requests.Response:
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            print("エラー : ",e)
            return None

        if response.status_code != 200:
            return None

        return response

    # トップページから記事に関する情報をスクレイピング
    def scraping(self, url) -> BeautifulSoup:
        html_text = self.html_request(url).text
        if html_text is None:
            return False

        soap = BeautifulSoup(html_text, "html.parser")

        # class名をcsvかなんかで登録しておけば汎用化できそう
        for col in soap.find_all(class_="col-xs-12 col-md-6"):
            img_div = col.find(class_="thumb-placeholder")
            img_url = img_div.find("img").get("src")

            ttl_div = col.find(class_="c-item-ttl__heading")
            ttl_text = ttl_div.text

            # ここのid属性が一対一対応してる...?
            link_div = col.find(class_="c-item-link")
            link_url = link_div.get("href")

            if link_url is not None:
                self.article_scraping(url=link_url)

        return True

    def archive_scraping(self, url):
        pass

    # 実際の記事の画面のスクレイピング
    def article_scraping(self, url):
        # ここから共通化できる
        html_text = self.html_request(url).text
        if html_text is None:
            return False

        soap = BeautifulSoup(html_text, "html.parser")
        # ここまで

        # 記事の掲載日時
        time_div = soap.find(class_="c-time-article")
        time_text = time_div.text

        # 記事の概要
        summary_div = soap.find(class_="c-heading-article")
        summary_text = summary_div.text

        # 記事の本文
        content_div = soap.find(class_="l-article responsive-iframe news-content")
        content_texts = content_div.find_all("p")

        # 記事についてるタグ
        tag_divs = soap.find_all(class_="c-taglist-item")
        for tag in tag_divs:
            tag_text = tag.find("a")

        return True