import threading
import queue
import requests
from nids.config.settings import settings
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class NotificationDispatcher:
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._worker = threading.Thread(target=self._process_queue, daemon=True)
        self._worker.start()

    def dispatch(self, alert_id: int, alert_type: str, severity: str, src_ip: str, detail: str):
        message = f"[{severity}] ALERT #{alert_id} | {alert_type} terdeteksi dari {src_ip} ? {detail}"
        logger.warning(message)

        if settings.slack_webhook_url:
            slack_message = {
                "text": f"?? *{severity}* | {alert_type}\n"
                        f"Source: {src_ip}\n"
                        f"Detail: {detail}\n"
                        f"Alert ID: #{alert_id}"
            }
            self._queue.put(slack_message)

    def _process_queue(self):
        while True:
            message = self._queue.get()
            try:
                response = requests.post(settings.slack_webhook_url, json=message, timeout=3)
                if response.status_code == 200:
                    logger.info("Slack notification sent successfully")
                else:
                    logger.warning(f"Slack notification failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Slack notification error: {e}")
            finally:
                self._queue.task_done()
