from io import BytesIO
import os
import requests


class Instagram:

    def __init__(
        self, base_path="https://graph.facebook.com/v19.0", notify_function=None
    ):
        self.base_path = base_path
        self.notify_function = (
            notify_function if notify_function else lambda message: print(f"{message}")
        )

    def generate_access_token(self, fb_exchange_token=None):
        """
        Generates an extended access token valid for 60 days

        Args:
            app_id (str): The App ID of the Facebook application.
            app_secret (str): The App Secret of the Facebook application.
            short_lived_token (str): The short-lived access token generated in Meta Business platform.

        Returns
            str: Long-lived access token
        """

        client_id = os.getenv("INSTAGRAM_CLIENT_ID", None)
        client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET", None)
        fb_exchange_token = os.getenv("INSTAGRAM_TOKEN", fb_exchange_token)

        if client_id is None or client_secret is None:
            raise Exception(
                "INSTAGRAM_CLIENT_ID o INSTAGRAM_CLIENT_SECRET must be defined"
            )

        url = f"{self.base_path}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "fb_exchange_token": fb_exchange_token,
        }

        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            if not "access_token" in response_data:
                raise Exception(
                    f"Long-lived access token couldn't be generated {response_data}"
                )

            return response_data["access_token"]
        except Exception as e:
            self.notify_function(f"Exception douring token generation: {str(e)}")
            raise

    def reel_upload(
        self,
        access_token: str,
        video_data: bytes,
        thumbnail_data: bytes,
        caption: str,
        user_id=None,
    ):
        """
        Upload new content to instagram feed

        Args:
            access_token (str): Long-lived access token
            video_data (bytes): Reel video byte data
            thumbnail_data (bytes): Thumbnail byte data
            caption (str): Post description
            user_id (_type_, optional): Instagram user id. Defaults to None.

        Returns:
            str: Instagram media id
        """
        user_id = os.getenv("INSTAGRAM_USER_ID", user_id)

        upload_url = f"{self.base_path}/{user_id}/media"
        files = {
            "video": ("video.mp4", BytesIO(video_data), "video/mp4"),
            "thumbnail": ("thumbnail.jpg", BytesIO(thumbnail_data), "image/jpeg"),
        }

        payload = {
            "media_type": "VIDEO",
            "caption": caption,
            "access_token": access_token,
        }

        try:
            response = requests.post(upload_url, data=payload, files=files)
            response_data = response.json()

            if "id" in response_data:
                return response_data["id"]
        except Exception as e:
            self.notify_function(f"Exception douring content uploading: {str(e)}")

        return None

    def publish_content(
        self,
        access_token: str,
        creation_id: str,
        user_id=None,
    ):
        """
        Publish uploaded content to instagram feed

        Args:
            access_token (str): Long-lived access token
            creation_id (str): Creation id returned by media upload
        """
        user_id = os.getenv("INSTAGRAM_USER_ID", user_id)

        publish_url = f"{self.base_path}/{user_id}/media_publish"
        publish_payload = {"creation_id": creation_id, "access_token": access_token}

        try:
            publish_response = requests.post(publish_url, data=publish_payload)
            publish_data = publish_response.json()

        except Exception as e:
            self.notify_function(f"Exception douring content publishing: {str(e)}")
