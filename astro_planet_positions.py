#!/usr/bin/env python3
"""
Compute ecliptic longitudes for major solar system bodies using Swiss Ephemeris.

Fixes:
- Converts local time to UTC before calling swe.julday (swe.julday expects UT).
- Uses full fractional hour (including minutes/seconds/microseconds).
- Handles return values and errors from swe.calc_ut.
"""

from datetime import datetime
import pytz
import swisseph as swe

def utc_fractional_hour(dt):
    """Return fractional hour (UT) for a timezone-aware datetime."""
    dt_utc = dt.astimezone(pytz.UTC)
    return (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )

def zodiac_sign_name(deg):
    """Return zodiac sign name and degree within sign for an ecliptic longitude in degrees."""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    deg = deg % 360.0
    index = int(deg // 30)
    deg_in_sign = deg - index * 30
    return signs[index], round(deg_in_sign, 2)

def main():
    # 设置出生时间和地点（示例）
    birth_date_local = datetime(1997, 8, 25, 20, 0)  # 1997-08-25 20:00 local (Asia/Shanghai)
    timezone = pytz.timezone('Asia/Shanghai')
    birth_date_local = timezone.localize(birth_date_local)

    # 北京经纬度（经度, 纬度）
    longitude = 116.4074
    latitude = 39.9042
    altitude = 0  # meters

    # 设置地理参数（经度, 纬度, 高度）
    swe.set_topo(longitude, latitude, altitude)

    # 计算儒略日（使用 UTC 小时）
    hour_ut = utc_fractional_hour(birth_date_local)
    jd_ut = swe.julday(birth_date_local.year, birth_date_local.month, birth_date_local.day, hour_ut)

    # 主要天体映射
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }

    planet_positions = {}
    for name, pid in planets.items():
        try:
            res, serr = swe.calc_ut(jd_ut, pid)
        except Exception as e:
            print(f"{name}: error calling swe.calc_ut: {e}")
            continue

        # res is typically a list/tuple where res[0] is ecliptic longitude in degrees
        if isinstance(res, (list, tuple)) and len(res) >= 1:
            lon = res[0] % 360.0
            lon_rounded = round(lon, 2)
            sign, deg_in_sign = zodiac_sign_name(lon)
            planet_positions[name] = {
                "longitude": lon_rounded,
                "zodiac": sign,
                "deg_in_sign": deg_in_sign
            }
        else:
            print(f"{name}: unexpected result from swe.calc_ut: {res} {serr}")

    # 打印结果
    print(f"Birth (local): {birth_date_local.isoformat()}  -> UT fractional hour: {hour_ut}")
    print("Planet ecliptic longitudes (degrees) and zodiac:")
    for planet, info in planet_positions.items():
        print(f"{planet}: {info['longitude']}°  ({info['zodiac']} {info['deg_in_sign']}°)")

if __name__ == "__main__":
    main()