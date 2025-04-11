import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class ClimkitAPI:
    """Class to interact with the Climkit API."""

    BASE_URL = "https://api.climkit.com/v1"

    def __init__(self, username, password, api_key):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.api_key = api_key
        self.session = None

    async def authenticate(self):
        """Authenticate with the Climkit API."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(f"{self.BASE_URL}/auth", headers=headers) as response:
                if response.status == 200:
                    _LOGGER.debug("Authentication successful.")
                    return True
                else:
                    _LOGGER.error("Authentication failed: %s", response.status)
                    raise Exception("Authentication failed")
        except aiohttp.ClientError as e:
            _LOGGER.error("Error during authentication: %s", e)
            raise

    async def get_site_id(self):
        """Retrieve the list of sites associated with the account."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(f"{self.BASE_URL}/sites", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sites", [])
                else:
                    _LOGGER.error("Failed to fetch sites: %s", response.status)
                    return []
        except aiohttp.ClientError as e:
            _LOGGER.error("Error fetching sites: %s", e)
            return []

    async def get_meter_list(self, site_id):
        """Retrieve the list of meters for a specific site."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(f"{self.BASE_URL}/sites/{site_id}/meters", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("meters", [])
                else:
                    _LOGGER.error("Failed to fetch meters: %s", response.status)
                    return []
        except aiohttp.ClientError as e:
            _LOGGER.error("Error fetching meters: %s", e)
            return []

    async def get_meter_data(self, site_id, meter_id):
        """Retrieve data for a specific meter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(f"{self.BASE_URL}/sites/{site_id}/meters/{meter_id}/data", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error("Failed to fetch meter data: %s", response.status)
                    return {}
        except aiohttp.ClientError as e:
            _LOGGER.error("Error fetching meter data: %s", e)
            return {}

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
