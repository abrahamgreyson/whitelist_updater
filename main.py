"""
Author: abe<wechat:abrahamgreyson>
Date: 2024/6/13 16:40:14

程序入口，用于定期检查 IP 地址变化，并更新云提供商的白名单
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from update_whitelist.config.config import config
from update_whitelist.ip_fetcher import get_current_ip, load_cached_ip, cache_ip
from update_whitelist.updater import update_cloud_providers
from update_whitelist.logger import get_logger

logger = get_logger()


def has_ip_changed():
    """
    检查本级 IP 地址是否变化
    """
    try:
        current_ip = get_current_ip()
    except Exception as e:
        logger.error(f"取得本机 IP 出错: {e}")
        return False, None

    cached_ip = load_cached_ip()

    if current_ip != cached_ip:
        cache_ip(current_ip)
        return True, current_ip
    return False, current_ip


def check_and_update_ip():
    """
    检查 IP 地址是否变化，如果变化则更新云服务的白名单
    """
    try:
        ip_changed, current_ip = has_ip_changed()
        if ip_changed:
            logger.info(f"IP 地址已经更改：{current_ip}. 更新云服务白名单.")
            update_cloud_providers(current_ip, config)
            logger.info("云服务白名单更新成功.")
        else:
            logger.info("IP 地址没有更改，无需更新云服务白名单")
    except Exception as e:
        logger.error(f"更新云服务白名单出错: {e}")


def main():
    """
    启动定时任务
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(check_and_update_ip, 'interval', seconds=3)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()