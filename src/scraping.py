from pydoc import classname
from bs4 import BeautifulSoup
import requests
import urllib
import datetime
import os
import csv

from sql_connector import ArticleClassIndex

class Scraping:
    def __init__(self) -> None:
        pass

    def html_request(self, url) -> requests.Response:
        print("Request: " + url)
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            print("エラー : ",e)
            return None

        if response.status_code != 200:
            return None

        return response

    # トップページから記事に関する情報をスクレイピング
    def scraping(self, url: str, class_names: tuple, dataset_dir: str) -> bool:
        response = self.html_request(url)
        if response is None:
            return None

        html_text = response.text
        # html_text = open("../tests/resource/animate.html")
        if html_text is None:
            return None

        soap = BeautifulSoup(html_text, "html.parser")
        results = []

        # class名をcsvかなんかで登録しておけば汎用化できそう
        for col in soap.find_all(class_=class_names[ArticleClassIndex.ARTICLE_TOP.value]):
            result = {}

            img_div = col.find(class_=class_names[ArticleClassIndex.IMG.value])
            img_url = img_div.find("img").get("src")

            ttl_div = col.find(class_=class_names[ArticleClassIndex.TITLE.value])
            result["title"] = ttl_div.text

            # ここのid属性が一意に対応してる...?
            link_div = col.find(class_=class_names[ArticleClassIndex.LINK.value])
            link_url = link_div.get("href")
            result["link"] = link_url
            qs = urllib.parse.urlparse(link_url).query
            result["id"] = urllib.parse.parse_qs(qs)["id"][0]

            result["created_date"] = datetime.datetime.now()

            if link_url is not None:
                result |= self.article_scraping(
                    class_names=class_names,
                    dataset_dir=dataset_dir,
                    url=link_url,
                    id=result["id"],
                    img_url=img_url
                )

            results.append(result)

        return results

    def archive_scraping(self, url) -> bool:
        pass

    def download_file(self, url, dst_path):
        try:
            with urllib.request.urlopen(url) as web_file:
                data = web_file.read()
                with open(dst_path, mode='wb') as local_file:
                    local_file.write(data)
        except urllib.error.URLError as e:
            print(e)

    # 実際の記事の画面のスクレイピング
    def article_scraping(self, dataset_dir: str, url: str, id: int, class_names: tuple, img_url: str) -> bool:
        # ここから共通化できる
        html_text = self.html_request(url).text
        if html_text is None:
            return None

        soap = BeautifulSoup(html_text, "html.parser")
        # ここまで

        # 記事の掲載日時
        created_date_div = soap.find(class_="c-time-article")
        created_date_text = created_date_div.text
        tdatetime = datetime.datetime.strptime(created_date_text, '%Y-%m-%d %H:%M')

        archive_dir = dataset_dir + "/{year}/{month}/{id}/".format(
            year=str(tdatetime.year),
            month=str(tdatetime.month),
            id=str(id),
        )
        os.makedirs(archive_dir, exist_ok=True)

        # 記事の概要
        summary_div = soap.find(class_=class_names[ArticleClassIndex.SUMMARY.value])
        summary_text = summary_div.text
        with open(archive_dir + "summary.txt", "w", encoding="utf-8") as f:
            f.write(summary_text)

        # 記事の本文
        content_div = soap.find(class_=class_names[ArticleClassIndex.CONTENT.value])
        content_texts = content_div.find_all("p")
        with open(archive_dir + "content.txt", "w", encoding="utf-8") as f:
            for text in content_texts:
                f.write(text.text + "\n")

        # 記事についてるタグ
        tag_divs = soap.find_all(class_=class_names[ArticleClassIndex.TAG.value])
        with open(archive_dir + "tags.csv", "w") as f:
            tags = []
            for tag in tag_divs:
                tags.append(tag.find("a").text)

            writer = csv.writer(f)
            writer.writerow(tags)

        self.download_file(url=img_url, dst_path=archive_dir+"thumbnail.png")

        return {"created_date": tdatetime}
