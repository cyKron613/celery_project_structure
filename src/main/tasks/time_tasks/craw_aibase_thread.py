import pathlib
import sys
import pandas as pd
from loguru import logger
import datetime
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
import requests
from lxml import html

prefix = "https://news.aibase.com"
home_url_list = [
    'https://news.aibase.com/zh/news'
]
url_xpath = '//div[@pathstr="client/doc"]//a/@href'
img_xpath = '//div[@class="articleContent"]//p//img/@src'
date_xpath = '//span[2]//text()'
title_xpath = '//h1/text()'
content_xpath = "//div[@class='articleContent']//text()"

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(str(ROOT_DIR))

from celery import shared_task
from src.utils.craw_tools import get_primary_key, fetch_and_parse
from src.utils.craw_tools import insert_into_table
# from src.utils.ai_tools import match_web_url_class_label


def convert_date_format(time_str):
    dt = datetime.datetime.strptime(time_str, "%Y年%m月%d号 %H:%M")
    date_str = dt.strftime("%Y-%m-%d")
    from dateutil.tz import tzoffset
    dt_utc8 = dt.replace(tzinfo=tzoffset("UTC+8", 8 * 3600))
    datetime_str = dt_utc8.strftime("%Y-%m-%d %H:%M:%S%z")
    return date_str, datetime_str


def fetch_and_parse(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        tree = html.fromstring(response.text)
        return {"parse_html": tree}
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None


@shared_task
def time_task():
    for home_url in home_url_list:
        res_list = []
        try:
            parsed_page = fetch_and_parse(home_url)
            if not parsed_page:
                logger.error("主页解析失败!")
                return []

            parsed_page = parsed_page.get("parse_html")
            # 取前20条时效性较高的
            download_urls = [prefix + u for u in parsed_page.xpath(url_xpath)][:15]

            if not download_urls:
                print(f"{home_url} 没有获取到数据")
                continue
            logger.info(f"解析获取了{len(download_urls)}个对象")

            for url in download_urls:
                try:
                    detail_parsed = fetch_and_parse(url)
                    detail_page = detail_parsed.get("parse_html")
                    detail_title = detail_page.xpath(title_xpath)[0]
                    detail_contents_list = [t.strip() for t in detail_page.xpath(content_xpath) if t.strip()]
                    detail_contents = '\n'.join(detail_contents_list)

                    img_parse_url = detail_page.xpath(img_xpath)[0] if detail_page.xpath(img_xpath) else 'https://ai-doc.data.myvessel.cn/news/%E8%88%AA%E8%BF%90%E5%BF%AB%E8%AE%AF%E5%A4%B4%E5%9B%BE.jpg?OSSAccessKeyId=LTAI5t7nfdMfD7YeTFpAENJ4&Expires=2725518616&Signature=Tw08oPC0RL%2FKweHU1Q1NlJZhZHA%3D'
                    date = detail_page.xpath(date_xpath)[0]
                    date_str, datetime_str = convert_date_format(date)
                    # print(date_str, datetime_str)
                    res = {"img_parse_url": img_parse_url, "detail_url": url, "detail_title_cn": detail_title,
                        "detail_date": date_str, "detail_timestamptz": datetime_str,
                        "detail_contents_cn": detail_contents}
                    try:
                        article_id = get_primary_key("aibase", res)
                        res["article_id"] = article_id
                        res["update_time"] = datetime.datetime.now().isoformat()
                        res["class_level_1"] = "科技前沿"
                        res["class_level_2"] = ""

                    except Exception as e:
                        logger.error(f"{e}, {e.__traceback__.tb_lineno}")
                        raise
                    
                    if res.get("detail_contents") == "":
                        logger.error(f"内容为空: {res.get('detail_url')}, {res.get('article_id')}")
                        continue
                    res_list.append(res)
                    logger.info(f"res: {res}")
                except Exception as e:
                    logger.error(f"错误行: {e.__traceback__.tb_lineno}, error: {e}")
                    raise
            df = pd.DataFrame(res_list)
            df_dicts = df.to_dict(orient="records")
            insert_into_table(df_dicts)
            return df_dicts
            
        except SoftTimeLimitExceeded:
            # 软超时跳过当前详情页继续执行
            logger.warning("任务执行时间超过软时间限制")
            if res_list:
                logger.info(f"当前软超时详情页数据条数: {len(res_list)}")
                df = pd.DataFrame(res_list)
                df_dicts = df.to_dict(orient="records")
                insert_into_table(df_dicts)
            raise
        except TimeLimitExceeded:
            # 硬超时直接返回异常
            logger.error("任务执行时间超过硬时间限制")
            raise
        except Exception as e:
            logger.error(f"错误行: {e.__traceback__.tb_lineno}, error: {e}")
            if res_list:
                logger.info(f"当前详情页数据条数: {len(res_list)}")
                df = pd.DataFrame(res_list)
                df_dicts = df.to_dict(orient="records")
                insert_into_table(df_dicts)
            raise
        
if __name__ == '__main__':
    time_task()