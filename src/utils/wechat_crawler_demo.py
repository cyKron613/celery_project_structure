#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
import random
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import argparse
from fake_useragent import UserAgent
import dotenv

# 加载环境变量
dotenv.load_dotenv()

# 请在这里填入你的token和cookie
TOKEN = os.getenv('WECHAT_TOKEN')
COOKIE = os.getenv('WECHAT_COOKIE')

# 初始化UserAgent对象
user_agent = UserAgent()

# 输出目录
OUTPUT_DIR = os.path.join(os.getcwd(), 'wechat_articles')

def get_random_headers():
    """获取随机的请求头"""
    return {
        "Host": "mp.weixin.qq.com",
        "User-Agent": user_agent.random,
        'cookie': COOKIE,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://mp.weixin.qq.com/'
    }

def search_account(account_name):
    """搜索公众号，获取fakeid"""
    print(f"正在搜索公众号: {account_name}")

    url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
    params = {
        'action': 'search_biz',
        'scene': 1,
        'begin': 0,
        'count': 10,
        'query': account_name,
        'token': TOKEN,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
    }

    try:
        response = requests.get(url, headers=get_random_headers(), params=params)
        data = response.json()

        if 'list' not in data:
            print(f"搜索失败: {data.get('base_resp', {}).get('err_msg', '未知错误')}")
            return []

        accounts = []
        for item in data['list'][:3]:
            accounts.append({
                'name': item['nickname'],
                'fakeid': item['fakeid']
            })

        print('搜索到相关公众号：')
        for i, account in enumerate(accounts):
            print(f"  {i + 1}. {account['name']}")

        return accounts

    except Exception as e:
        print(f"搜索公众号出错: {e}")
        return []

def get_articles_list(fakeid, account_name, max_articles=10):
    """获取公众号文章列表"""
    print(f"正在获取 {account_name} 的文章列表（目标：{max_articles}篇）...")

    url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
    articles = []
    page = 0
    finished = False

    while len(articles) < max_articles and not finished:
        params = {
            'action': 'list_ex',
            'begin': page * 5,
            'count': '5',
            'fakeid': fakeid,
            'type': '9',
            'query': '',
            'token': TOKEN,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
        }

        try:
            time.sleep(random.uniform(3, 5))
            response = requests.get(url, headers=get_random_headers(), params=params)
            data = response.json()
            
            if 'base_resp' in data and data['base_resp'].get('error_msg'):
                print(data['base_resp']['error_msg'])
                time.sleep(60)
                continue
                
            if 'app_msg_list' not in data or not data['app_msg_list']:
                print(f"获取文章列表失败: {data.get('base_resp', {}).get('err_msg', '未知错误')}")
                break

            for article in data['app_msg_list']:
                if len(articles) >= max_articles:
                    finished = True
                    print(f"文章数量达到 {max_articles} 篇，结束搜索")
                    break

                # 添加文章信息
                articles.append({
                    'account_name': account_name,
                    'title': article['title'],
                    'link': article['link'],
                    'digest': article.get('digest', ''),
                    'publish_time': datetime.fromtimestamp(article['update_time']).strftime('%Y-%m-%d %H:%M:%S'),
                    'publish_timestamp': article['update_time']
                })
                print(f'添加文章：{len(articles)} {article["title"]}')

            page += 1

        except Exception as e:
            print(f"获取出错: {e}")
            break

    print(f"获取到 {len(articles)} 篇文章")
    return articles

def get_article_content(url, max_retries=3):
    """获取文章内容"""
    for retry in range(max_retries):
        try:
            headers = {
                "Host": "mp.weixin.qq.com",
                "User-Agent": user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://mp.weixin.qq.com/'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            for selector in ['#js_content', '.rich_media_content', '#activity-detail']:
                element = soup.find(id=selector[1:]) if selector.startswith('#') else soup.find(class_=selector[1:])
                if element:
                    return convert_to_markdown(element)
            return "未找到文章内容区域"

        except:
            if retry < max_retries - 1:
                time.sleep(3)
    return "获取内容失败"

def get_structured_article_data(url, max_retries=3):
    """获取文章结构化数据，包含标题、内容、日期、图片等信息"""
    for retry in range(max_retries):
        try:
            headers = {
                "Host": "mp.weixin.qq.com",
                "User-Agent": user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://mp.weixin.qq.com/'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取文章标题
            title_element = soup.find('h1') or soup.find('h2') or soup.find(class_='rich_media_title')
            article_title = title_element.get_text().strip() if title_element else ""

            # 获取文章内容区域
            content_element = None
            for selector in ['#js_content', '.rich_media_content', '#activity-detail']:
                element = soup.find(id=selector[1:]) if selector.startswith('#') else soup.find(class_=selector[1:])
                if element:
                    content_element = element
                    break

            if not content_element:
                return {
                    "article_title": article_title,
                    "article_content": "未找到文章内容区域",
                    "article_date": "",
                    "article_images": [],
                    "article_url": url
                }

            # 提取文章内容（正文 + 引用）
            content_text = extract_article_content(content_element)
            
            # 提取图片信息
            images = extract_article_images(content_element)
            
            # 提取发布日期
            date_element = soup.find('em', id='publish_time') or soup.find(class_='rich_media_meta rich_media_meta_text')
            article_date = date_element.get_text().strip() if date_element else ""

            return {
                "article_title": article_title,
                "article_content": content_text,
                "article_date": article_date,
                "article_images": images,
                "article_url": url
            }

        except Exception as e:
            print(f"获取结构化数据出错: {e}")
            if retry < max_retries - 1:
                time.sleep(3)
    
    return {
        "article_title": "",
        "article_content": "获取内容失败",
        "article_date": "",
        "article_images": [],
        "article_url": url
    }

def extract_article_content(element):
    """提取文章内容（正文 + 引用）"""
    if not element:
        return ""
    
    content_parts = []
    
    # 提取所有段落和文本内容
    for tag in element.find_all(['p', 'div', 'span', 'section']):
        text = tag.get_text().strip()
        if text and len(text) > 0:
            content_parts.append(text)
    
    # 提取引用内容
    for blockquote in element.find_all('blockquote'):
        quote_text = blockquote.get_text().strip()
        if quote_text:
            content_parts.append(f"引用：{quote_text}")
    
    # 合并内容，去除重复
    unique_content = []
    seen_content = set()
    
    for part in content_parts:
        if part not in seen_content:
            unique_content.append(part)
            seen_content.add(part)
    
    return '\n\n'.join(unique_content)

def extract_article_images(element):
    """提取文章中的图片信息"""
    if not element:
        return []
    
    images = []
    
    for img in element.find_all('img'):
        img_src = img.get('data-src') or img.get('src') or img.get('data-original')
        if img_src and img_src.startswith('http'):
            alt_text = img.get('alt', 'image')
            images.append({
                "img_url": img_src,
                "alt_text": alt_text
            })
    
    return images

def convert_to_markdown(element):
    """将HTML元素转换为Markdown格式"""
    if not element:
        return ""

    markdown_lines = []
    processed_texts = set()  # 用于去重

    # 处理标题
    for i in range(1, 7):
        for h in element.find_all(f'h{i}'):
            text = h.get_text().strip()
            if text and text not in processed_texts:
                markdown_lines.append(f'{"#" * i} {text}\n')
                processed_texts.add(text)

    # 处理段落和图片
    for tag in element.find_all(['p', 'div', 'section', 'img']):
        if tag.name == 'img':
            img_src = tag.get('data-src') or tag.get('src') or tag.get('data-original')
            if img_src and img_src.startswith('http'):
                alt_text = tag.get('alt', 'image')
                markdown_lines.append(f'![{alt_text}]({img_src})\n')
        else:
            text = tag.get_text().strip()
            # 去重逻辑：只添加未处理过的文本
            if text and len(text) > 5 and text not in processed_texts:
                markdown_lines.append(f'{text}\n')
                processed_texts.add(text)

    # 处理列表
    for ul in element.find_all(['ul', 'ol']):
        for i, li in enumerate(ul.find_all('li'), 1):
            text = li.get_text().strip()
            if text and text not in processed_texts:
                prefix = f'{i}. ' if ul.name == 'ol' else '- '
                markdown_lines.append(f'{prefix}{text}\n')
                processed_texts.add(text)

    # 处理引用
    for blockquote in element.find_all('blockquote'):
        text = blockquote.get_text().strip()
        if text and text not in processed_texts:
            for line in text.split('\n'):
                line_text = line.strip()
                if line_text and line_text not in processed_texts:
                    markdown_lines.append(f'> {line_text}\n')
                    processed_texts.add(line_text)

    # 如果没有结构化内容，返回纯文本
    if not markdown_lines:
        return element.get_text().strip()

    # 清理多余的空行
    result = ''.join(markdown_lines).strip()
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)

    return result

def clean_filename(title):
    """清理文件名，移除不合法的字符"""
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename[:80] if len(filename) > 80 else filename or "无标题文章"

def save_single_article(article, account_name):
    """保存单篇文章为markdown文件"""
    save_dir = os.path.join(OUTPUT_DIR, clean_filename(account_name))
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{clean_filename(article['title'])}.md"
    filepath = os.path.join(save_dir, filename)

    markdown_content = f"""# {article['title']}

**公众号**: {account_name}  
**发布时间**: {article['publish_time']}  
**原文链接**: {article['link']}  

---

{article['content'] if article['content'] and article['content'] not in ["未获取", "获取内容失败"] else ""}"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"已保存: {filename}")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='微信爬虫最小化demo')
    parser.add_argument('--account', type=str, required=True, help='公众号名称')
    parser.add_argument('--count', type=int, default=10, help='爬取文章数量，默认10篇')
    parser.add_argument('--structured', action='store_true', help='返回结构化数据而不是保存Markdown文件')
    
    args = parser.parse_args()
    
    account_name = args.account
    max_articles = args.count
    
    print(f"开始爬取公众号: {account_name}")
    print(f"目标文章数量: {max_articles}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 搜索公众号
    accounts = search_account(account_name)
    if not accounts:
        print(f"未找到公众号: {account_name}")
        return
    
    # 使用第一个匹配的公众号
    selected_account = accounts[0]
    print(f"使用公众号: {selected_account['name']} (ID: {selected_account['fakeid']})")
    
    # 获取文章列表
    articles = get_articles_list(selected_account['fakeid'], selected_account['name'], max_articles)
    if not articles:
        print(f"{account_name} 未获取到文章")
        return
    
    print(f"\n开始获取 {len(articles)} 篇文章的内容...")
    saved_count = 0
    
    # 存储结构化数据结果
    structured_results = []
    
    # 获取并保存每篇文章
    for i, article in enumerate(articles, 1):
        print(f"获取第 {i}/{len(articles)} 篇: {article['title']}")
        
        if args.structured:
            # 获取结构化数据
            structured_data = get_structured_article_data(article['link'])
            structured_data['original_title'] = article['title']
            structured_data['original_date'] = article['publish_time']
            structured_results.append(structured_data)
            print(f"结构化数据获取完成: {structured_data['article_title']}")
        else:
            # 获取文章内容
            article['content'] = get_article_content(article['link'])
            if save_single_article(article, account_name):
                saved_count += 1
        
        # 添加延迟，避免请求过快
        if i < len(articles):
            time.sleep(random.uniform(2, 4))
    
    if args.structured:
        # 返回结构化数据
        print("\n结构化数据结果:")
        for i, result in enumerate(structured_results, 1):
            print(f"\n第 {i} 篇文章:")
            print(f"标题: {result['article_title']}")
            print(f"日期: {result['article_date']}")
            print(f"URL: {result['article_url']}")
            print(f"图片数量: {len(result['article_images'])}")
            print(f"内容预览: {result['article_content'][:200]}...")
        
        # 可以选择将结构化数据保存为JSON文件
        import json
        json_filename = f"{account_name}_structured_data.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(structured_results, f, ensure_ascii=False, indent=2)
        print(f"\n结构化数据已保存到: {json_filename}")
        return structured_results
    else:
        print(f"\n爬取完成！")
        print(f"成功保存文章数: {saved_count}/{len(articles)}")
        print(f"文件保存目录: {OUTPUT_DIR}")
        return None

if __name__ == "__main__":
    main()