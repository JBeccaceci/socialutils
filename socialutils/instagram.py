from io import BytesIO
import os
import time
import requests


class Instagram:

    def __init__(
        self, base_path="https://graph.facebook.com/v22.0", notify_function=None
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
            "video": ("video.mp4", video_data, "video/mp4"),
            "thumbnail": ("thumbnail.jpg", thumbnail_data, "image/jpeg"),
        }

        payload = {
            "media_type": "REELS",
            "caption": caption,
            "access_token": access_token,
        }

        try:
            response = requests.post(upload_url, data=payload, files=files)
            response_data = response.json()

            if not "id" in response_data:
                raise Exception(f"Uploaded content error {response_data}")

            return response_data["id"]
        except Exception as e:
            self.notify_function(f"Exception douring content uploading: {str(e)}")
            raise

    def publish_content(
        self, access_token: str, creation_id: str, user_id=None, is_draft: bool = False
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

        if is_draft:
            publish_payload["is_draft"] = "true"

        try:
            publish_response = requests.post(publish_url, data=publish_payload)
            publish_data = publish_response.json()
            return publish_data
        except Exception as e:
            self.notify_function(f"Exception douring content publishing: {str(e)}")

    def upload_reel(
        self,
        access_token: str,
        video_url: str,
        caption: str,
        cover_url: str = None,
        share_to_feed: bool = False,
        collaborators: list = None,
        audio_name: str = None,
        user_tags: list = None,
        location_id: str = None,
        thumb_offset: int = None,
        user_id=None,
    ):
        """
        Uploads a reel to Instagram using the Graph API.

        Args:
            access_token (str): Instagram user access token.
            user_id (str): Instagram user ID.
            video_url (str): URL of the reel video.
            caption (str): Caption for the reel.
            cover_url (str, optional): URL of the reel cover image.
            share_to_feed (bool, optional): Whether to share to feed.
            collaborators (list, optional): List of collaborator usernames.
            audio_name (str, optional): Custom audio name.
            user_tags (list, optional): List of user tags.
            location_id (str, optional): Location page ID.
            thumb_offset (int, optional): Thumbnail offset.

        Returns:
            dict: Response from the API.
        """
        user_id = os.getenv("INSTAGRAM_USER_ID", user_id)

        url = f"{self.base_path}/{user_id}/media"

        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": str(share_to_feed).lower(),
            "access_token": access_token,
        }

        if cover_url:
            payload["cover_url"] = cover_url
        if collaborators:
            payload["collaborators"] = ",".join(collaborators)
        if audio_name:
            payload["audio_name"] = audio_name
        if user_tags:
            payload["user_tags"] = ",".join(user_tags)
        if location_id:
            payload["location_id"] = location_id
        if thumb_offset is not None:
            payload["thumb_offset"] = thumb_offset

        try:
            response = requests.post(url, data=payload)
            response_data = response.json()

            if "id" not in response_data:
                raise Exception(f"Upload failed: {response_data}")

            media_id = response_data["id"]

            if self.wait_for_media_processing(media_id, access_token):
                return self.publish_content(access_token, media_id, user_id)
            else:
                raise Exception("Media processing timeout.")

        except Exception as e:
            print(f"Error uploading reel: {e}")
            return None

    def upload_image(self, access_token: str, url):
        """
        Upload image using instagram API

        Args:
            access_token (str): Instagram user access token.
            url (str): Image url

        Returns:
            str: Media id
        """
        user_id = os.getenv("INSTAGRAM_USER_ID", user_id)

        url = f"{self.base_path}/{user_id}/media"

        payload = {"image_url": url, "access_token": access_token}
        response = requests.post(url, data=payload)
        response_data = response.json()
        return response_data.get("id")

    def publish_carousel(self, access_token: str, media_ids, caption):
        """
        Publish carouse given an array of pre-load imagenes

        Args:
            access_token (str): Instagram user access token.
            media_ids (str[]): Pre-load images
            caption (str): Caption of the carousel

        Returns:
            str: Carousel id
        """
        user_id = os.getenv("INSTAGRAM_USER_ID", user_id)

        url = f"{self.base_path}/{user_id}/media"

        payload = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(media_ids),
            "access_token": access_token,
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        return response_data.get("id")

    def wait_for_media_processing(
        self, media_id: str, access_token: str, timeout=120, interval=5
    ):
        """
        Espera hasta que el video esté procesado antes de publicarlo.
        """
        url = f"{self.base_path}/{media_id}?fields=status_code&access_token={access_token}"
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = requests.get(url)
            data = response.json()

            if data.get("status_code") == "FINISHED":
                return True

            time.sleep(interval)

        return False
