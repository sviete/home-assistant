"""
Support for interacting with Spotify.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.spotify/
"""
import logging
import asyncio
from homeassistant.ais_dom import ais_global
from homeassistant.components import ais_cloud
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import callback

aisCloud = ais_cloud.AisCloudWS()

REQUIREMENTS = ['spotipy-homeassistant==2.4.4.dev1']

_LOGGER = logging.getLogger(__name__)

AUTH_CALLBACK_NAME = 'api:ais_spotify_service'
AUTH_CALLBACK_PATH = ''

CONF_ALIASES = 'aliases'
CONF_CACHE_PATH = 'cache_path'
CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'
AIS_SPOTIFY_TOKEN = None

CONFIGURATOR_DESCRIPTION = 'Aby połączyć swoje konto Spotify, ' \
                           'kliknij link, zaloguj się i autoryzuj:'
CONFIGURATOR_LINK_NAME = 'Połącz konto Spotify'
CONFIGURATOR_SUBMIT_CAPTION = 'OK wykonane. Synchronizuj!'

DEFAULT_CACHE_PATH = '.dom/.ais-dom-spotify-token-cache'
DEFAULT_NAME = 'Spotify'
DEPENDENCIES = ['http']
DOMAIN = 'ais_spotify_service'

ICON = 'mdi:spotify'

SCOPE = 'app-remote-control streaming user-read-email'
G_SPOTIFY_FOUND = []

def request_configuration(hass, config, oauth):
    """Request Spotify authorization."""
    configurator = hass.components.configurator
    hass.data[DOMAIN] = configurator.request_config(
        DEFAULT_NAME, lambda _: None,
        link_name=CONFIGURATOR_LINK_NAME,
        link_url=oauth.get_authorize_url(),
        description=CONFIGURATOR_DESCRIPTION,
        submit_caption=CONFIGURATOR_SUBMIT_CAPTION)


@asyncio.coroutine
def async_setup(hass, config):
    """Set up the Spotify platform."""
    import spotipy.oauth2
    import json
    global AIS_SPOTIFY_TOKEN

    try:
        ws_resp = aisCloud.key("spotify_oauth")
        json_ws_resp = ws_resp.json()
        spotify_redirect_url = json_ws_resp["SPOTIFY_REDIRECT_URL"]
        spotify_client_id = json_ws_resp["SPOTIFY_CLIENT_ID"]
        spotify_client_secret = json_ws_resp["SPOTIFY_CLIENT_SECRET"]
        spotify_scope = json_ws_resp["SPOTIFY_SCOPE"]
        try:
            ws_resp = aisCloud.key("spotify_token")
            key = ws_resp.json()["key"]
            AIS_SPOTIFY_TOKEN = json.loads(key)
        except:
            AIS_SPOTIFY_TOKEN = None
            _LOGGER.info("No AIS_SPOTIFY_TOKEN")
    except Exception as e:
        _LOGGER.error("No spotify oauth info: " + str(e))
        return False

    cache = hass.config.path(DEFAULT_CACHE_PATH)
    gate_id = ais_global.get_sercure_android_id_dom()
    oauth = spotipy.oauth2.SpotifyOAuth(spotify_client_id, spotify_client_secret, spotify_redirect_url,
                                        scope=spotify_scope, cache_path=cache, state=gate_id)
    token_info = oauth.get_cached_token()
    if not token_info:
        _LOGGER.info("no spotify token in cache;")
        if AIS_SPOTIFY_TOKEN is not None:
            with open(cache, 'w') as outfile:
                json.dump(AIS_SPOTIFY_TOKEN, outfile)
            token_info = oauth.get_cached_token()
        if not token_info:
            _LOGGER.info("no spotify token; run configurator")
            request_configuration(hass, config, oauth)
            return True

    if hass.data.get(DOMAIN):
        configurator = hass.components.configurator
        configurator.request_done(hass.data.get(DOMAIN))
        del hass.data[DOMAIN]

    # register services
    data = hass.data[DOMAIN] = SpotifyData(hass, oauth)

    @asyncio.coroutine
    def search(call):
        _LOGGER.info("search")
        yield from data.process_search_async(call)

    def select_track_name(call):
        _LOGGER.info("select_track_name")
        data.process_select_track_name(call)

    hass.services.async_register(DOMAIN, 'search', search)
    hass.services.async_register(DOMAIN, 'select_track_name', select_track_name)

    # add spotify to service list
    # hass.async_add_job(
    #     hass.services.async_call(
    #         'input_select',
    #         'set_options', {
    #             "entity_id": "input_select.ais_music_service",
    #             "options": ["YouTube", "Spotify"]}
    #     )
    # )

    return True


class SpotifyAuthCallbackView(HomeAssistantView):
    """Spotify Authorization Callback View."""

    requires_auth = False
    url = AUTH_CALLBACK_PATH
    name = AUTH_CALLBACK_NAME

    def __init__(self, config, add_entities, oauth):
        """Initialize."""
        self.config = config
        self.add_entities = add_entities
        self.oauth = oauth

    @callback
    def get(self, request):
        """Receive authorization token."""
        hass = request.app['hass']
        self.oauth.get_access_token(request.query['code'])


class SpotifyData:
    """Representation of a Spotify browser."""

    def __init__(self, hass, oauth):
        """Initialize."""
        self.hass = hass
        self._oauth = oauth
        self._spotify = None
        self._user = None
        self._token_info = self._oauth.get_cached_token()

    def refresh_spotify_instance(self):
        """Fetch a new spotify instance."""
        import spotipy

        token_refreshed = False
        need_token = (self._token_info is None or
                      self._oauth.is_token_expired(self._token_info))
        if need_token:
            new_token = \
                self._oauth.refresh_access_token(
                    self._token_info['refresh_token'])
            # skip when refresh failed
            if new_token is None:
                return

            self._token_info = new_token
            token_refreshed = True
        if token_refreshed or self._spotify is None:
            self._spotify = spotipy.Spotify(auth=self._token_info.get('access_token'))
            self._user = self._spotify.me()

    @asyncio.coroutine
    def process_search_async(self, call):
        """Search album on Spotify."""
        if "query" not in call.data:
            _LOGGER.error("No text to search")
            return
        global G_SPOTIFY_FOUND
        search_text = call.data["query"]

        self.refresh_spotify_instance()

        # Don't true search when token is expired
        if self._oauth.is_token_expired(self._token_info):
            _LOGGER.warning("Spotify failed to update, token expired.")
            return

        results = self._spotify.search(q='artist:' + search_text, type='artist')
        items = results['artists']['items']

        found = []
        titles = []
        for item in items:
            i = {}
            i["uri"] = item['uri']
            i["title"] = "Wykonawca " + item['name']
            if len(item['images']) > 0:
                i["thumbnail"] = item['images'][0]['url']
            else:
                i["thumbnail"] = ""
            titles.append(item['name'])
            found.append(i)
        G_SPOTIFY_FOUND = found
        _LOGGER.debug('found artist' + str(found))





        # Update input_select values:
        yield from self.hass.services.async_call(
            'input_select',
            'set_options', {
                "entity_id": "input_select.ais_music_track_name",
                "options": titles})

        text = "Znaleziono: %s, włączam pierwszy: %s" % (
            str(len(G_SPOTIFY_FOUND)), G_SPOTIFY_FOUND[0]["title"])
        _LOGGER.debug("text: " + text)
        yield from self.hass.services.async_call(
            'ais_ai_service', 'say_it', {
                "text": text
            })

    def process_select_track_name(self, call):
        _LOGGER.info("process_select_track_name")
        import json
        # """Search in last search return."""
        name = call.data["name"]
        for item in G_SPOTIFY_FOUND:
            if item["title"] == name:
                item_uri = item["uri"]
                _audio_info = json.dumps(
                    {"IMAGE_URL": item["thumbnail"], "NAME": item["title"], "MEDIA_SOURCE": ais_global.G_AN_SPOTIFY}
                )

        player_name = self.hass.states.get(
            'input_select.ais_music_player').state
        player = ais_cloud.get_player_data(player_name)
        self.hass.services.call(
            'media_player',
            'play_media', {
                "entity_id": player["entity_id"],
                "media_content_type": "audio/mp4",
                "media_content_id": item_uri
            })
        _LOGGER.info(
            "player: " + str(player["entity_id"]) + " " + "media_content_id: " + "spotify:album:" + str(item_uri))

        # set stream image and title
        # if entity_id == 'media_player.wbudowany_glosnik':
        self.hass.services.call(
            'media_player',
            'play_media', {
                "entity_id": player["entity_id"],
                "media_content_type": "ais_info",
                "media_content_id": _audio_info
            })

