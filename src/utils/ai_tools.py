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


