# Install re2
# pip3 install fb-re2 simpleeval
# TODO: replace grequests in ebay sdk
import math

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import simpleeval
from pprint import pprint
import re2 as re
from typing import NamedTuple
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


class Item(NamedTuple):
    price: float
    title: str
    url: str
    galleryURL: str
    condition: str


class SearchResult(NamedTuple):
    item: Item
    unit_price: float


def _get_value(rx_compiled, value_expression, item):
    seval = simpleeval.SimpleEval()
    for match in [rx_compiled.search(item.title.lower())]:
        if not match:
            continue
        seval.names = {**match.groupdict(),
                       **simpleeval.DEFAULT_NAMES,
                       'price': item.price}
        logger.info(f"Evaluating item {item}, match {match}")
        try:
            return seval.eval(value_expression)
        except Exception as e:
            logger.warning(f"Ignoring exception: {e}")
            return math.inf
    return 0


ebay_api = Finding(appid="",
                   config_file=None, warnings=True, https=True)


def _ebay_search(keywords):
    for pageNumber in range(1, 4 + 1):
        response = ebay_api.execute('findItemsAdvanced', {
            'keywords': keywords,
            'paginationInput': {
                'pageNumber': pageNumber,
            }
        })
        for item in response.reply.searchResult.item:
            try:
                if item.isMultiVariationListing == 'true':
                    logger.info("Skipping a MultiVariationListing because handling it is too much work.")
                    continue
                price = float(item.sellingStatus.convertedCurrentPrice.value)
                if item.listingInfo.listingType in ('Auction', 'AuctionWithBIN'):
                    if item.listingInfo.buyItNowAvailable == 'false':
                        price = math.inf
                    else:
                        price = item.listingInfo.convertedBuyItNowPrice
                ret = Item(title=item.title,
                           price=price,
                           url=item.viewItemURL,
                           galleryURL=item.galleryURL,
                           condition=item.condition.conditionDisplayName)
            except Exception as e:
                logger.warning("Ignoring exception" + str(e))
                continue
            yield ret


def search_and_evaluate(keywords, regex_query_string, expression_string):
    logger.warning(f"Compiling {regex_query_string}")
    regex_query = re.compile(regex_query_string)
    try:
        items = _ebay_search(keywords)
        for item in items:
            unit_price = _get_value(regex_query, expression_string, item)
            if unit_price != 0:
                yield SearchResult(item, unit_price)
                pass
    except ConnectionError as e:
        logger.error(f"Ignoring: {e} {e.response.dict()}")
