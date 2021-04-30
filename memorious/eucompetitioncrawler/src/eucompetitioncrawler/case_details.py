# TODO
# - [ ] case_list: parse metadata for a case and pass it on (via context)
# - [ ] case_details: parse metadata for the table of events (<table class="events">)
# - [ ] case_details: filter content to avoid fetching all available languages

import logging
from banal import ensure_list
from urllib.parse import urljoin
from normality import collapse_spaces
from servicelayer.cache import make_key

from memorious.helpers.rule import Rule
from memorious.helpers.dates import iso_date
from memorious.operations.parse import parse_html, parse_for_metadata


log = logging.getLogger(__name__)
# 3 possibilities : case list, case details, no case (when we generate URLs with sequences of numerical ids)
XP_LIST = './/table[@class="list"]'
XP_DETAILS = './/table[@class="details"]'
XP_ERR = './/h2[text()[contains(., "Procedure doesn\'t exist.")]]'
# case_details
XP_COMPANIES = './/tr[td[@class="ClassLabelDetail_1"][text()[contains(., "Companies:")]]]/td[@class="ClassTextDetail"]'
XP_ACTIVITIES = './/tr[td[@class="ClassLabelDetail_1"][text()[contains(., "Economic Activity:")]]]/td[@class="ClassTextDetail"]'


def parse_case_list(context, data, result):
    """Parse metadata from a case_list page and pass it on to case_details.

    The retrieved metadata is about policy area, case number and title.
    (Should we also get member state and last decision date?)

    Parameters
    ----------
    context : ?
        Context
    data : Dict[str, Any]
        Data
    result : memorious.logic.ContextHttpResponse
        HTTP response
    """
    # copied and adapted from memorious.operations.parse.parse_html
    context.log.info("Parse case_list: %r", result.url)

    case_list = result.html.xpath('.//table[@class="list"]')[0]
    for row in case_list.xpath('.//tr[td[@class="case"]]'):
        # read row for a case
        data["policy_area"] = collapse_spaces(
            row.xpath('.//td[@class="policy"]')[0].text_content()
        )
        case_num = row.xpath('.//td[@class="case"]/a')[0]
        data["case_num"] = collapse_spaces(case_num.text_content())
        case_link = case_num.get("href")
        data["member_state"] = collapse_spaces(
            row.xpath('.//td[@class="member"]')[0].text_content()
        )
        data["last_decision_date"] = collapse_spaces(
            row.xpath('.//td[@class="decision"]')[0].text_content()
        )
        data["case_title"] = collapse_spaces(
            row.xpath('.//td[@class="tittle"]')[0].text_content()
        )
        # build URL
        try:
            url = urljoin(result.url, case_link)
            key = url
        except Exception:
            log.warning("Invalid URL: %r", case_link)
            continue
        # check for duplicate and set URL
        tag = make_key(context.run_id, key)
        if context.check_tag(tag):
            continue
        context.set_tag(tag, None)
        data["url"] = url
        # fetch
        context.http.session.headers["Referer"] = url
        context.emit(rule="fetch", data=data)


def parse_case_events(context, data, result):
    """Parse metadata from the events in a case_details page and pass it on to linked docs.

    The retrieved metadata is about date, document type, document and language.

    Parameters
    ----------
    context : ?
        Context
    data : Dict[str, Any]
        Data
    result : memorious.logic.ContextHttpResponse
        HTTP response
    """
    # copied and adapted from memorious.operations.parse.parse_html
    context.log.info("Parse case_events: %r", result.url)

    event_list = result.html.xpath('.//table[@class="events"]')[0]
    base_title = data["title"]
    for row in event_list.xpath('.//tr[td[@class="eventsTdDate"]]'):
        # read row for a case event
        # - publication date
        pub_date_str = collapse_spaces(
            row.xpath('.//td[@class="eventsTdDate"]')[0].text_content()
        )
        # dates are written 21.01.2012, we need to convert to an even more standard format
        pub_date = iso_date(pub_date_str, format_hint="%d.%m.%Y")
        # "published_at" is understood by aleph.validation.schema.ingest
        data["published_at"] = pub_date
        # - document type and document
        doc_type = collapse_spaces(
            row.xpath('.//td[@class="eventsTdDocType"]')[0].text_content()
        )
        data["doc_type"] = doc_type
        # "doc" could be a title but very often is not informative enough
        td_doc = row.xpath('.//td[@class="eventsTdDoc"]')[0]
        doc = collapse_spaces(td_doc.text_content())
        data["doc"] = doc
        # we define title = title + date + doc_type + doc + doc_language
        for doc_lang in td_doc.xpath(".//a"):
            doc_lg = collapse_spaces(doc_lang.text_content())
            data["doc_language"] = doc_lg
            # we build a very long but precise title for this document, that aleph can understand
            data["title"] = " > ".join(
                (base_title, pub_date_str, doc_type, doc, doc_lg)
            )
            doc_link = doc_lang.get("href")
            # build URL
            try:
                url = urljoin(result.url, doc_link)
                key = url
            except Exception:
                log.warning("Invalid URL: %r", doc_link)
                continue
            # check for duplicate and set URL
            tag = make_key(context.run_id, key)
            if context.check_tag(tag):
                continue
            context.set_tag(tag, None)
            data["url"] = url
            # fetch
            context.http.session.headers["Referer"] = url
            context.emit(rule="fetch", data=data)


def parse_case_details(context, data, result):
    """Parse specific case metadata from a case_details page.

    The retrieved metadata is about companies involved, economic activities, events on the case.

    Parameters
    ----------
    context : ?
        Context
    data : Dict[str, Any]
        Data
    result : memorious.logic.ContextHttpResponse
        HTTP response
    """
    # 1. Companies : extract structured data and parse links :
    # for each link, recursively fetch that page by handing it back
    # to the 'fetch' stage.
    cell_companies = result.html.xpath(XP_COMPANIES)
    if not cell_companies:
        data["companies"] = []
    else:
        # there should be a unique matching element
        cell_companies = cell_companies[0]
        # company names are separated by a forward slash
        comp_names = cell_companies.text_content().split("/\n")
        # clean up the many whitespaces (including newlines) between tokens
        comp_names = [
            " ".join(line.strip() for line in x.splitlines() if line.strip())
            for x in comp_names
        ]
        data["companies"] = comp_names
        # print(f"Companies: {repr(data['companies'])}")  # DEBUG

    # 2. Economic activities : extract structured data and parse links :
    # for each link, recursively fetch that page by handing it back
    # to the 'fetch' stage.
    cell_activities = result.html.xpath(XP_ACTIVITIES)
    if not cell_activities:
        data["economic_activities"] = []
    else:
        # there should be a unique matching element
        cell_activities = cell_activities[0]
        # activity names are composed of (1) a link <a> for the NACE, (2) the following text (aka tail)
        # for the long description, until the next <br> (could equally be the next <a>)
        acti_names = [(x.text_content(), x.tail) for x in cell_activities.xpath(".//a")]
        # clean up the many whitespaces (including newlines) between tokens, for the NACE
        # and the description as well
        acti_names = [
            tuple(
                [
                    " ".join(line.strip() for line in x.splitlines() if line.strip())
                    for x in acti_name
                ]
            )
            for acti_name in acti_names
        ]
        # we turn each tuple (nace, description) into a unique string "<nace>  - <description>"
        acti_names = [" ".join(x) for x in acti_names]
        data["economic_activities"] = acti_names
        # print(f"Economic activities: {repr(data['economic_activities'])}")  # DEBUG
    # we put companies and economic activities in a single list named "keywords" that aleph can read
    data["keywords"] = data["companies"] + data["economic_activities"]
    return data


def parse_competition(context, data):
    """Parse a page. Determines which method to call : list or details.

    Parameters
    ----------
    context : ?
        Context
    data : Dict[str, Any]
        Data
    """
    # copied from memorious.operations.parse, lightly adapted as necessary
    with context.http.rehash(data) as result:
        if result.html is not None:
            # Get extra metadata from the DOM
            parse_for_metadata(context, data, result.html)
            # begin custom code
            # Get specific metadata then parse for links
            if result.html.xpath(XP_LIST):
                parse_case_list(context, data, result)
            elif result.html.xpath(XP_DETAILS):
                parse_case_details(context, data, result)
                parse_case_events(context, data, result)
            elif result.html.xpath(XP_ERR):
                # print(f"No case at : {result.url}")  # DEBUG
                return
            else:
                # we might be on another website, eg. on the Press Corner or EUR-LEX,
                # that we don't support well currently
                parse_html(context, data, result)
            # end custom code

        rules = context.params.get("store") or {"match_all": {}}
        if Rule.get_rule(rules).apply(result):
            context.emit(rule="store", data=data)
