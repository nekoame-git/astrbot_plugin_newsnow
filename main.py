from astrbot.api.all import *
import aiohttp
import json


@register("newsnow", "YourName", "NewsNow热点新闻", "1.0.0", "获取各平台实时热点")
class NewsNowPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    # 定义指令 /news
    @filter.command("news")
    async def news(self, event: AstrMessageEvent, source: str = "zhihu"):
        '''获取热点新闻。

        Args:
            source (str): 新闻源ID，支持 zhihu(知乎), weibo(微博), 36kr, ithome(IT之家), baidu(百度) 等。默认为 zhihu。
        '''

        # 1. 从配置中获取 API 地址，如果没填则使用默认
        base_url = self.config.get("api_url", "http://192.168.124.8:12444").rstrip('/')
        timeout = self.config.get("timeout", 10)

        api_url = f"{base_url}/api/s"
        params = {"id": source}

        # 2. 发送提示消息
        yield event.plain_result(f"正在从 {source} 获取最新热点...")

        try:
            async with aiohttp.ClientSession() as session:
                # aiohttp 会自动处理 gzip 解压
                async with session.get(api_url, params=params, timeout=timeout) as resp:
                    if resp.status != 200:
                        yield event.plain_result(f"❌ 获取失败，API 返回状态码: {resp.status}")
                        return

                    # 解析 JSON
                    data = await resp.json()

                    # 检查数据有效性
                    if not data or "items" not in data:
                        yield event.plain_result(f"❌ 数据格式错误或源 {source} 不可用。")
                        return

                    items = data.get("items", [])
                    if not items:
                        yield event.plain_result("📭 当前没有获取到任何新闻。")
                        return

                    # 3. 构建漂亮的回复消息
                    # 获取源名称和更新时间
                    source_id = data.get("id", source)
                    updated_time = data.get("updatedTime", "")

                    # 构建消息链
                    msg = [
                        Plain(f"🔥 {source_id} 实时热点\n"),
                        Plain(f"------------------------------\n")
                    ]

                    # 取前 15 条，避免刷屏
                    for i, item in enumerate(items[:15], 1):
                        title = item.get("title", "无标题").strip()
                        url = item.get("url", "")

                        # 格式：1. 标题
                        #       链接
                        msg.append(Plain(f"{i}. {title}\n"))
                        if url:
                            msg.append(Plain(f"{url}\n"))
                        msg.append(Plain("\n"))  # 增加空行分隔

                    yield event.chain_result(msg)

        except aiohttp.ClientConnectorError:
            yield event.plain_result(
                f"❌ 连接失败：无法连接到 {base_url}。\n请检查 AstrBot 后台插件配置中的 API 地址是否正确。")
        except Exception as e:
            yield event.plain_result(f"❌ 发生未知错误: {str(e)}")