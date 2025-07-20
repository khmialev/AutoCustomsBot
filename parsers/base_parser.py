import asyncio
import json

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import Logger
from Logger import MyLogger
from config import (
    BASE_URL,
    USD_URL,
    PROXY_URL,
    COPART_LOT_IMAGES_URL,
    BID_CARS_TRACKING_URL,
)
from parsers.selenium_hundler import DriverManager


class BasicParser:
    base_url = BASE_URL
    tracking_bid_cars_url = BID_CARS_TRACKING_URL
    ua = UserAgent().random
    copart_lot_images_url = COPART_LOT_IMAGES_URL
    slenium_driver = DriverManager(ua=ua)

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

    # может ебать голову из-за x-xsrf токена
    copart_main_page_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": ua,
        # 'cookie': 'g2usersessionid=194cd5e0f7b1804ca2b095e9dbeccf62; G2JSESSIONID=4B66099D486D8B31434DFA4F70439050-n1; visid_incap_242093=X9v212+ZQnyApty3J0Hhp55Q5WcAAAAAQUIPAAAAAAAgC+2srD1oH6/bfbzXaVaH; nlbi_242093=aYIKbROfnRemvTJjie/jegAAAABsP4dyd7GTmI2Wjo5OkP89; incap_ses_520_242093=ybzgOIbtPH7PDPZbQ2k3B59Q5WcAAAAAibkhC3NOzDbf5uWNLm6SXg==; userLang=en; anonymousCrmId=6655d269-1908-4774-89d6-2616cc14605e; timezone=Europe%2FMinsk; reese84=3:rcZJBbt1RFyHGrLf9MN9fw==:qw6VJj58eIvyJaISi5lHFK0gcGj3RZqGSO4GXhNaPusXaNhlWTgGbdUYryEE7iZ6ZWhCsTc1mDLovon1MQVolIuychlwzpUBd9wnKaxaSxFBaLn7sk+rM0wtz1TPgyvg6BKeF1lyR8RxDG0H8UOeI6DusaDrviQuT26lREEv1JS8c6G5i9CdaT0LkJkivXajSw4A4ke3TzHqL2qB9RVy5fsU3e0Nwg+q91qs1fmSJ78OhZOktq9/JNdCl3QaCDBqWW44U3hyG9DW8oxreNT6CBPOdZ6Tj+Gm78oKRoJQMMBwBrypvEPA/R4BM/5V22cPu3OyfnP0qqQ0kxhcKZDc9FUmiywBAWZ2r7so6g9POeoT55+3dlDHXcp/UDPjaHh7i09M+IDLWX1JJp3pWYZWVGuS8tYbenbCNEzyT4uISZatPXvQRYyxJ5QQbV3IJ52Yf0IysuvQZtDjS1vmvgO/Fa2smuzPA02bVRWbGj8g2zQ=:SeqW01z/IstWWfzgYHXw9BQBzXtfMiiSjwxB8h4OmnQ=; OAGEO=PL%7CMazowieckie%7CWarsaw%7C05-077%7C52.22977%7C21.01178%7C%7C022%7C%7CThe+Constant+Company+LLC%7CT1; usersessionid=a464acc53ef4b4804afa8864eaa2ad5e; OAID=3e6048a3d9ee919af82aad895b36ce54; lhnStorageType=cookie; lhnStorageType=cookie; lhnRefresh=79b845f8-69a0-4d17-8e41-53f6d860a498; lhnRefresh=79b845f8-69a0-4d17-8e41-53f6d860a498; lhnJWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2aXNpdG9yIiwiZG9tYWluIjoiIiwiZXhwIjoxNzQzMTY4NzgyLCJpYXQiOjE3NDMwODIzODIsImlzcyI6eyJhcHAiOiJqc19zZGsiLCJjbGllbnQiOjIyNzI0LCJjbGllbnRfbGV2ZWwiOiJiYXNpYyIsImxobnhfZmVhdHVyZXMiOltdLCJ2aXNpdG9yX3RyYWNraW5nIjp0cnVlfSwianRpIjoiODI3OTY2ODEtOWRkNi00MGRmLWFlNzMtN2RhMzc5ZDNmOTMwIiwicmVzb3VyY2UiOnsiaWQiOiI4Mjc5NjY4MS05ZGQ2LTQwZGYtYWU3My03ZGEzNzlkM2Y5MzAtMjI3MjQtSmxuRHNNMiIsInR5cGUiOiJFbGl4aXIuTGhuRGIuTW9kZWwuQ29yZS5WaXNpdG9yIn19.5NbUn87KS82lerFglZgSjXAGx65E9lKqevQi0VMOja0; lhnJWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2aXNpdG9yIiwiZG9tYWluIjoiIiwiZXhwIjoxNzQzMTY4NzgyLCJpYXQiOjE3NDMwODIzODIsImlzcyI6eyJhcHAiOiJqc19zZGsiLCJjbGllbnQiOjIyNzI0LCJjbGllbnRfbGV2ZWwiOiJiYXNpYyIsImxobnhfZmVhdHVyZXMiOltdLCJ2aXNpdG9yX3RyYWNraW5nIjp0cnVlfSwianRpIjoiODI3OTY2ODEtOWRkNi00MGRmLWFlNzMtN2RhMzc5ZDNmOTMwIiwicmVzb3VyY2UiOnsiaWQiOiI4Mjc5NjY4MS05ZGQ2LTQwZGYtYWU3My03ZGEzNzlkM2Y5MzAtMjI3MjQtSmxuRHNNMiIsInR5cGUiOiJFbGl4aXIuTGhuRGIuTW9kZWwuQ29yZS5WaXNpdG9yIn19.5NbUn87KS82lerFglZgSjXAGx65E9lKqevQi0VMOja0; lhnContact=82796681-9dd6-40df-ae73-7da379d3f930-22724-JlnDsM2; lhnContact=82796681-9dd6-40df-ae73-7da379d3f930-22724-JlnDsM2; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CQO7dIAQO7dIAEsACBENBiFoAP_gAEPgACiQINJD7C7FbSFCwD5zaLsAMAhHRsAAQoQAAASBAmABQAKQIAQCgkAYFASgBAACAAAAICRBIQIECAAAAUAAQAAAAAAEAAAAAAAIIAAAgAEAAAAIAAACAIAAEAAIAAAAEAAAmAgAAIIACAAAgAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAQNVSD2F2K2kKFkHCmwXYAYBCujYAAhQgAAAkCBMACgAUgQAgFJIAgCIFAAAAAAAAAQEiCQAAQABAAAIACgAAAAAAIAAAAAAAQQAABAAIAAAAAAAAEAQAAIAAQAAAAIAABEhAAAQQAEAAAAAAAQAAA%22%2C%222~70.89.93.108.122.149.184.196.236.259.311.313.314.323.358.415.442.486.494.495.540.574.609.864.981.1029.1048.1051.1095.1097.1126.1205.1276.1301.1365.1415.1449.1514.1570.1577.1598.1651.1716.1735.1753.1765.1870.1878.1889.1958.1960.2072.2253.2299.2373.2415.2506.2526.2531.2568.2571.2575.2624.2677.2778~dv.%22%2C%225A1352F8-73C9-468F-B5D0-20CA6E1901BE%22%5D%5D; OptanonAlertBoxClosed=2025-03-27T13:33:04.433Z; _fbp=fb.1.1743082384542.726500928889980026; userCategory=RPU; _gcl_au=1.1.1453935977.1743082386; _clck=zqkhzg%7C2%7Cfuk%7C1%7C1912; _ga=GA1.1.1130723028.1743082405; __gads=ID=251e1c450eabd3a5:T=1743083028:RT=1743083028:S=ALNI_MZ9IGtGoS8MOiKlsiySi61dvtYPuQ; __gpi=UID=00001072b87229d0:T=1743083028:RT=1743083028:S=ALNI_MYPP0EwcaoDwUbFuxD_RVAwidsHLA; __eoi=ID=5ff51e266cb1ab2e:T=1743083028:RT=1743083028:S=AA-AfjbRkUNU57vfokzcNwODuT_D; _ga_VMJJLGQLHF=GS1.1.1743082393.1.1.1743083026.57.0.0; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Mar+27+2025+16%3A45%3A09+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202403.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=f398a967-632a-4d3d-9f55-6968091db2dc&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0002%3A1%2CC0003%3A1%2CC0001%3A1%2CC0004%3A1&geolocation=PL%3B14&AwaitingReconsent=false; nlbi_242093_2147483392=q5SgPHCmHXjUkvGgie/jegAAAAAI6h9kJmFFHXMFZ9c1K9hD; fs_lua=1.1743083110032; fs_uid=#o-76DP-eu1#d564d5fc-903e-48b1-a031-8cba59e269bc:6b2da63e-2f44-4417-a20a-08e4fa3ee781:1743082385188::4#/1774618393; copartTimezonePref=%7B%22displayStr%22%3A%22GMT%2B3%22%2C%22offset%22%3A3%2C%22dst%22%3Afalse%2C%22windowsTz%22%3A%22Europe%2FMinsk%22%7D; _uetsid=04e039f00b1011f0b12619a0d28f0d1d; _uetvid=04e06ba00b1011f0935133c74986882c; _clsk=1iirubf%7C1743083111540%7C6%7C1%7Cl.clarity.ms%2Fcollect; FCNEC=%5B%5B%22AKsRol_HMBNEVHiRFbRxUZ3vVSOwHI7zYS5WYOt6I-gcKEqt-OlvTVq_i9k3OPwYGEQkn40HFNWXTDltp1SEzeZrVXqozShXCV2TrLz7pSUfLDBxjxIElGlw6aYU-4zQKPJOiT9lmPBFNlzR-FL9UTVhofmVLYmK7w%3D%3D%22%5D%5D',
    }
    copart_image_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "access-control-allow-headers": "Content-Type, X-XSRF-TOKEN",
        "content-type": "application/json",
        "origin": "https://www.copart.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua,
        "x-requested-with": "XMLHttpRequest",
    }

    copart_car_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": UserAgent().random,
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

    async def get_copart_lot_images(self, lot_id, referer: str, proxy: bool):
        async with self._session.get(
            "https://www.copart.com/", ssl=False, headers=self.copart_main_page_headers
        ) as response:
            self.logger.info(f"Get cookies status: {response.status}")
            cookies = response.cookies

        json_data = {
            "lotNumber": lot_id,
        }

        self.copart_image_headers["referer"] = referer
        try:
            async with self._session.post(
                url=self.copart_lot_images_url,
                ssl=False,
                headers=self.copart_image_headers,
                cookies=cookies,
                proxy=PROXY_URL if proxy else None,
                json=json_data,
            ) as response:
                data = await response.json()
                self.logger.info("Success get copart images json")
                return data
        except Exception as e:
            self.logger.warning(f"Error on get copart images json: {e}")
            return False

    async def get_through_selenium(self, copart_url: str):
        driver = await self.slenium_driver.get_driver(copart_url)
        try:
            json_text = driver.find_element("tag name", "pre").text
            return json.loads(json_text)
        except Exception as e:
            self.logger.warning(f"Error on get copart car json THROUGH SELENIUM : {e}")
            return False

    async def get_copart_json(self, copart_url: str, referer: str, proxy: bool):
        # async with self._session.get(
        #     "https://www.copart.com/", ssl=False, headers=self.copart_main_page_headers
        # ) as response:
        #     cookies = response.cookies
        #     print(cookies)

        # todo посомтри где взять эит куки
        # cookies = {
        #     "incap_ses_323_242093": "V/9iftmf5mtMs3K/HYd7BCsB62cAAAAAbLRG11EPY+qKsFNAAiVJcQ==",
        #     "incap_sh_242093": "jgHrZwAAAAA5Jg4tBgAIjoOsvwZvKcV7Tcz16NizBuHcnpVS",
        #     "g2usersessionid": "57546ecd068d15a49a663b44694f4609",
        #     "G2JSESSIONID": "01D76D014F98B849A668D59B6E6AD2A0-n1",
        #     "userLang": "en",
        #     "anonymousCrmId": "d0c5c31b-2b8c-45b9-af8a-60d8cd1f124b",
        #     "visid_incap_242093": "FpZY3cvnQzW4tqKkkVGgBCsB62cAAAAAQkIPAAAAAACAKGK7AUCwSL0aXiX2ndzLd0tYIzM2yA35",
        #     "nlbi_242093": "djWQeF85PRpaZ4hBie/jegAAAADUmdhObR1NFvT+o2H1DCss",
        #     "userCategory": "PU",
        #     "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Mar+31+2025+23%3A56%3A48+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202403.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=36a8eb5b-cf1d-45d0-98e1-603212354663&interactionCount=0&isAnonUser=1&landingPath=https%3A%2F%2Fwww.copart.com%2F&groups=C0002%3A0%2CC0003%3A0%2CC0001%3A1%2CC0004%3A0",
        #     "timezone": "Europe%2FMinsk",
        #     "copartTimezonePref": "%7B%22displayStr%22%3A%22GMT%2B3%22%2C%22offset%22%3A3%2C%22dst%22%3Afalse%2C%22windowsTz%22%3A%22Europe%2FMinsk%22%7D",
        #     "lhnStorageType": "cookie",
        #     "lhnContact": "82796681-9dd6-40df-ae73-7da379d3f930-22724-JlnDsM2",
        #     "nlbi_242093_2147483392": "EvZgQcfM5QIxw4j2ie/jegAAAACEhemVR4njbrHModJq9Nlv",
        #     "reese84": "3:WVyWXaR6nrD6fNYLF3BQvA==:OyNQPeHH5E74i1Ba/r8qBWKr+fjDLevmo1Mc3ZeYSfrgETdl4MgdWcBMwMkE+19snCylJvcAy6SgkdnIq4b+2uFIGJPVl5+kgxSvjmrTNmKBT659D6JJtuURoUU7GMNSGh0BOuxysEB3FrM6TW29s5wrxQJ2z8Fcmum5X/V4B80tVed9go8b5egDGlNdDdUZoG30ps1dN5DTKuqoV79BP7xhUsqqD9QaaJTliA5bKs8T204yR/RAqFQ9qIeCfcxJuhmtYg2nqita7hBzOM9DNk6/OlO1if2SX2eKMc6mj5P2ppZAW/uHM5W1YIz4VBRXXZcPFZnNqu04ykKkHwFip04dccINOdZw66Zdlc2g/vR/ZYhrqf0PnQkOdGOCQ0Ltg3ZE3EYEow3rWqnfncH/mR+EQ8HLT5OpwvmROGJOrjWXuZ6NkBZZbzbLeiQejZFCaXSsYPbq41oalsrDyVPqp9yZxeGHDg9lWtvEPZ4Df6s=:nlQcgTg2Pm6mit4LJHaIA661GJiokIxsAuseH67qUFA=",
        # }

        self.copart_car_headers["referer"] = referer
        try:
            async with self._session.get(
                copart_url,
                ssl=False,
                headers=self.copart_car_headers,
                # cookies=cookies,
                proxy=PROXY_URL if proxy else None,
            ) as response:
                data = await response.json()
                self.logger.info("Success get copart car json")
                return data
        except Exception as e:
            data = await self.get_through_selenium(copart_url=copart_url)
            await self.slenium_driver.close_driver()
            if data:
                return data
            self.logger.warning(f"Error on get copart car json: {e}")
            return False

    async def get_iaai_json(self, iaai_url: str, proxy: bool):
        try:
            async with self._session.get(
                iaai_url, ssl=False, proxy=PROXY_URL if proxy else None
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.warning(e)
            return False

    async def get_iaai_images(self, image_url: str, proxy: bool, payload: str):
        params = {"imageKeys": payload}
        try:
            async with self._session.get(
                image_url, ssl=False, proxy=PROXY_URL if proxy else None, params=params
            ) as response:
                return await response.json()
        except Exception as e:
            self.logger.warning(e)
            return False

    async def get_iaai_engine(self, iaai_url: str, proxy: bool):
        try:
            async with self._session.get(
                iaai_url, ssl=False, proxy=PROXY_URL if proxy else None
            ) as response:
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

    async def get_url_for_iaai(self, payload: str):
        await self.get_session()
        params = {
            "Keyword": payload,
        }
        try:
            async with self._session.get(
                "https://www.iaai.com/Search?", ssl=False, params=params
            ) as response:
                await self.close_session()
                return response.url
        except Exception as e:
            await self.close_session()
            self.logger.warning(e)
            return False

    async def get_data_tracking_bid_cars(
        self, brand: str, model: str, year_from: str, year_to: str
    ):
        await self.get_session()
        url = (
            self.tracking_bid_cars_url.replace("BRAND", brand)
            .replace("MODEL", model)
            .replace("YEAR_FROM", year_from)
            .replace("YEAR_TO", year_to)
        )
        async with self._session.get(url, ssl=False) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            table = soup.find("div", {"id": "search_area"}).find_all(
                "div", _class="item-horizontal lots-search "
            )
            for element in table:
                wrapper = element.find("div", _class="wrapper").find(
                    "span", _class="vin_title"
                )
                print(wrapper)

            print(soup)


# async def main():
#     a = BasicParser()
#     await a.get_session()
#     b = await a.get_copart_json(
#         copart_url="https://www.copart.com/public/data/lotdetails/solr/49845435",
#         proxy=False,
#         referer="https://www.copart.com/lot/49845435/clean-title-2024-bmw-228i-fl-miami-north",
#     )
#     await a.close_session()
#     print(b)
#
#
# asyncio.run(main())
