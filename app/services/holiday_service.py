"""Holiday determination service using KASI (Korea Astronomy and Space Science Institute) API.

Detects weekends and statutory/substitute holidays to evaluate emergency department
pediatric patient surge risk levels (NORMAL / HIGH / CRITICAL).
"""

from __future__ import annotations

import datetime
from typing import Optional

import requests
import xmltodict

from app.config import settings
from app.schemas.emergency import HolidayInfo

KASI_HOLIDAY_URL = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"


KST = datetime.timezone(datetime.timedelta(hours=9))


class HolidayService:
    """Service to evaluate holiday status and surge risk."""

    @classmethod
    def get_holiday_info(
        cls,
        target_date: Optional[Union[datetime.date, datetime.datetime, str]] = None,
        api_key: Optional[str] = None,
        timeout: float = 5.0,
    ) -> HolidayInfo:
        """Determines whether the given date is a weekend or public holiday.

        Surge risk levels:
        - CRITICAL: Official statutory or substitute holiday (local clinics closed).
        - HIGH: Regular weekend (Saturday / Sunday).
        - NORMAL: Regular weekday.
        """
        if target_date is None:
            target_date = datetime.datetime.now(KST).date()
        elif isinstance(target_date, str):
            clean = target_date.replace("-", "").strip()
            target_date = datetime.datetime.strptime(clean, "%Y%m%d").date()
        elif isinstance(target_date, datetime.datetime):
            target_date = target_date.date()


        if api_key is None:
            api_key = settings.data_go_api_key

        weekday = target_date.weekday()  # 5: Saturday, 6: Sunday
        is_weekend = weekday in [5, 6]
        weekend_name = "토요일" if weekday == 5 else ("일요일" if weekday == 6 else None)
        target_str = target_date.strftime("%Y%m%d")

        holiday_data = {
            "date": target_str,
            "is_holiday": is_weekend,
            "holiday_name": weekend_name if is_weekend else "평일",
            "is_rest_day_special": False,
            "surge_risk_level": "HIGH" if is_weekend else "NORMAL",
        }

        if not api_key:
            return HolidayInfo(**holiday_data)

        params = {
            "serviceKey": api_key,
            "solYear": str(target_date.year),
            "solMonth": f"{target_date.month:02d}",
            "_type": "json",
            "numOfRows": "50",
        }

        try:
            res = requests.get(KASI_HOLIDAY_URL, params=params, timeout=timeout)
            if res.status_code == 200:
                raw_text = res.text.strip()
                if raw_text.startswith("<?xml"):
                    data = xmltodict.parse(raw_text)
                    body = data.get("response", {}).get("body", {})
                    items = body.get("items", {}).get("item", []) if body else []
                else:
                    data = res.json()
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])

                if isinstance(items, dict):
                    items = [items]

                for item in items:
                    locdate = str(item.get("locdate"))
                    is_holi = item.get("isHoliday") == "Y"
                    if locdate == target_str and is_holi:
                        holiday_data["is_holiday"] = True
                        holiday_data["is_rest_day_special"] = True
                        holiday_data["holiday_name"] = item.get("dateName", "법정공휴일")
                        holiday_data["surge_risk_level"] = "CRITICAL"
                        break
        except Exception:
            # On network timeout or API error, fallback to weekend evaluation
            pass

        return HolidayInfo(**holiday_data)


# Top-level functional alias
def get_kasi_holiday_info(
    target_date: Optional[datetime.date] = None,
    api_key: Optional[str] = None,
) -> HolidayInfo:
    """Functional wrapper for HolidayService.get_holiday_info."""
    return HolidayService.get_holiday_info(target_date=target_date, api_key=api_key)
