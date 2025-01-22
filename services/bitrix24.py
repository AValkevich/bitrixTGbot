import requests


class Bitrix24:

    def __init__(self, webhook_create_task, webhook_add_comment):
        self.webhook_create_task = webhook_create_task
        self.webhook_add_comment = webhook_add_comment

    def create_task(self, title, description, responsible_id, deadline):
        method_url = f"{self.webhook_create_task}task.item.add"
        payload = {
            "fields": {
                "TITLE": title,
                "DESCRIPTION": description,
                "RESPONSIBLE_ID": responsible_id,
                "DEADLINE": deadline
            }
        }
        try:
            response = requests.post(method_url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("result"):
                return result
            else:
                print(
                    f"Ошибка при создании задачи: {result.get('error', 'Неизвестная ошибка')}"
                )
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке запроса: {e}")
            return None

    def add_comment(self, task_id, comment_text, author_id):
        method_url = f"{self.webhook_add_comment}task.commentitem.add"
        payload = {
            "taskId": int(task_id),
            "fields": {
                "POST_MESSAGE": comment_text,
                "AUTHOR_ID": int(author_id)
            }
        }
        try:
            response = requests.post(method_url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("result"):
                return result
            else:
                print(
                    f"Ошибка при добавлении комментария: {result.get('error', 'Неизвестная ошибка')}"
                )
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке запроса: {e}")
            print(f"URL: {method_url}")
            print(f"Payload: {payload}")
            return None
