from loguru import logger
from src.utils.chromium_manager import ChromiumOptionsManager
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from DrissionPage import ChromiumPage
from lxml import etree

import time

ua = UserAgent()

def get_primary_key(web_name, res_dict):
    try:
        primary_key = web_name + '_' + res_dict.get('detail_date').split(' ')[0].replace('-', '') + '_' + res_dict.get(
            'detail_title')[:4] + res_dict.get('detail_title')[-4:]
        return primary_key
    except Exception:
        try:
            primary_key = web_name + '_' + res_dict.get('detail_date').split(' ')[0].replace('-',
                                                                                             '') + '_' + res_dict.get(
                'detail_title_cn')[:4] + res_dict.get('detail_title_cn')[-4:]
            return primary_key
        except Exception as e:
            logger.error(e)
            return None


def get_with_timeout(url, need_click, chromium_options_manager):
    """
    使用DrissionPage获取页面内容，支持超时和重试
    :param url: 目标URL
    :param need_click: 是否需要点击页面元素
    :param task_id: 任务唯一标识符
    :return: 包含html和状态的字典
    """
    local_web_status = {'html': None, 'status': False}
    tab = None
    page = None
    
    try:
        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }
        # 使用单例管理器获取配置好的ChromiumOptions
        co = chromium_options_manager.get_options()
        
        page = ChromiumPage(co)
        tab = page.new_tab()
        
        # 设置页面加载超时
        tab.set.timeouts(page_load=30)
        
        # 添加模拟请求头
        tab.set.headers(headers)
        tab.get(url=url, retry=0, interval=0)
        tab.stop_loading()  # 优化点：获取到页面以后 直接停止加载。

        # if need_click:
        #     try:
        #         get_more_button = tab.ele('x://button[@class="wysiwyg-content__read-more wysiwyg-content__show"]', timeout=3)
        #         price_btn = tab.ele('x://button[@data-article-type="{C60C0F27-FFBF-40B4-A7CF-DC241D2A2A44}"]', timeout=3)
        #         ky_date_btn = tab.ele('x://label[@class="postDate__date postDate__date--toggleButton"]', timeout=3)

        #         if price_btn:
        #             price_btn.click()
        #             logger.info("mscargo site 点击了 Customer Advisorie按钮")
        #             time.sleep(3)
        #         elif get_more_button:
        #             get_more_button.click()
        #             logger.info(f"alja 点击了 read more按钮")
        #             time.sleep(3)
        #         elif ky_date_btn:
        #             ky_date_btn.click()
        #             logger.info(f"kyodo 点击了 日期按钮")
        #             time.sleep(3)
        #         else:
        #             logger.warning("未找到更多按钮")
        #     except Exception as e:
        #         logger.warning(f"点击操作失败: {str(e)}")
        
        html = tab.html
        if html:
            local_web_status['html'] = html
            local_web_status['status'] = True
        return local_web_status

    except Exception as e:
        logger.error(f"爬取失败: {url}, 错误: {str(e)}")
        return local_web_status
    finally:
        # 确保在任何情况下都清理浏览器实例和端口
        try:
            # 关闭标签页
            if tab is not None:
                try:
                    tab.close()
                except Exception as e:
                    logger.warning(f"关闭标签页失败: {str(e)}")
            
            # 关闭浏览器页面
            if page is not None:
                try:
                    page.quit()
                except Exception as e:
                    logger.warning(f"关闭浏览器页面失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"清理浏览器实例时发生错误: {str(e)}")

def fetch_and_parse(url: str, need_click: bool = False, max_retries: int = 2, retry_delay: int = 1, timeout: float = 300):
    """
    优化后的爬虫函数，直接调用避免线程池开销
    :param url: 目标URL
    :param need_click: 是否需要点击页面元素
    :param max_retries: 最大重试次数
    :param retry_delay: 重试延迟基数(秒)
    :param timeout: 单次请求超时时间(秒)
    :return: 包含html和解析结果的字典
    """
    logger.info(f"fetch_and_parse_normal解析失败，使用fetch_and_parse解析: {url}")
    chromium_options_manager = ChromiumOptionsManager()
    
    for attempt in range(max_retries):
        try:
            logger.info(f'开始第{attempt+1}次尝试: {url}, 超时时间: {timeout}秒')
            
            # 使用线程池 timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_with_timeout, url, need_click, chromium_options_manager)
                result = future.result(timeout=timeout)
            
                if result and result.get('status'):
                    html = result.get('html')
                    if html:
                        return {
                            "html": html,
                            "parse_html": etree.HTML(html),
                            "status": True
                        }
                    raise ValueError(f'获取到空HTML内容: {url}')
                
                raise RuntimeError(f'请求失败: {url}, 超时!')

        except Exception as e:
            logger.warning(f"第{attempt+1}次尝试失败: {url}, 错误: {str(e)}")
            if attempt < max_retries - 1:
                delay = retry_delay * (attempt + 1)
                logger.info(f"{delay}秒后重试...")
                time.sleep(delay)
                continue
            raise TimeoutError(f"所有{max_retries}次尝试均失败: {url}")