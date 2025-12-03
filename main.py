from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api.all import Plain, AstrBotConfig
from astrbot.api import logger
import aiohttp
import asyncio
import datetime


@register("newsnow", "YourName", "NewsNow热点新闻", "1.3.3", "获取各平台实时热点及定时推送")
class NewsNowPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def terminate(self):
        if hasattr(self, '_scheduler_task') and not self._scheduler_task.done():
            self._scheduler_task.cancel()

    async def _scheduler_loop(self):
        """分钟级定时任务循环"""
        while True:
            try:
                now = datetime.datetime.now()
                # 对齐到下一分钟的 00 秒
                delay = 60 - now.second
                await asyncio.sleep(delay)

                current_time = datetime.datetime.now().strftime("%H:%M")
                tasks = self.config.get("scheduled_tasks", [])

                if not tasks:
                    continue

                for task_str in tasks:
                    try:
                        parts = task_str.split('#')
                        if len(parts) != 3:
                            logger.warning(f"[NewsNow] 任务格式错误: {task_str}。请使用 '时间#完整ID#新闻源' 格式。")
                            continue

                        sched_time = parts[0].strip()
                        target_id = parts[1].strip()
                        source = parts[2].strip()
                        logger.info(
                            f"获取到定时推送任务，将在每日{sched_time}推送, 目标ID [{target_id}] 源 [{source}]")

                        if sched_time == current_time:
                            logger.info(f"[NewsNow] 执行定时推送: ID [{target_id}] 源 [{source}]")

                            # 获取新闻内容 (返回的是 list)
                            msg_list = await self._fetch_news(source)
                            if msg_list:
                                # 【关键修改】必须将 list 封装为 MessageChain 对象
                                chain_obj = MessageChain(msg_list)
                                await self.context.send_message(target_id, chain_obj)

                    except Exception as e:
                        logger.error(f"[NewsNow] 执行任务失败 ({task_str}): {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[NewsNow] 定时器循环出错: {e}")
                await asyncio.sleep(5)

    async def _fetch_news(self, source: str):
        """核心获取逻辑，返回消息组件列表 (List[Plain])"""
        base_url = self.config.get("api_url", "")
        if not base_url:
            return [Plain("⚠️ NewsNow API 地址未配置。")]

        base_url = base_url.rstrip('/')
        api_url = f"{base_url}/api/s"
        params = {"id": source}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        return [Plain(f"❌ 获取失败 (HTTP {resp.status})")]

                    data = await resp.json()
                    if not data or "items" not in data:
                        return [Plain(f"❌ 源 {source} 数据格式错误。")]

                    items = data.get("items", [])
                    if not items:
                        return [Plain("📭 该源当前没有内容。")]

                    source_name = data.get("title", source)
                    msg = [
                        Plain(f"🔥 {source_name} 实时热点\n"),
                        Plain(f"------------------------------\n")
                    ]

                    for i, item in enumerate(items[:15], 1):
                        title = item.get("title", "无标题").strip()
                        url = item.get("url", "")
                        msg.append(Plain(f"{i}. {title}\n"))
                        if url:
                            msg.append(Plain(f"{url}\n"))
                        msg.append(Plain("\n"))

                    return msg

        except Exception as e:
            return [Plain(f"❌ 请求错误: {str(e)}")]

    @filter.command("news_id")
    async def get_session_id(self, event: AstrMessageEvent):
        '''获取当前会话的完整ID，用于配置定时任务'''
        uid = event.unified_msg_id
        yield event.plain_result(f"🆔 当前会话的完整 ID 如下 (请复制到定时任务配置中):\n\n{uid}")

    @filter.command("news")
    async def news(self, event: AstrMessageEvent, source: str = "zhihu"):
        '''获取热点新闻'''
        user_id = event.get_sender_id()
        user_blacklist = self.config.get("user_blacklist", [])
        if user_id in user_blacklist: return

        user_whitelist = self.config.get("user_whitelist", [])
        if user_whitelist and user_id not in user_whitelist: return

        current_group_id = event.message_obj.group_id
        if current_group_id:
            group_whitelist = self.config.get("whitelist", [])
            if not group_whitelist: return
            if current_group_id not in group_whitelist: return

        allowed_sources = self.config.get("sources", [])
        if allowed_sources and source not in allowed_sources:
            yield event.plain_result(f"❌ 新闻源 '{source}' 未启用。")
            return

        yield event.plain_result(f"正在从 {source} 获取最新热点...")

        # 指令回复会自动处理 list，不需要封装 MessageChain
        msg_chain = await self._fetch_news(source)
        if msg_chain:
            yield event.chain_result(msg_chain)