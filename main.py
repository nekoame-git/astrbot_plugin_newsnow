from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.all import Plain  # 仅导入需要的组件
import aiohttp


@register("newsnow", "YourName", "NewsNow热点新闻", "1.0.0", "获取各平台实时热点")
class NewsNowPlugin(Star):
    # 修复点 1: __init__ 只接收 context
    def __init__(self, context: Context):
        super().__init__(context)
        # 注意：此时 self.config 可能还未注入，请勿在这里访问配置

    # 注册指令 /news
    @filter.command("news")
    async def news(self, event: AstrMessageEvent, source: str = "zhihu"):
        '''获取热点新闻。

        Args:
            source (str): 新闻源ID，支持 zhihu(知乎), weibo(微博), 36kr, ithome(IT之家), baidu(百度) 等。默认为 zhihu。
        '''

        # 修复点 2: 在指令执行时从 self.config 获取配置
        # 如果 self.config 为空（未注入），则使用默认值
        base_url = "http://192.168.124.8:12444"
        timeout = 10

        if hasattr(self, "config") and self.config:
            base_url = self.config.get("api_url", base_url).rstrip('/')
            timeout = self.config.get("timeout", timeout)

        api_url = f"{base_url}/api/s"
        params = {"id": source}

        # 发送提示消息
        yield event.plain_result(f"正在从 {source} 获取最新热点...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=timeout) as resp:
                    if resp.status != 200:
                        yield event.plain_result(f"❌ 获取失败，API 返回状态码: {resp.status}")
                        return

                    data = await resp.json()

                    if not data or "items" not in data:
                        yield event.plain_result(f"❌ 数据格式错误或源 {source} 不可用。")
                        return

                    items = data.get("items", [])
                    if not items:
                        yield event.plain_result("📭 当前没有获取到任何新闻。")
                        return

                    # 构建回复
                    source_id = data.get("id", source)
                    msg = [
                        Plain(f"🔥 {source_id} 实时热点\n"),
                        Plain(f"------------------------------\n")
                    ]

                    for i, item in enumerate(items[:15], 1):
                        title = item.get("title", "无标题").strip()
                        url = item.get("url", "")
                        msg.append(Plain(f"{i}. {title}\n"))
                        if url:
                            msg.append(Plain(f"{url}\n"))
                        msg.append(Plain("\n"))

                    yield event.chain_result(msg)

        except aiohttp.ClientConnectorError:
            yield event.plain_result(
                f"❌ 连接失败：无法连接到 {base_url}。\n请检查 AstrBot 后台插件配置中的 API 地址是否正确，并确保 Docker 容器网络互通。")
        except Exception as e:
            yield event.plain_result(f"❌ 发生未知错误: {str(e)}")