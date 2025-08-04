import asyncio
import logging
import psutil

logger = logging.getLogger("system_monitor")

# [TASK-ID: system_monitoring_init]


async def log_system_usage():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        logger.info(f"[MONITOR] CPU: {cpu}%, RAM: {ram}%")
        await asyncio.sleep(60)


# [TASK-ID: resource_alerting]
async def check_resource_limits(cpu_limit=90, ram_limit=90):
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        if cpu > cpu_limit or ram > ram_limit:
            logger.warning(
                f"[ALERT] Resource limit exceeded: CPU={cpu}%, RAM={ram}%"
            )
        await asyncio.sleep(60)
