from scraping import Scraping
from sql_connector import SQLConnector
import urllib

def main():
    # (予定)
    # ・スクレイピングスケジューラのスレッド
    # ・Rest APIのリクエストを受け取るスレッド

    scraping = Scraping()
    sc = SQLConnector()
    target_url = "https://www.animatetimes.com/"

    # サブレベルドメイン(サイト名)を取得
    domain = urllib.parse.urlparse(target_url).netloc
    second_domain = domain.split(".")[1]

    class_names = sc.load_class_names(site_name=second_domain)
    dataset_dir = "../dataset/" + second_domain
    values_list = scraping.scraping(url=target_url, class_names=class_names, dataset_dir=dataset_dir)
    sc.create_article_table(second_domain)
    
    for values in values_list:
        sc.insert_article(
            table_name=second_domain,
            values=values
        )

    # url = "https://www.animatetimes.com/news/details.php?id=1660786886"
    # qs = urllib.parse.urlparse(url).query
    # id = urllib.parse.parse_qs(qs)
    # print(id)

if __name__ == "__main__":
    main()