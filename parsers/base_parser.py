import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import Logger
from Logger import MyLogger
from config import BASE_URL, USD_URL, PROXY_URL


class BasicParser:
    base_url = BASE_URL
    ua = UserAgent().random

    av_headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://cars.av.by",
        "priority": "u=1, i",
        "referer": "https://cars.av.by/",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "same-site",
        "user-agent": ua,
    }
    copart_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "access-control-allow-headers": "Content-Type, X-XSRF-TOKEN",
        "cache-control": "no-cache",
        "if-modified-since": "Mon, 26 Jul 1997 05:00:00 GMT",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": UserAgent().random,
        "x-requested-with": "XMLHttpRequest",
        # 'cookie': 'anonymousCrmId=502c4ba2-bf72-4d10-9994-18f51eccab08; ConstructorioID_client_id=d3da21ae-9127-4417-b031-1fc912a7fdbd; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CQNBgcAQNBgcAEsACBENBdFoAP_gAEPgACiQINJD7C7FbSFCwH5zaLsAMAhHRsAAQoQAAASBAmABQAKQIAQCgkAYFASgBAACAAAAICRBIQIECAAAAUAAQAAAAAAEAAAAAAAIIAAAgAEAAAAIAAACAIAAEAAIAAAAEAAAmAgAAIIACAAAgAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAQNVSD2F2K2kKFkPCmwXYAYBCujYAAhQgAAAkCBMACgAUgQAgFJIAgCIFAAAAAAAAAQEiCQAAQABAAAIACgAAAAAAIAAAAAAAQQAABAAIAAAAAAAAEAQAAIAAQAAAAIAABEhAAAQQAEAAAAAAAQAAA%22%2C%222~70.89.93.108.122.149.184.196.236.259.311.313.323.358.415.442.486.494.495.540.574.609.864.981.1029.1048.1051.1095.1097.1126.1205.1276.1301.1365.1415.1449.1514.1570.1577.1598.1651.1716.1735.1753.1765.1870.1878.1889.1958.1960.2072.2253.2299.2373.2415.2506.2526.2531.2568.2571.2575.2624.2677.2778~dv.%22%2C%2292B10883-BCCB-4835-9E4A-F4E1AA293EF3%22%5D%5D; lhnContact=c497a657-1abc-495b-b8ee-a4e69d9d12fe-22724-KZgGFFL; lhnContact=c497a657-1abc-495b-b8ee-a4e69d9d12fe-22724-KZgGFFL; OptanonAlertBoxClosed=2025-02-18T10:19:01.083Z; userCategory=RPU; _gcl_au=1.1.819497927.1739873943; QuantumMetricUserID=5122bc6e8a59aaceff19b375435b76fc; OAID=e2cf36cff7053e1927aebda7512c55af; _fbp=fb.1.1741459796480.810031795805533511; _ga=GA1.1.1660701916.1739873943; lhnStorageType=cookie; g2usersessionid=fde404c3ac97ffd921e5b375b9649014; userLang=ru; nlbi_242093=gpuFFB2J3wBCKULzie/jegAAAADTO2bQCZQJYyuixDidsXB9; timezone=Europe%2FMinsk; OAGEO=BY%7CHorad+Minsk%7CMinsk%7C220030%7C53.90005%7C27.5668%7C%7C017%7C%7CUnitary+Enterprise+A1%7CDSL; incap_ses_1288_242093=um0CfZVeFkS+dGrwXeXfEe/v2WcAAAAArsL93XofZI4YD55cij//0w==; incap_ses_519_242093=0QvZS5JIlFgJMk5M89szB32+2mcAAAAAmPGusw0vLVBysTPJt8LJIg==; incap_ses_323_242093=RKnCIiEK02IZzDtwG4d7BOHD2mcAAAAA8Tn38ygzkvkfL0XuUZLNCA==; incap_ses_687_242093=rMMdGRCkhnTOsJgRG7eICf3F2mcAAAAAvrv4clHw2bqyBJ7jD6y36A==; incap_ses_408_242093=xvUnWZ1WTmOBQgYhIYKpBTsU22cAAAAAa6toSRwTQruXVudVKJ3lLQ==; visid_incap_242093=42gLHtSXTq+xU7v4VQp/N4detGcAAAAAREIPAAAAAACAeB67AaesuOQJc5YiNK12q+cGwTFQFx3e; incap_ses_1855_242093=MgNTUQrEAi3dHBg5+0i+Gbsr22cAAAAAbW5s+594/xy/TEJVdSDM1w==; incap_ses_875_242093=i6mvDrOM+kxbO5PGGaAkDMIu22cAAAAArn7eY0k/E8uzC5QhCzGNLw==; _clck=1h0z4o8%7C2%7Cfud%7C1%7C1875; incap_ses_688_242093=6dQteLotA2Qyp4Jrl0SMCeDX22cAAAAArxFfqxH60DcJjf+BgKxiTA==; usersessionid=a464acc53ef4b4804afa8864eaa2ad5e; lhnRefresh=2612e1d9-5869-4065-9265-e4eab96c99c4; lhnRefresh=2612e1d9-5869-4065-9265-e4eab96c99c4; lhnJWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2aXNpdG9yIiwiZG9tYWluIjoiIiwiZXhwIjoxNzQyNTU0MDQxLCJpYXQiOjE3NDI0Njc2NDEsImlzcyI6eyJhcHAiOiJqc19zZGsiLCJjbGllbnQiOjIyNzI0LCJjbGllbnRfbGV2ZWwiOiJiYXNpYyIsImxobnhfZmVhdHVyZXMiOltdLCJ2aXNpdG9yX3RyYWNraW5nIjp0cnVlfSwianRpIjoiYzQ5N2E2NTctMWFiYy00OTViLWI4ZWUtYTRlNjlkOWQxMmZlIiwicmVzb3VyY2UiOnsiaWQiOiJjNDk3YTY1Ny0xYWJjLTQ5NWItYjhlZS1hNGU2OWQ5ZDEyZmUtMjI3MjQtS1pnR0ZGTCIsInR5cGUiOiJFbGl4aXIuTGhuRGIuTW9kZWwuQ29yZS5WaXNpdG9yIn19.3IJgtrLZ6Fx9PDBOKmpJbQ39on02X3MOGJ6t5hDZVpo; lhnJWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2aXNpdG9yIiwiZG9tYWluIjoiIiwiZXhwIjoxNzQyNTU0MDQxLCJpYXQiOjE3NDI0Njc2NDEsImlzcyI6eyJhcHAiOiJqc19zZGsiLCJjbGllbnQiOjIyNzI0LCJjbGllbnRfbGV2ZWwiOiJiYXNpYyIsImxobnhfZmVhdHVyZXMiOltdLCJ2aXNpdG9yX3RyYWNraW5nIjp0cnVlfSwianRpIjoiYzQ5N2E2NTctMWFiYy00OTViLWI4ZWUtYTRlNjlkOWQxMmZlIiwicmVzb3VyY2UiOnsiaWQiOiJjNDk3YTY1Ny0xYWJjLTQ5NWItYjhlZS1hNGU2OWQ5ZDEyZmUtMjI3MjQtS1pnR0ZGTCIsInR5cGUiOiJFbGl4aXIuTGhuRGIuTW9kZWwuQ29yZS5WaXNpdG9yIn19.3IJgtrLZ6Fx9PDBOKmpJbQ39on02X3MOGJ6t5hDZVpo; incap_ses_689_242093=Fl54RtYPEEvF93EMFtKPCbb122cAAAAABWWT6z1gvV73vwFZgM11Nw==; g2app.search-table-rows=20; incap_ses_878_242093=AbufCHvq1QpAxvNfjEgvDBAa3GcAAAAAczGGzL7MvIHSFQz95Px7SA==; G2JSESSIONID=A0422994A132096285C3DCFCA1914ACE-n1; incap_ses_686_242093=02HbTL9QQlsveiFwnCmFCfxk3GcAAAAAB36DYggaJ+RNCtBIiK58kg==; incap_ses_1784_242093=8AxXaFrZZi1rndenFQvCGD1p3GcAAAAAGmAwqfmdOXAtkaNBTke8Zg==; lhnAutoInviteShown=true; lhnAutoInviteShown=true; incap_ses_767_242093=fwcERlT3cWceDCWdoO6kCnxs3GcAAAAAxHKlymY7gOtlFWvtLHiYtQ==; reese84=3:Dtho1fcquZhQVfkLLd3/iA==:obX5phx99hk+EnRXV1ndNsOnH1l3rNcmnnrG134/ykn+mzCqMALj4NnGtWh/yVbWEqYzfGWG8oyhSA8jhUlGHh3VDTx1zVNPR4xoFWyZd6X6MMqByyVZp0nZ7uRWA+tloByDwmIX3iH65NSsKJp8TAdy77ge7iU+jashOrjK6sJN5vnkaxJh3wHrnRVVVIhTzfIHh5uo+sAbp+dcCYelbmpCnCS7ph/EbiB8ac8AzGc0A5XhvRSYBTX+T7sQoaOD146jlzRP3iDG+LbmC6C6jN+lkqKPj0dFcGAVHa6j1pte7LfyRvHcCL8b9+7zg5isRZ2SLRl02DCY7RFqG1rd3PWrR4zxx7fHwf0x6hB0kAD1eLq/Bii3e+NE/XjnV6ajDdsLnvy8U11e5QNST8giXHlgfxAmRR+odvFRon4jdUHz1+FCUO1wDpvBcICYGY1nK8UCyBAB9yC4GX7Rv12xbw==:guCGGdszhNiwixFjdl7MujNMFRqUhlPMsLdpB+/a+5w=; nlbi_242093_2147483392=LK1GIvAXhVr8JZTjie/jegAAAADOc3u3C6vFvK3O9PFYUI+B; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Mar+20+2025+22%3A33%3A22+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202403.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e8993d0-50d3-4134-a211-8d3c2bf70f71&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0002%3A1%2CC0003%3A1%2CC0001%3A1%2CC0004%3A1&geolocation=PL%3B14&AwaitingReconsent=false; copartTimezonePref=%7B%22displayStr%22%3A%22GMT%2B3%22%2C%22offset%22%3A3%2C%22dst%22%3Afalse%2C%22windowsTz%22%3A%22Europe%2FMinsk%22%7D; fs_lua=1.1742499202614; fs_uid=#o-76DP-eu1#5da23651-3c20-4a22-b19b-2125b38e0c7f:122d04db-e8c4-4d11-947b-c4f487f444dc:1742498128899::2#/1774034132; _uetsid=b2551000057811f096425d8c4517e736; _uetvid=c35ed8b0ede111ef98f093688546df36; __gads=ID=cf5ad59ad3ace006:T=1741459885:RT=1742499205:S=ALNI_MZjArYOTIPAt4LMHvt0LKGxcqTQKw; __gpi=UID=000010576a3d7728:T=1741459885:RT=1742499205:S=ALNI_Mat39uljX_Mo2AZpyUHpZ9KIZ29bQ; __eoi=ID=a125d77db2fd6c4c:T=1741459885:RT=1742499205:S=AA-AfjYMyrazVKWOueGYhyDege3C; FCNEC=%5B%5B%22AKsRol-JmsYd8q79GGBOQr7YNBdYlQ1Gv8C30JZN8mQsRSsW-QEZRJhG9i5rrwMItIG8hX34gTooTmY1sJuINBlc8eHa_slC1aOqM8dYV8vUB5bRW2odGlEHV7qnUZQ4DAKBp96-Ja4gK5h2kfefX75EubpjS4aagA%3D%3D%22%5D%5D; _clsk=1utiy8l%7C1742499233321%7C6%7C0%7Cv.clarity.ms%2Fcollect; _ga_VMJJLGQLHF=GS1.1.1742498130.15.1.1742499243.18.0.0',
    }

    def __init__(self):
        self._session: aiohttp.ClientSession = None
        self.logger: Logger = MyLogger().get_logger()

    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_json(
        self,
        data: str = None,
        usd_url: bool = False,
    ):
        url = USD_URL if usd_url else f"{self.base_url}{data}"
        async with self._session.get(
            url, ssl=False, headers=self.av_headers
        ) as response:
            return await response.json()

    async def get_not_generation_json(self, url: str):
        async with self._session.get(
            url, ssl=False, headers=self.av_headers
        ) as response:
            return await response.json()

    async def get_cars(self, brand_id: int, model_id: int, generation_id: int | None):
        generation = {"name": "generation", "value": generation_id}
        page = 1
        results = []

        while True:
            json_data = {
                "page": page,
                "properties": [
                    {
                        "name": "brands",
                        "property": 6,
                        "value": [
                            [
                                {"name": "brand", "value": brand_id},
                                {"name": "model", "value": model_id},
                            ],
                        ],
                    },
                    {
                        "name": "price_currency",
                    },
                ],
                "sorting": 1,
            }
            if generation_id:
                json_data["properties"][0]["value"][0].append(generation)

            async with self._session.post(
                "https://api.av.by/offer-types/cars/filters/main/apply",
                ssl=False,
                headers=self.av_headers,
                json=json_data,
            ) as response:
                data = await response.json()

            results.append(data)

            page_count = data.get("pageCount", 1)
            if page >= page_count:
                break
            page += 1

        return results

    async def get_copart_json(self, copart_url: str, referer: str, proxy: bool):
        async with self._session.get(
            "https://www.copart.com/", ssl=False, headers=self.copart_headers
        ) as response:
            cookies = response.cookies

        self.copart_headers["referer"] = referer
        try:
            async with self._session.get(
                copart_url,
                ssl=False,
                headers=self.copart_headers,
                cookies=cookies,
                proxy=PROXY_URL if proxy else None,
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.warning(e)
            return False

    async def get_iaai_json(self, iaai_url: str):
        try:
            async with self._session.get(
                iaai_url,
                ssl=False,
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.warning(e)
            return False

    async def get_iaai_engine(self, iaai_url: str):
        # надо мб прокси или через селениум но там капча
        try:
            async with self._session.get(iaai_url, ssl=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                engine = soup.find("span", {"id": "ingine_image"}).text.strip()
                return engine
        except Exception as e:
            self.logger.warning(e)
            return False

    async def close_session(self):
        if self._session is not None:
            await self._session.close()

    async def get_current_curse(self):
        current_curse_data = await self.get_json(usd_url=True)
        return current_curse_data["Cur_OfficialRate"]
