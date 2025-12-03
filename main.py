from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.all import Plain, AstrBotConfig
import aiohttp


@register("newsnow", "YourName", "NewsNow热点新闻", "1.3.0", "获取各平台实时热点")
class NewsNowPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.command("news")
    async def news(self, event: AstrMessageEvent, source: str = "zhihu"):
        '''获取热点新闻。

        Args:
            source (str): 新闻源ID (如 zhihu, weibo, 36kr)。默认为 zhihu。
        '''

        # ==================== 1. API 地址检查 ====================
        base_url = self.config.get("api_url", "")
        if not base_url:
            # 如果地址为空，直接报错提示用户配置
            yield event.plain_result(
                "⚠️ 插件配置错误：NewsNow API 地址未配置。\n请前往 AstrBot 管理后台 -> 插件 -> NewsNow -> 配置页面填写 'api_url'。")
            return

        base_url = base_url.rstrip('/')

        # ==================== 2. 用户权限检查 ====================
        user_id = event.get_sender_id()  # 获取发送者ID (通常是字符串类型的QQ号)
        user_blacklist = self.config.get("user_blacklist", [])
        user_whitelist = self.config.get("user_whitelist", [])

        # 2.1 黑名单检查 (最高优先级)
        # 如果用户在黑名单中，直接静默返回，不予响应
        if user_id in user_blacklist:
            return

        # 2.2 白名单检查
        # 如果白名单不为空，且用户不在白名单中，静默返回
        # (如果白名单为空，则默认跳过此检查，允许所有人)
        if user_whitelist and user_id not in user_whitelist:
            return

        # ==================== 3. 群组权限检查 ====================
        current_group_id = event.message_obj.group_id

        # 判断是否为群聊消息 (group_id 存在且不为空)
        if current_group_id:
            group_whitelist = self.config.get("whitelist", [])

            # 需求：群组白名单为空时，不响应任何群组消息
            if not group_whitelist:
                return  # 白名单为空，直接忽略所有群消息

            # 需求：不在白名单内的群组不响应
            if current_group_id not in group_whitelist:
                return

        # ==================== 4. 新闻源检查 ====================
        allowed_sources = self.config.get("sources", [])
        if allowed_sources and source not in allowed_sources:
            yield event.plain_result(f"❌ 新闻源 '{source}' 未在配置中启用或不支持。")
            return

        # ==================== 5. 执行 API 请求 ====================
        api_url = f"{base_url}/api/s"
        params = {"id": source}

        yield event.plain_result(f"正在从 {source} 获取最新热点...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        yield event.plain_result(f"❌ 获取失败 (HTTP {resp.status})")
                        return

                    data = await resp.json()

                    if not data or "items" not in data:
                        yield event.plain_result(f"❌ 源 {source} 数据格式错误或不可用。")
                        return

                    items = data.get("items", [])
                    if not items:
                        yield event.plain_result("📭 该源当前没有新闻内容。")
                        return

                    # 构建回复消息
                    source_name = data.get("title", source)
                    msg = [
                        Plain(f"🔥 {source_name} 实时热点\n"),
                        Plain(f"------------------------------\n")
                    ]

                    # 限制显示前 15 条
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
                f"❌ 连接失败：无法连接到配置的 API 地址。\n当前地址: {base_url}\n请检查 Docker 是否运行以及网络连接。")
        except Exception as e:
            yield event.plain_result(f"❌ 发生内部错误: {str(e)}")