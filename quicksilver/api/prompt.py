import base64
import json
import os
import random
from io import BytesIO

import banana_dev as banana
import boto3
import requests
import structlog
from mastodon import Mastodon

import quicksilver.logconfig as logconfig
from quicksilver.prompt import Prompt
from quicksilver.repository import Prompts
from quicksilver.utils.lambdafn import api_handler

logger = structlog.get_logger(__name__)


@api_handler(model=Prompt)
def save_prompt(prompt):
    prompt = Prompts.save(prompt)
    return prompt


def update_picture(event, _):
    logconfig.configure()
    s3 = boto3.client("s3")

    event_body = json.loads(event["Records"][0]["body"])
    prompt_id = event_body["responsePayload"]

    logger.info("Updating picture", aws_event=event, prompt_id=prompt_id)
    prompt = Prompts.from_id(prompt_id)

    banana_api_key = os.environ["BANANA_API_KEY"]
    banana_model_key = os.environ["BANANA_MODEL_KEY"]
    s3_bucket_name = os.environ["AVATAR_BUCKET"]
    mastodon_client_secret = os.environ["MASTODON_CLIENT_SECRET"]
    mastodon_client_key = os.environ["MASTODON_CLIENT_KEY"]
    mastodon_access_token = os.environ["MASTODON_ACCESS_TOKEN"]

    try:
        response = banana.run(
            banana_api_key, banana_model_key, {"prompt": prompt.prompt}
        )
    except Exception:
        logger.error("Banana dev failure", response=response)
        raise RuntimeError("Banana dev failure")

    img_base64 = response["modelOutputs"][0]["image_base64"]
    img_bytes = base64.b64decode(img_base64)

    img_file = BytesIO(img_bytes)
    s3.upload_fileobj(img_file, s3_bucket_name, f"images/{prompt.id}.jpg")

    api = Mastodon(
        mastodon_client_key,
        mastodon_client_secret,
        mastodon_access_token,
        api_base_url="https://hachyderm.io",
    )
    api.account_update_credentials(
        avatar=img_bytes, avatar_mime_type="image/jpeg"
    )

    prompt.use()
    Prompts.save(prompt)


def pick_prompt(_, __):
    logconfig.configure()
    prompt_ids = Prompts.unused_ids()

    if len(prompt_ids):
        # Double the chances of recent prompts
        prompt_ids = (
            prompt_ids[: len(prompt_ids) // 2] * 2
            + prompt_ids[len(prompt_ids) // 2 :]
        )

        return random.choice(prompt_ids)
    else:
        raise RuntimeError("No available prompts")


@api_handler
def get_latest_prompts():
    logconfig.configure()
    prompts = Prompts.latest()

    return prompts
