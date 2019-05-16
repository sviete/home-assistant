"""The tests for the Sun helpers."""
# pylint: disable=protected-access
from unittest.mock import patch
from datetime import timedelta, datetime

from homeassistant.const import SUN_EVENT_SUNRISE, SUN_EVENT_SUNSET
import homeassistant.util.dt as dt_util
import homeassistant.helpers.sun as sun


def test_next_events(hass):
    """Test retrieving next sun events."""
    utc_now = datetime(2016, 11, 1, 8, 0, 0, tzinfo=dt_util.UTC)
    from astral import Astral

    astral = Astral()
    utc_today = utc_now.date()

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    mod = -1
    while True:
        next_dawn = (astral.dawn_utc(
            utc_today + timedelta(days=mod), latitude, longitude))
        if next_dawn > utc_now:
            break
        mod += 1

    mod = -1
    while True:
        next_dusk = (astral.dusk_utc(
            utc_today + timedelta(days=mod), latitude, longitude))
        if next_dusk > utc_now:
            break
        mod += 1

    mod = -1
    while True:
        next_midnight = (astral.solar_midnight_utc(
            utc_today + timedelta(days=mod), longitude))
        if next_midnight > utc_now:
            break
        mod += 1

    mod = -1
    while True:
        next_noon = (astral.solar_noon_utc(
            utc_today + timedelta(days=mod), longitude))
        if next_noon > utc_now:
            break
        mod += 1

    mod = -1
    while True:
        next_rising = (astral.sunrise_utc(
            utc_today + timedelta(days=mod), latitude, longitude))
        if next_rising > utc_now:
            break
        mod += 1

    mod = -1
    while True:
        next_setting = (astral.sunset_utc(
            utc_today + timedelta(days=mod), latitude, longitude))
        if next_setting > utc_now:
            break
        mod += 1

    with patch('homeassistant.helpers.condition.dt_util.utcnow',
               return_value=utc_now):
        assert next_dawn == sun.get_astral_event_next(
            hass, 'dawn')
        assert next_dusk == sun.get_astral_event_next(
            hass, 'dusk')
        assert next_midnight == sun.get_astral_event_next(
            hass, 'solar_midnight')
        assert next_noon == sun.get_astral_event_next(
            hass, 'solar_noon')
        assert next_rising == sun.get_astral_event_next(
            hass, SUN_EVENT_SUNRISE)
        assert next_setting == sun.get_astral_event_next(
            hass, SUN_EVENT_SUNSET)


def test_date_events(hass):
    """Test retrieving next sun events."""
    utc_now = datetime(2016, 11, 1, 8, 0, 0, tzinfo=dt_util.UTC)
    from astral import Astral

    astral = Astral()
    utc_today = utc_now.date()

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    dawn = astral.dawn_utc(utc_today, latitude, longitude)
    dusk = astral.dusk_utc(utc_today, latitude, longitude)
    midnight = astral.solar_midnight_utc(utc_today, longitude)
    noon = astral.solar_noon_utc(utc_today, longitude)
    sunrise = astral.sunrise_utc(utc_today, latitude, longitude)
    sunset = astral.sunset_utc(utc_today, latitude, longitude)

    assert dawn == sun.get_astral_event_date(
        hass, 'dawn', utc_today)
    assert dusk == sun.get_astral_event_date(
        hass, 'dusk', utc_today)
    assert midnight == sun.get_astral_event_date(
        hass, 'solar_midnight', utc_today)
    assert noon == sun.get_astral_event_date(
        hass, 'solar_noon', utc_today)
    assert sunrise == sun.get_astral_event_date(
        hass, SUN_EVENT_SUNRISE, utc_today)
    assert sunset == sun.get_astral_event_date(
        hass, SUN_EVENT_SUNSET, utc_today)


def test_date_events_default_date(hass):
    """Test retrieving next sun events."""
    utc_now = datetime(2016, 11, 1, 8, 0, 0, tzinfo=dt_util.UTC)
    from astral import Astral

    astral = Astral()
    utc_today = utc_now.date()

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    dawn = astral.dawn_utc(utc_today, latitude, longitude)
    dusk = astral.dusk_utc(utc_today, latitude, longitude)
    midnight = astral.solar_midnight_utc(utc_today, longitude)
    noon = astral.solar_noon_utc(utc_today, longitude)
    sunrise = astral.sunrise_utc(utc_today, latitude, longitude)
    sunset = astral.sunset_utc(utc_today, latitude, longitude)

    with patch('homeassistant.util.dt.now', return_value=utc_now):
        assert dawn == sun.get_astral_event_date(
            hass, 'dawn', utc_today)
        assert dusk == sun.get_astral_event_date(
            hass, 'dusk', utc_today)
        assert midnight == sun.get_astral_event_date(
            hass, 'solar_midnight', utc_today)
        assert noon == sun.get_astral_event_date(
            hass, 'solar_noon', utc_today)
        assert sunrise == sun.get_astral_event_date(
            hass, SUN_EVENT_SUNRISE, utc_today)
        assert sunset == sun.get_astral_event_date(
            hass, SUN_EVENT_SUNSET, utc_today)


def test_date_events_accepts_datetime(hass):
    """Test retrieving next sun events."""
    utc_now = datetime(2016, 11, 1, 8, 0, 0, tzinfo=dt_util.UTC)
    from astral import Astral

    astral = Astral()
    utc_today = utc_now.date()

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    dawn = astral.dawn_utc(utc_today, latitude, longitude)
    dusk = astral.dusk_utc(utc_today, latitude, longitude)
    midnight = astral.solar_midnight_utc(utc_today, longitude)
    noon = astral.solar_noon_utc(utc_today, longitude)
    sunrise = astral.sunrise_utc(utc_today, latitude, longitude)
    sunset = astral.sunset_utc(utc_today, latitude, longitude)

    assert dawn == sun.get_astral_event_date(
        hass, 'dawn', utc_now)
    assert dusk == sun.get_astral_event_date(
        hass, 'dusk', utc_now)
    assert midnight == sun.get_astral_event_date(
        hass, 'solar_midnight', utc_now)
    assert noon == sun.get_astral_event_date(
        hass, 'solar_noon', utc_now)
    assert sunrise == sun.get_astral_event_date(
        hass, SUN_EVENT_SUNRISE, utc_now)
    assert sunset == sun.get_astral_event_date(
        hass, SUN_EVENT_SUNSET, utc_now)


def test_is_up(hass):
    """Test retrieving next sun events."""
    utc_now = datetime(2016, 11, 1, 12, 0, 0, tzinfo=dt_util.UTC)
    with patch('homeassistant.helpers.condition.dt_util.utcnow',
               return_value=utc_now):
        assert not sun.is_up(hass)

    utc_now = datetime(2016, 11, 1, 18, 0, 0, tzinfo=dt_util.UTC)
    with patch('homeassistant.helpers.condition.dt_util.utcnow',
               return_value=utc_now):
        assert sun.is_up(hass)


def test_norway_in_june(hass):
    """Test location in Norway where the sun doesn't set in summer."""
    hass.config.latitude = 69.6
    hass.config.longitude = 18.8

    june = datetime(2016, 6, 1, tzinfo=dt_util.UTC)

    print(sun.get_astral_event_date(hass, SUN_EVENT_SUNRISE,
                                    datetime(2017, 7, 25)))
    print(sun.get_astral_event_date(hass, SUN_EVENT_SUNSET,
                                    datetime(2017, 7, 25)))

    print(sun.get_astral_event_date(hass, SUN_EVENT_SUNRISE,
                                    datetime(2017, 7, 26)))
    print(sun.get_astral_event_date(hass, SUN_EVENT_SUNSET,
                                    datetime(2017, 7, 26)))

    assert sun.get_astral_event_next(hass, SUN_EVENT_SUNRISE, june) \
        == datetime(2016, 7, 25, 23, 23, 39, tzinfo=dt_util.UTC)
    assert sun.get_astral_event_next(hass, SUN_EVENT_SUNSET, june) \
        == datetime(2016, 7, 26, 22, 19, 1, tzinfo=dt_util.UTC)
    assert sun.get_astral_event_date(hass, SUN_EVENT_SUNRISE, june) \
        is None
    assert sun.get_astral_event_date(hass, SUN_EVENT_SUNSET, june) \
        is None
