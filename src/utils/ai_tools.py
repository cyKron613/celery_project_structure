from src.settings.config import settings
from openai import OpenAI
from loguru import logger

sdk_key = settings.OPENAI_API_KEY

client = OpenAI(
    api_key=sdk_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def chat(system_prompt:str = "", query:str = "", model:str = "qwen-max"):
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "system", "content": query})
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        logger.info(f'usage_token: {completion.usage.total_tokens}')
        result = completion.choices[0].message.content
    except Exception as e:
        logger.error(f"chat： {e}")
        raise e
    return result

def match_web_url_class_label(news_title, news_content):
    """
    匹配新闻标题和内容的分类标签
    :param news_title: 新闻标题
    :param news_content: 新闻内容
    :return: 分类标签
    """
    try:
        abstract = f"""
                        # 角色
                        专业航运新闻分类AI，具备精准的文本理解与分析能力，需严格结合新闻标题与正文内容，对各分类主题的相关度进行量化评估，最终依据得分确定新闻分类。

                        # 任务
                        1. 英翻中：完整、准确翻译新闻标题和正文内容，确保语义无偏差。
                        2. 相关度打分：针对每条分级分类准则对应的类别，根据标题与正文内容的关联程度进行打分（1-10分，10分为高度相关，1分为微弱相关，0分为不相关）。
                        3. 分类判定：基于各分类的得分结果，结合分级分类准则及异常处理规则，确定最匹配的分类。

                        # 分级分类准则（按优先级降序，打分时需优先参考此逻辑）

                        1. 满足以下任一特征时，对“船舶状态”类别打分：
                        - 船舶生命周期事件（建造/维修/拆解/下水）
                        - 船舶技术革新（脱碳技术/新型设计）
                        - 船东/船厂发布的订单信息
                        - 新型船舶技术规定
                        （符合特征越多、描述越详细，得分越高）

                        2. 满足以下任一特征时，对“船舶事故”类别打分：
                        - 涉及船舶实体损坏（碰撞/火灾/沉没）
                        - 造成人员伤亡或环境危害
                        （事故严重程度越高、描述越具体，得分越高）

                        3. 满足以下任一特征时，对“港口资讯”类别打分：
                        - 港口基础设施建设/改造
                        - 码头作业流程变更
                        - 港口管理政策调整
                        （内容与港口直接关联度越高，得分越高）

                        4. 满足以下任一特征时，对“地缘政治”类别打分：
                        - 国家间海事协议/制裁
                        - 军事部署/海上冲突
                        - 贸易政策（如关税）
                        - 国家政局变化
                        （涉及国家层面或国际间影响越大，得分越高）

                        5. 满足以下任一特征时，对“国际市场”类别打分：
                        - 国际物流贸易数据发布
                        - 邮轮旅游市场动态
                        - 非船舶类海事合同（如集装箱租赁）
                        - 海事金融/保险交易
                        - 跨国走私案件侦破
                        - 物流从业人员数量（如海员、司机）
                        - 环保组织/环保活动
                        - 捕捞
                        （与市场动态、交易行为、行业数据关联越紧密，得分越高）

                        6. 不满足上述任何特征时，“其他”类别得基础分（默认5分，若完全无关联可打0分）。

                        # 异常处理
                        当内容跨多个分类且得分接近或难以直接判定时：
                        - 按事件严重性优先（事故>政治>市场动态>船舶状态>港口资讯>其他）
                        - 按时效性优先（突发事故>常态运营；紧急政策>常规数据）
                        - 若上述条件仍无法区分，严格遵循分级分类准则的优先级顺序判定。

                        # 数据输入
                        标题：{news_title}
                        正文：{news_content}

                        # 输出规范
                        仅输出通过打分及规则判定后最匹配的分类标签（无需解释，标签范围：船舶状态、船舶事故、港口资讯、地缘政治、国际市场、其他）
                        """
        logger.info(f"根据文章标题和内容分类中...")

        info = chat(abstract)
        logger.info(f'分类结果: {info}')
        return info
    except Exception as e:
        logger.error(f"分类结果报错: {e}")
        return '其他'


# 微信热点草稿
def for_analyze_report(content_text):
    try:
        abstract = f"""
                # 上下文（Context）
                你是一位亲切且高效的航运新闻分析助手，你的职责是将用户提供的新闻内容进行专业且全面的中文分析，拒绝回答其他无关问题。

                # 目标（Objective）
                你的目标是根据航运信息，按照给出的分析角度进行专业的分析。

                # 风格（Style）
                你的回答风格应该是一位从业多年并且履历资深职业航运新闻分析师的风格。

                # 语气（Tone）
                你的语气应该是官方并且正式的。

                # 受众（Audience）
                你的受众会是船舶航运业的所有人员。

                # 响应（Response）


                # 航运新闻内容
                新闻内容：{content_text}


                # 分析角度

                ## 基础层面（基本面分析）
                从基本面角度进行分析，包括但不限于以下方面：
                - 市场需求和供给的变化
                - 经济指标（如GDP增长、通货膨胀率、就业率等）
                - 行业内主要企业的表现和财务状况
                - 政策和法规的影响

                ## 影响层面（外部因素分析）
                从外部因素角度进行分析，包括但不限于以下方面：
                - 国际贸易形势和政策变化
                - 自然灾害、气候变化等环境因素
                - 地缘政治事件及其影响
                - 全球供应链的变化

                ## 操作层面（战术和策略分析）
                从操作层面进行分析，包括但不限于以下方面：
                - 运输和物流策略的调整
                - 成本控制和效率提升措施
                - 竞争对手的战术和策略
                - 技术创新和应用

                ## 预测层面（未来趋势和策略制定）
                从预测层面进行分析，包括但不限于以下方面：
                - 行业未来的发展趋势
                - 可能的市场变化和应对策略
                - 长期投资和发展的建议
                - 风险评估和管理策略

                # 任务
                请你结合以上信息和分析角度，给出你的分析，要求分析内容不少于2千字, 如果文本。

        """
        logger.info(f"微信热点简报生成中...")
        info = chat(abstract)
        logger.info(f'分析简报生成完成, 分析字数: {len(info)}')
        return info
    except Exception as e:
        logger.error(f"for_analyze_report： {e}")
        raise


def match_web_url_class_label(news_title, news_content):
    try:
        abstract = f"""
                        # 角色
                        专业航运新闻分类AI，具备精准的文本理解与分析能力，需严格结合新闻标题与正文内容，对各分类主题的相关度进行量化评估，最终依据得分确定新闻分类。

                        # 任务
                        1. 英翻中：完整、准确翻译新闻标题和正文内容，确保语义无偏差。
                        2. 相关度打分：针对每条分级分类准则对应的类别，根据标题与正文内容的关联程度进行打分（1-10分，10分为高度相关，1分为微弱相关，0分为不相关）。
                        3. 分类判定：基于各分类的得分结果，结合分级分类准则及异常处理规则，确定最匹配的分类。

                        # 分级分类准则（按优先级降序，打分时需优先参考此逻辑）

                        1. 满足以下任一特征时，对“船舶状态”类别打分：
                        - 船舶生命周期事件（建造/维修/拆解/下水）
                        - 船舶技术革新（脱碳技术/新型设计）
                        - 船东/船厂发布的订单信息
                        - 新型船舶技术规定
                        （符合特征越多、描述越详细，得分越高）

                        2. 满足以下任一特征时，对“船舶事故”类别打分：
                        - 涉及船舶实体损坏（碰撞/火灾/沉没）
                        - 造成人员伤亡或环境危害
                        （事故严重程度越高、描述越具体，得分越高）

                        3. 满足以下任一特征时，对“港口资讯”类别打分：
                        - 港口基础设施建设/改造
                        - 码头作业流程变更
                        - 港口管理政策调整
                        （内容与港口直接关联度越高，得分越高）

                        4. 满足以下任一特征时，对“地缘政治”类别打分：
                        - 国家间海事协议/制裁
                        - 军事部署/海上冲突
                        - 贸易政策（如关税）
                        - 国家政局变化
                        （涉及国家层面或国际间影响越大，得分越高）

                        5. 满足以下任一特征时，对“国际市场”类别打分：
                        - 国际物流贸易数据发布
                        - 邮轮旅游市场动态
                        - 非船舶类海事合同（如集装箱租赁）
                        - 海事金融/保险交易
                        - 跨国走私案件侦破
                        - 物流从业人员数量（如海员、司机）
                        - 环保组织/环保活动
                        - 捕捞
                        （与市场动态、交易行为、行业数据关联越紧密，得分越高）

                        6. 不满足上述任何特征时，“其他”类别得基础分（默认5分，若完全无关联可打0分）。

                        # 异常处理
                        当内容跨多个分类且得分接近或难以直接判定时：
                        - 按事件严重性优先（事故>政治>市场动态>船舶状态>港口资讯>其他）
                        - 按时效性优先（突发事故>常态运营；紧急政策>常规数据）
                        - 若上述条件仍无法区分，严格遵循分级分类准则的优先级顺序判定。

                        # 数据输入
                        标题：{news_title}
                        正文：{news_content}

                        # 输出规范
                        仅输出通过打分及规则判定后最匹配的分类标签（无需解释，标签范围：船舶状态、船舶事故、港口资讯、地缘政治、国际市场、其他）
                        """
        logger.info(f"根据文章标题和内容分类中...")

        info = chat(abstract)
        logger.info(f'分类结果: {info}')
        return info
    except Exception as e:
        logger.error(f"分类结果报错: {e}")
        return '其他'


# 100字简要概括
def for_simple_analyze_report(content_text):
    try:
        abstract = f"""
                    # 角色
                    你是一位高效的新闻摘要助手，专门负责快速提炼信息核心，为用户提供简洁明了的新闻概览。
                    
                    ## 技能
                    ### 技能1：快速阅读理解
                    - 能够迅速浏览大量新闻文章，准确把握文章主旨、关键信息及细节。
                    - 理解并处理多种新闻体裁，包括政治、经济、科技、娱乐等领域。
                    
                    ### 技能2：精准摘要生成
                    - 根据文章内容，自动生成简洁、全面的摘要，确保包含最重要的事实和亮点。
                    - 保持摘要的客观性和中立性，避免添加个人意见或偏见。
                    
                    ### 技能3：适应多样格式
                    - 能够根据用户需求调整摘要长度和格式，无论是简短的几句话概要还是较为详细的段落总结。
                    - 支持为不同媒介定制摘要，如社交媒体分享、邮件通报或口头汇报要点。
                    
                    ## 文章内容
                    {content_text}
                    
                    ## 限制
                    - 输出的摘要以纯中文文字格式。
                    - 输出的内容应能够直接作为新闻的摘要。
                    - 输出的内容在100字左右
                    - 输出时请认真校对原文中出现的公司名称，不要进行混淆。
                """
        logger.info(f"根据文章内容生成摘要中...")
        info = chat(abstract)
        logger.info(f'摘要生成完成, 摘要字数: {len(info)}')
        return info
    except Exception as e:
        logger.error(f"for_simple_analyze_report： {e}")
        raise


def report_for_en(content_text):
    try:
        abstract = f"""
                请将该中文摘要翻译成英文，要求保持格式一致：{content_text}
        """
        logger.info(f"根据文章摘要生成英文分析简报中...")
        info = chat(abstract)
        logger.info(f'英文分析简报生成完成, 分析字数: {len(info)}')
        return info
    except Exception as e:
        logger.error(f"report_for_en： {e}")
        raise


def translate_title(title_text, type):
    try:
        if title_text is None:
            raise ValueError("title returned None, which is not allowed")
        if type == "zh":
            logger.info(f"根据文章标题生成英文翻译中...")
            abstract = f"""
                        请将以下海洋航运业的新闻标题翻译为英文新闻标题: {title_text}。
                        要求：
                        返回的结果仅仅是英文新闻的标题不要多余的字眼，不要出现例如"标题是"，"翻译是"类似的表述
            """
        else:
            # type == "en"
            logger.info(f"根据文章标题生成中文翻译中...")
            abstract = f"""
                        请将以下海洋航运业的新闻标题翻译为中文新闻标题: {title_text}。
                        要求：
                        返回的结果仅仅是中文新闻的标题不要多余的字眼，不要出现例如"标题是"，"翻译是"类似的表述
            """
        info = chat(abstract)
        logger.info(f"根据文章标题生成翻译完成, 翻译字数: {len(info)}")
        return info
    except Exception as e:
        logger.error(f"translate_title： {e}")
        raise


def translate_content(content_text, type):
    try:
        if content_text is None:
            raise ValueError("content returned None, which is not allowed")
        if type == "zh":
            logger.info(f"根据文章内容生成英文翻译中...")
            abstract = f"""
                        请将以下海洋航运业的新闻内容翻译为英文新闻内容: {content_text}
                        要求返回的结果
                        1. 仅有英文新闻内容
                        2. 不要出现例如：英文新闻内容是:...，英文翻译是:... 类似的表述。
            """
        else:
            logger.info(f"根据文章内容生成中文翻译中...")
            abstract = f"""
                        请将以上海洋航运业的新闻内容翻译为中文新闻内容: {content_text}。
                        要求返回的结果
                        1. 仅有中文新闻内容
                        2. 不要出现例如：中文新闻内容是:...，中文翻译是:... 类似的表述。
            """
        info = chat(abstract)
        logger.info(f'新闻内容翻译完成, 翻译字数: {len(info)}')
        return info
    except Exception as e:
        logger.error(f"translate_content： {e}")
        raise


def catch_hot_key_words(content_text, title_text):
    # 根据 原文正文 和 原文标题 提取关键字
    try:
        abstract = f"""
                    请根据以下海洋航运业的新闻内容，标题进行专业的分析
                    ## 新闻内容
                    {content_text}

                    ## 新闻标题
                    {title_text}

                    ## 分析要求 & 限制
                    - 得到三个航运相关的英文关键字。
                    - 只返回一个元组不需要多余的文字。
                    ## 返回示例
                    ("Containers", "Singapore", "Safety")
        """
        logger.info(f"根据文章内容和标题提取关键字中...")
        info = chat(abstract)
        logger.info(f'关键字内容: {info}')
        return info
    except Exception as e:
        logger.error(f"catch_hot_key_words： {e}")
        raise


# 过滤国内外对中国不良言论的新闻
def llm_filter_high_risk_news(content_title:str, content_text:str):
    sys_pmt = """
        你是一个严格的内容安全过滤器。你的任务​​不是修改或重写​​，而是基于以下​​绝对标准​​，对提供的国际新闻内容进行二元判断：​"直接过滤"或 ​​"允许通过"​。无需提供解释，只需给出判定结果。
    """
    query_prompt = f"""
    新闻标题： {content_title}
    新闻内容： {content_text}

    请判断以上新闻标题或内容是否涉及中国的不良言论

    ## 过滤（判断）标准
    1. 新闻政治方向：
    - 必须符合习近平新时代中国特色社会主义思想
    - 坚定维护"一国两制"方针
    - 积极宣传中华民族伟大复兴进程
    - 客观反映社会主义现代化建设成就
    2. 判断新闻是否涉及敏感话题（如：语言轻蔑、歪曲事实、隐晦暗指、诋毁辱骂、色情暴力、恐怖主义、极端主义、重大谣言、仇恨言论、违法内容等）
        ，如有则标记为【直接过滤】。
    3. 如果新闻主要是政治中立，则可以标记为【允许通过】。
    4. 严格排除【直接过滤】：
    - 任何含西方意识形态偏见的内容
    - 对中国特色社会主义制度的质疑
    - 涉及台湾、香港、澳门的不实表述
    - 任何形式的"历史虚无主义"内容
    - 任何形式的西方视角言论
    ## 重要说明：​​
        【允许通过】不代表认同其观点，后续可能由编辑进行平衡报道处理或加工
        ，但这已超出你的职责范围。你只需严格守住内容安全性。
    ## 输出：
        输出 ​​【直接过滤】​或者 ​​【允许通过】​​。
        不要输出任何其他内容。
    """
    try:
        result = chat(sys_pmt, query_prompt, model="qwen3-235b-a22b-instruct-2507")
        return result
    except Exception as e:
        logger.error(f"llm_filter_high_risk_news： {e}")
        return "【直接过滤】"
