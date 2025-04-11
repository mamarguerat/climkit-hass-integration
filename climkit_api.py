import aiohttp

API_BASE = "https://api.climkit.io/api/v1"

class ClimkitAPI:
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.token = None
    self.session = aiohttp.ClientSession()

  async def authenticate(self):
    url = f"{API_BASE}/auth"
    payload = {"username": self.username, "password": self.password}
    async with self.session.post(url, json=payload) as resp:
      resp.raise_for_status()
      data = await resp.json()
      self.token = data.get("token")

  async def _get(self, endpoint):
    headers = {
      "Authorization": f"Bearer {self.token}",
      "Content-Type": "application/json"
    }
    async with self.session.get(f"{API_BASE}{endpoint}", headers=headers) as resp:
      resp.raise_for_status()
      return await resp.json()

  async def get_site_id(self):
    data = await self._get("/all_installations")
    if data and isinstance(data, list):
      return data[0].get("site_id")
    return None

  async def get_meter_list(self, site_id):
    return await self._get(f"/meter_info/{site_id}")

  async def get_meter_data(self, site_id, meter_id):
    return await self._get(f"/meter_data/{site_id}/{meter_id}")

  async def close(self):
    await self.session.close()
