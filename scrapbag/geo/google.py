#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import json
import logging
import requests
import ssl
import urllib.request
import urllib.parse
from urllib.parse import urljoin
import structlog

# change for logging visibility
logger = structlog.getLogger(__name__)


ROOT_GOOGLEMAPS_API_URL = "https://maps.googleapis.com"

# urls for google api web service
DETAIL_GOOGLEMAPS_API_URL = urljoin(ROOT_GOOGLEMAPS_API_URL, "maps/api/place/details/json")

NEARBY_GOOGLEMAPS_API_URL = urljoin(ROOT_GOOGLEMAPS_API_URL, 'maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type=bar&key={api_key}&pagetoken={pagetoken}')

# user agent for populartimes request
default_user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/54.0.2840.98 Safari/537.36"}


def get_popularity_for_day(popularity):
    """

    :param popularity:
    :return:
    """
    pop_json = [[0 for _ in range(24)] for _ in range(7)]
    wait_json = [[[0, "Closed"] for _ in range(24)] for _ in range(7)]

    for day in popularity:

        day_no, pop_times = day[:2]

        if pop_times is not None:
            for el in pop_times:

                hour, pop, wait_str = el[0], el[1], el[3],

                pop_json[day_no - 1][hour] = pop

                wait_l = [int(s) for s in wait_str.replace("\xa0", " ").split(" ") if s.isdigit()]
                wait_json[day_no - 1][hour] = [0 if len(wait_l) == 0 else wait_l[0], wait_str]

                # day wrap
                if hour == 23:
                    day_no = day_no % 7 + 1

    result_pop = {}
    result_wait = {}

    for d in range(7):
        day_name = list(calendar.day_name)[d]

        result_pop[day_name] = dict(zip([x for x in range(0, 24)], pop_json[d]))
        result_wait[day_name] = dict(zip([x for x in range(0, 24)], wait_json[d]))

    return result_pop, result_wait


def index_get(array, *argv):
    """
    checks if a index is available in the array and returns it
    :param array: the data array
    :param argv: index integers
    :return: None if not available or the return value
    """

    try:

        for index in argv:
            array = array[index]

        return array

    # there is either no info available or no popular times
    # TypeError: rating/rating_n/populartimes wrong of not available
    except (IndexError, TypeError):
        return None


def add_optional_parameters(detail_json, detail, rating, rating_n, popularity, current_popularity, time_spent):
    """
    check for optional return parameters and add them to the result json
    :param detail_json:
    :param detail:
    :param rating:
    :param rating_n:
    :param popularity:
    :param current_popularity:
    :param time_spent:
    :return:
    """

    if rating is not None:
        detail_json["rating"] = rating
    elif "rating" in detail:
        detail_json["rating"] = detail["rating"]

    if rating_n is not None:
        detail_json["rating_n"] = rating_n

    if "international_phone_number" in detail:
        detail_json["international_phone_number"] = detail["international_phone_number"]

    if current_popularity is not None:
        detail_json["current_popularity"] = current_popularity

    if popularity is not None:
        popularity, wait_times = get_popularity_for_day(popularity)

        detail_json["populartimes"] = popularity
        detail_json["time_wait"] = wait_times

    if time_spent is not None:
        detail_json["time_spent"] = time_spent

    return detail_json


def get_populartimes_from_search(place_identifier, user_agent=default_user_agent, **kwargs):
    """
    request information for a place and parse current popularity
    :param place_identifier: name and address string
    :return:
    """
    params_url = {
        "tbm": "map",
        "tch": 1,
        "q": urllib.parse.quote_plus(place_identifier),
        "pb": "!4m12!1m3!1d4005.9771522653964!2d-122.42072974863942!3d37.8077459796541!2m3!1f0!2f0!3f0!3m2!1i1125!2i976"
              "!4f13.1!7i20!10b1!12m6!2m3!5m1!6e2!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m61!2m2!1i203!2i100!3m2!2i4!5b1"
              "!6m6!1m2!1i86!2i86!1m2!1i408!2i200!7m46!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!"
              "1m3!1e4!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e"
              "10!2b0!3e4!2b1!4b1!9b0!22m6!1sa9fVWea_MsX8adX8j8AE%3A1!2zMWk6Mix0OjExODg3LGU6MSxwOmE5ZlZXZWFfTXNYOGFkWDh"
              "qOEFFOjE!7e81!12e3!17sa9fVWea_MsX8adX8j8AE%3A564!18e15!24m15!2b1!5m4!2b1!3b1!5b1!6b1!10m1!8e3!17b1!24b1!"
              "25b1!26b1!30m1!2b1!36b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i976!1m6!1m2!1i1075!2i0!2m2!"
              "1i1125!2i976!1m6!1m2!1i0!2i0!2m2!1i1125!2i20!1m6!1m2!1i0!2i956!2m2!1i1125!2i976!37m1!1e81!42b1!47m0!49m1"
              "!3b1"
    }

    search_url = "https://www.google.es/search?" + "&".join(k + "=" + str(v) for k, v in params_url.items())
    logging.info("searchterm: " + search_url)

    # noinspection PyUnresolvedReferences
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    resp = urllib.request.urlopen(
        urllib.request.Request(
            url=search_url,
            data=None,
            headers=user_agent),
        context=gcontext)

    data = resp.read().decode('utf-8').split('/*""*/')[0]

    # find eof json
    jend = data.rfind("}")
    if jend >= 0:
        data = data[:jend + 1]

    jdata = json.loads(data)["d"]
    jdata = json.loads(jdata[4:])

    # get info from result array, has to be adapted if backend api changes
    info = index_get(jdata, 0, 1, 0, 14)

    rating = index_get(info, 4, 7)
    rating_n = index_get(info, 4, 8)

    popular_times = index_get(info, 84, 0)

    # current_popularity is also not available if popular_times isn't
    current_popularity = index_get(info, 84, 7, 1)

    time_spent = index_get(info, 117, 0)

    # extract numbers from time string
    if time_spent is not None:
        time_spent = time_spent.replace("\xa0", " ")

        time_spent = [[
            float(s) for s in time_spent.replace("-", " ").replace(",", ".").split(" ")
            if s.replace('.', '', 1).isdigit()
        ], time_spent]

    return rating, rating_n, popular_times, current_popularity, time_spent


def check_response_code(resp):
    """
    check if query quota has been surpassed or other errors occured
    :param resp: json response
    :return:
    """
    if resp["status"] == "OK" or resp["status"] == "ZERO_RESULTS":
        return

    if resp["status"] == "REQUEST_DENIED":
        raise Exception("Google Places " + resp["status"],
                        "Request was denied, the API key is invalid.")

    if resp["status"] == "OVER_QUERY_LIMIT":
        raise Exception("Google Places " + resp["status"],
                        "You exceeded your Query Limit for Google Places API Web Service, "
                        "check https://developers.google.com/places/web-service/usage "
                        "to upgrade your quota.")

    if resp["status"] == "INVALID_REQUEST":
        raise Exception("Google Places " + resp["status"],
                        "The query string is malformed, "
                        "check if your formatting for lat/lng and radius is correct.")

    raise Exception("Google Places " + resp["status"],
                    "Unidentified error with the Places API, please check the response code")


def get_place_details(api_key, place_id, **kwargs):
    """
    sends request to detail to get a search string and uses standard proto buffer to get additional information
    on the current status of popular times
    :return: json details
    """

    params = {
        'placeid': place_id,
        'key': api_key,
        }

    resp = requests.get(url=DETAIL_GOOGLEMAPS_API_URL, params=params)

    if resp.status_code >= 300:
        raise Exception('Bad status code rerieved from google api')

    data = json.loads(resp.text)

    # check api response status codess
    check_response_code(data)

    detail = data.get("result", {})

    place_identifier = "{} {}".format(detail.get("name"), detail.get("formatted_address"))

    detail_json = {
        "id": detail.get("place_id"),
        "name": detail.get("name"),
        "address": detail.get("formatted_address"),
        "types": detail.get("types"),
        "coordinates": detail.get("geometry", {}).get("location")
    }

    detail_json = add_optional_parameters(
        detail_json, detail,
        *get_populartimes_from_search(place_identifier, **kwargs)
    )

    return detail_json


def get_places_by_geo_radius(api_key, latitude, longitude, radius=500, types=[], **kwargs):

    pagetoken = True

    while pagetoken:

        params = {
                'location': '{}, {}'.format(latitude, longitude),
                'radius': radius,
                'type': ','.join(types),
                'api_key': api_key,
                'pagetoken': pagetoken if isinstance(pagetoken, str) else ''
                }

        resp = requests.get(url=NEARBY_GOOGLEMAPS_API_URL, params=params)

        if resp.status_code >= 300:
            raise Exception('Bad status code rerieved from google api')

        data = json.loads(resp.text)

        # check api response status codess
        check_response_code(data)

        pagetoken = data.get('next_page_token')
        results = data.get('results', [])

        yield results
