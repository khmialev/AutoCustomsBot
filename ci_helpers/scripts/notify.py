import asyncio
import os
from datetime import datetime, timezone

from aiohttp import ClientResponseError, ClientSession

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PROJECT_NAME = os.getenv("CI_PROJECT_NAME", "Unknown")
COMMIT_BRANCH = os.getenv("CI_COMMIT_REF_NAME", "Unknown")
PIPELINE_SOURCE = (
    os.getenv("CI_PIPELINE_SOURCE", "Unknown").replace("_", " ").title()
)
PIPELINE_URL = os.getenv("CI_PIPELINE_URL", "")
PIPELINE_ID = os.getenv("CI_PIPELINE_ID", "N/A")

TEMPLATE_PATH = "ci_helpers/templates/telegram_message.tmpl"


def ensure_env_vars() -> None:
    missing = [
        var
        for var in [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "CI_PROJECT_NAME",
            "CI_COMMIT_REF_NAME",
            "CI_PIPELINE_SOURCE",
            "CI_PIPELINE_URL",
            "CI_PIPELINE_ID",
        ]
        if not os.getenv(var)
    ]

    if missing:
        print(f"ERROR: Missing required env vars: {', '.join(missing)}")
        exit(1)


def render_message() -> str:
    with open(TEMPLATE_PATH) as f:
        template = f.read()

    message = os.path.expandvars(template)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return (
        f"{message}\n"
        f"🧰 *Project:* {PROJECT_NAME}\n"
        f"🌿 *Branch:* {COMMIT_BRANCH}\n"
        f"🔗 *Pipeline source:* {PIPELINE_SOURCE}\n"
        f"🚦 *Pipeline:* [#{PIPELINE_ID}]({PIPELINE_URL})\n"
        f"⏰ *Timestamp:* {timestamp}\n"
    )


async def send_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}

    async with ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            try:
                resp.raise_for_status()
            except ClientResponseError as e:
                print(f"Failed to send Telegram message: {e}")
                raise


async def main():
    ensure_env_vars()
    message = render_message()
    await send_message(message)


if __name__ == "__main__":
    asyncio.run(main())
