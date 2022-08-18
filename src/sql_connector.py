import csv
from datetime import datetime
from enum import Enum
from re import S
import sqlite3

class ArticleClassIndex(Enum):
    SITE_NAME = 0
    ARTICLE_TOP = 1
    ARTICLE_ARCHIVE = 2
    IMG = 3
    TITLE = 4
    LINK = 5
    DATE = 6
    SUMMARY = 7
    CONTENT = 8
    TAG = 9

class SQLConnector:
    def __init__(self, dbname="main.db") -> None:
        self.__dbname = dbname
        self.__conn = sqlite3.connect(self.__dbname)
        self.__cur = self.__conn.cursor()
        self.__class_colnames = []

        with open("./resource/class_name.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                for col in row:
                    self.__class_colnames.append(col)
                break

    def __del__(self) -> None:
        self.__conn.close()

    def create_article_table(self, table_name) -> bool:
        """
        SQLite3 で記事の情報をまとめるテーブルを作成する．

        Returns
        -------
        bool
            テーブルの作成が成功したかどうか返す．
        """
        self.__cur.execute("SELECT * FROM sqlite_master WHERE type='table' and name='{table_name}'".format(
            table_name=table_name
        ))
        if not self.__cur.fetchone():
            self.__cur.execute(
                'CREATE TABLE {table_name}(id INTEGER PRIMARY KEY, title STRING, link STRING, created_date DATETIME)'.format(
                    table_name=table_name
                )
            )

        return True

    def import_class_csv(self):
        with open("./resource/class_name.csv", "r") as f:
            reader = csv.reader(f)
            is_rowname = True
            for row in reader:
                if is_rowname:
                    is_rowname = False
                    continue
                
                with open("./resource/insert_class.sql", "r") as sqlfile:
                    sql_statement = sqlfile.read().format(
                        site_name=row[ArticleClassIndex.SITE_NAME],
                        article_top=row[ArticleClassIndex.ARTICLE_TOP],
                        article_archive=row[ArticleClassIndex.ARTICLE_ARCHIVE],
                        img=row[ArticleClassIndex.IMG],
                        title=row[ArticleClassIndex.TITLE],
                        link=row[ArticleClassIndex.LINK],
                        date=row[ArticleClassIndex.DATE],
                        summary=row[ArticleClassIndex.SUMMARY],
                        content=row[ArticleClassIndex.CONTENT],
                        tag=row[ArticleClassIndex.TAG]
                    )

                try:
                    self.__cur.execute(sql_statement)
                    self.__conn.commit()
                except Exception as e:
                    print(e)
                    self.__conn.rollback()

    def load_class_names(self, site_name) -> tuple:
        class_names = ()
        with open("./resource/select_class.sql", "r") as f:
            sql_statement = f.read().format(
                site_name=site_name
            )

            try:
                class_names = self.__cur.execute(sql_statement).fetchone()
                
            except Exception as e:
                print(e)
                self.__conn.rollback()

        return class_names

    def insert_article(self, table_name: str, values: dict) -> bool:
        """
        指定したテーブルに任意の記事の情報を挿入する．
        
        Parameters
        ----------
        table_name : str
            情報を挿入するテーブル名
        values : dict
            挿入する情報のディクショナリ変数

        Returns
        -------
        bool
            挿入成功したかどうかを返す．
        """
        sql_statement = "SELECT created_date FROM {table_name} WHERE id={id}".format(
            table_name=table_name,
            id=values["id"]
        )
        target_archive = self.__cur.execute(sql_statement).fetchone()

        if target_archive:
            target_time = datetime.strptime(target_archive[0], '%Y-%m-%d %H:%M:%S.%f')
            if values["created_date"] <= target_time:
                return False

            sql_statement = "UPDATE {table_name} SET title='{title}', link='{link}', created_date='{created_date}' WHERE id={id}".format(
                table_name=table_name,
                title=values["title"],
                link=values["link"],
                created_date=values["created_date"],
                id=values["id"],
            )
            print(sql_statement)
            self.__cur.execute(sql_statement)
            self.__conn.commit()

            return True

        sql_filepath = "./resource/insert.sql"
        with open(sql_filepath, "r") as f:
            try:
                sql_statement = f.read().format(
                    table_name=table_name,
                    id=values["id"],
                    title=values["title"],
                    link=values["link"],
                    created_date=values["created_date"]
                )

                self.__cur.execute(sql_statement)
                self.__conn.commit()
            except Exception as e:
                print("ERROR: " + str(e))
                self.__conn.rollback()

        return True

if __name__ == "__main__":
    sc = SQLConnector()
    # sc.create_table(table_name='test2')
    values = {
        "id": 9999999999,
        "title": "title2",
        "link": "https://www.test2.com",
        "created_date": datetime.now()
    }
    sc.insert_article(
        table_name="animatetimes",
        values=values
    )

    # print(class_names)