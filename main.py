# _*_coding:utf-8_*_

import os, sys
import pandas as pd
import logging
from pyquery import PyQuery as pq


def crawler(home_url):
    """
    「next >>」リンクがあればそこに飛び、scraperを呼ぶ
    なければ終了
    """
    shop_info_list = []
    page_num = 1

    while True:
        url = home_url+"page:{}".format(page_num)
        logging.info("次のページをスクレーピングします")
        logging.info(url)
        shop_info_list.extend(scraper(url))
        dom = pq(url=url)
        if dom.find(".next"):
            logging.info("次のページへ遷移します")
            page_num += 1
            continue
        else:
            logging.info("終了します")
            break

    return shop_info_list


def scraper(page_url):
    """
    ショップ一覧から情報を取得する
    取得情報
    {"name": ショップ名,
     "address": 住所,
     "link": リンク先}
    """
    shop_list = []
    dom = pq(page_url)

    # ショップの名前とリンク一覧取得
    names = []
    links = []
    for shop_name in dom("li.shop_name a"):
        query = pq(shop_name)
        names.append(query.text().encode("utf-8"))
        links.append("http://www.fashion-press.net" + query.attr("href"))

    # 住所一覧取得
    addresses = []
    for address in dom(".shop_info").items():
        addresses.append(address.text().lstrip(u"住所 : ").encode("utf-8"))

    # ループでくっつける
    for name, link, address in zip(names, links, addresses):
        logging.debug("-----------------------")
        logging.debug("NAME: {}".format(name))
        logging.debug("ADDRESS: {}".format(address))
        logging.debug("LINK: {}".format(link))
        logging.debug("-----------------------")
        shop_list.append({"name": name,
                          "link": link,
                          "address": address,
                          })
    return shop_list


def generate_shop_csv(shop_list, pref_num):
    logging.info("CSVファイルを作成します")
    data = pd.DataFrame(shop_list)
    file_name = "result_pref_{}.csv".format(pref_num)
    data.to_csv(os.path.join("result", file_name))
    logging.info("CSVファイルを作成しました")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    params = sys.argv

    # 簡単に引数チェック
    try:
        pref_num_list = params[1:]
        for pref_num in pref_num_list:
            assert(0 < int(pref_num) and int(pref_num) < 48)
    except Exception, e:
        print "---------USAGE--------"
        print "python main.py [pref_num_list*]"
        print "pref_num: from 1 to 47"
        print "----------------------"
        raise(e)

    for pref_num in pref_num_list:
        logging.info("県番号が{}のショップをスクレーピングします".format(pref_num))
        url = "http://www.fashion-press.net/shops/pref_{pref_num}/".format(
                                                            pref_num=pref_num)

        generate_shop_csv(crawler(url), pref_num)
