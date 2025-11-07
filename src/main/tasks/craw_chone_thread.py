import pathlib
import sys
import pandas as pd
from celery import shared_task
from loguru import logger
import datetime
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded


prefix = "https://ch.one-line.com"
home_url_list = [
    'https://ch.one-line.com/zh-hans/news/all-news/all-years/all-months'
]
url_xpath = '//div[@class="news-list"]/a/@href'
date_xpath = '//div[@class="news-release-date"]/time/text()'
title_xpath = '//h1[@class="page-title"]/text()'
content_xpath = "//div[@class='news-detail-content']//text()"

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.parent.parent.parent.resolve()
sys.path.append(str(ROOT_DIR))


ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
sys.path.append(str(ROOT_DIR))

from src.utils.craw_tools import get_primary_key, fetch_and_parse
from src.utils.db_tools import insert_into_table
# from src.utils.ai_tools import match_web_url_class_label

def convert_date_format(time_str):
    time_str = time_str.strip()
    
    # 处理中文日期格式，如"5月 23, 2025"
    if any(cn_month in time_str for cn_month in ["月"]):
        # 提取月、日、年
        parts = time_str.replace(",", "").split()
        month = parts[0].replace("月", "")
        day = parts[1]
        year = parts[2]
        
        # 将中文月份转换为数字
        month_num = int(month)
        
        # 创建datetime对象
        dt = datetime.datetime(int(year), month_num, int(day))
    else:
        # 原有的英文日期格式处理
        try:
            dt = datetime.datetime.strptime(time_str, "%d %B %Y %H:%M %Z")
        except ValueError:
            # 如果没有时区信息，尝试不带时区的格式
            try:
                dt = datetime.datetime.strptime(time_str, "%d %B %Y %H:%M")
            except ValueError:
                # 如果没有时间信息，尝试只有日期的格式
                dt = datetime.datetime.strptime(time_str, "%d %B %Y")
    
    date_str = dt.strftime("%Y-%m-%d")
    from dateutil.tz import tzoffset
    dt_utc8 = dt.replace(tzinfo=tzoffset("UTC+8", 8 * 3600))
    datetime_str = dt_utc8.strftime("%Y-%m-%d %H:%M:%S%z")
    
    return date_str, datetime_str


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
            # 取前5条时效性较高的
            download_urls = [prefix + u for u in parsed_page.xpath(url_xpath)][:5]
            if not download_urls:
                logger.error("对象解析失败!")
                continue

            logger.info(f"解析获取了{len(download_urls)}个对象")


            for url in download_urls:
                try:
                    detail_parsed = fetch_and_parse(url)
                    detail_page = detail_parsed.get("parse_html")
                    detail_title = detail_page.xpath(title_xpath)[0]
                    detail_contents_list = [t.strip() for t in detail_page.xpath(content_xpath) if t.strip()]
                    detail_contents = ''.join(detail_contents_list)
                    date = detail_page.xpath(date_xpath)[0]
                    
                    date_str, datetime_str = convert_date_format(date)
                    img_parse_url = "https://ai-doc.data.myvessel.cn/news/%E8%88%AA%E8%BF%90%E5%BF%AB%E8%AE%AF%E5%A4%B4%E5%9B%BE.jpg?OSSAccessKeyId=LTAI5t7nfdMfD7YeTFpAENJ4&Expires=2725518616&Signature=Tw08oPC0RL%2FKweHU1Q1NlJZhZHA%3D"
                    # print(date_str, datetime_str)
                    res = {"img_parse_url": img_parse_url, "detail_url": url, "detail_title": detail_title,
                        "detail_date": date_str, "detail_timestamptz": datetime_str,
                        "detail_contents": detail_contents}
                    try:
                        article_id = get_primary_key("CHONE", res)
                        res["article_id"] = article_id
                        res["update_time"] = datetime.datetime.now().isoformat()
                        res["class_level_1"] = "船司动态"
                        res["class_level_2"] = ""

                    except Exception as e:
                        logger.error(f"{e}, {e.__traceback__.tb_lineno}")
                        raise

                    res_list.append(res)
                    logger.info(f"res: {res}")
                except Exception as e:
                    logger.error(f"错误行: {e.__traceback__.tb_lineno}, error: {e}")
                    raise
            df = pd.DataFrame(res_list)
            df_dicts = df.to_dict(orient="records")
            insert_into_table("CHONE", df_dicts)
    
        except SoftTimeLimitExceeded:
            # 软超时跳过当前详情页继续执行
            logger.warning("任务执行时间超过软时间限制")
            if res_list:
                logger.info(f"当前软超时详情页数据条数: {len(res_list)}")
                df = pd.DataFrame(res_list)
                df_dicts = df.to_dict(orient="records")
                insert_into_table("CHONE", df_dicts)
            raise
        except TimeLimitExceeded:
            # 硬超时直接返回异常
            logger.error("任务执行时间超过硬时间限制")
            raise
        except Exception as e:
            logger.error(f"error: {e}, line: {e.__traceback__.tb_lineno}")
            if res_list:
                logger.info(f"当前详情页数据条数: {len(res_list)}")
                df = pd.DataFrame(res_list)
                df_dicts = df.to_dict(orient="records")
                insert_into_table("CHONE", df_dicts)
            raise



if __name__ == '__main__':
    time_task()
