from nonebot import MessageSegment
import random
import datetime
from loguru import logger
from PIL import Image
from .constant import PIG_HUB_PATH, PIGINFO_PATH, TODAY_PATH
from .util import async_fetch_pig_data, find_image_file, load_json, save_json
from hoshino import Service
from hoshino.util import pic2b64
from hoshino.typing import CQEvent, HoshinoBot

sv = Service(
    "今天是什么小猪",
    enable_on_default=True,
    help_="今日小猪 - 抽取今天属于你的小猪\n随机小猪 - 从PigHub随机获取一张猪猪图",
)
# 载入小猪信息
PIG_LIST = load_json(PIGINFO_PATH, [])
if not PIG_LIST:
    logger.error("猪圈空荡荡，请检查资源文件！")


@sv.scheduled_job("cron", hour="0", minute="0")
async def auto_refresh_pig_data():
    try:
        data = await async_fetch_pig_data("https://pighub.top/api/all-images")
        if data and data.get("images"):
            save_json(PIG_HUB_PATH, data)
            logger.success(f"成功从 PigHub 刷新 {len(data['images'])} 头猪猪")
        else:
            logger.warning("PigHub 中找不到猪猪，未能刷新数据。")
    except Exception as e:
        logger.error(f"从PigHub中获取猪猪失败: {e}")


@sv.on_fullmatch("刷新小猪")
async def refresh_pig_data(bot: HoshinoBot, ev: CQEvent):
    try:
        data = await async_fetch_pig_data("https://pighub.top/api/all-images")
        if data and data.get("images"):
            save_json(PIG_HUB_PATH, data)
            msg = f"成功从 PigHub 刷新 {len(data['images'])} 头猪猪"
        else:
            msg = "刷新失败，PigHub 中找不到猪猪。"
        await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, f"刷新失败，无法从PigHub获取数据。{e}")


@sv.on_fullmatch("随机小猪")
async def send_random_pig(bot: HoshinoBot, ev: CQEvent):
    data = load_json(PIG_HUB_PATH, {})
    pig_images = data["images"]
    pig = random.choice(pig_images)
    image_url = "https://pighub.top/data/" + pig["thumbnail"].split("/")[-1]
    await bot.send(ev, MessageSegment.image(image_url))


# 主函数
@sv.on_fullmatch("今日小猪")
async def send_today_pig(bot: HoshinoBot, ev: CQEvent):
    today_str = datetime.date.today().isoformat()
    user_id = str(ev.user_id)

    # 读取今日缓存
    today_cache = load_json(TODAY_PATH, {"date": "", "records": {}})

    # 检查日期，如果不是今天，则清空记录
    if today_cache.get("date") != today_str:
        today_cache = {"date": today_str, "records": {}}

    user_records = today_cache["records"]

    # 如果用户今天已经抽过，直接发送结果
    if user_id in user_records:
        pig = user_records[user_id]
    else:
        pig = random.choice(PIG_LIST)
        user_records[user_id] = pig
        save_json(TODAY_PATH, today_cache)
    msg = (
        "今日你是："
        + pig["name"]
        + MessageSegment.image(pic2b64(Image.open(find_image_file(pig["id"]))))
        + "\n"
        + pig["description"]
        + "\n分析："
        + pig["analysis"]
    )

    await bot.send(ev, msg)
