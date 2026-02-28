# https://learn.microsoft.com/en-gb/linkedin/consumer/integrations/self-serve/share-on-linkedin

# https://developer.linkedin.com/
# Create App

# https://www.linkedin.com/developers/apps/229251438/products
# Sign In with LinkedIn using OpenID Connect
# Share on LinkedIn

# Go to https://www.linkedin.com/developers/tools/oauth and create token
# Make sure to click all boxes to enable required access


from dotenv import load_dotenv

assert load_dotenv()

import json
import os

import requests


class LinkedinClient:
    def __init__(self):
        self.base_url = "https://api.linkedin.com/v2"

        api_token = os.getenv("LINKEDIN_API_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

        response = requests.get(f"{self.base_url}/userinfo", headers=self.headers)
        response.raise_for_status()
        response = response.json()
        self.author = f"urn:li:person:{response['sub']}"

    def create_post(self, text):
        payload = {
            "author": self.author,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        response = requests.post(
            f"{self.base_url}/posts", headers=self.headers, json=payload
        )
        response.raise_for_status()
        response = json.dumps(response.json())
        return response
