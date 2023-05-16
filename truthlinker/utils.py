import re

from typing import List

import mwparserfromhell  # type: ignore
import nltk  # type: ignore
import requests

from truthlinker.constants import DICT_LANG_NLTK, USER_AGENT


def wikitext2text(wikitext: str) -> str:
    """
    Method to get the text of leading section from the wikitext of article
    :param wikitext:
    :return: extracted text
    """
    # we select only the lead section
    first_section = re.search('={2,}.+?={2,}', wikitext)
    if first_section:
        wikitext_sec = wikitext[:first_section.span()[0]]
    else:
        wikitext_sec = wikitext

    # we replace <ref>-tags
    filter_wikitext = re.sub(r"<\s*ref.*?\n?(<\s*/ref\s*>|/\s*>)", "", wikitext_sec)
    wiki_code = mwparserfromhell.parse(filter_wikitext)

    text = wiki_code.strip_code()
    return text


def text2sentences(text: str, lang: str = "en") -> List[str]:
    """
    Method to split text into sentences
    :param text: text to split
    :param lang: text language
    :return: list of sentences
    """
    # map to nltk's language (default: english)
    lang_nltk = DICT_LANG_NLTK.get(lang, "english")

    # full stop bengali
    text = text.replace("।", ".\n")
    # full stop armenian (this is not the same as colon)
    text = text.replace("։", ".\n")

    sentences = []
    # loading the sentence-tokenizer
    try:
        sentence_tokenizer = nltk.data.load(f"tokenizers/punkt/{lang_nltk}.pickle")
    except Exception as e:
        print(e, "lang_nltk")
        sentence_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")

    # ToDo: Consider abbreviation handling

    for line in text.split("\n"):
        for sent in sentence_tokenizer.tokenize(line):
            # formatting with whitespaces
            if len(sent) < 2:
                continue
            # remove trailing navigation links to categories etc
            if sent[-1] != ".":
                continue
            # remove captions from images (not handled well by mwparserfromhell)
            # https://github.com/earwig/mwparserfromhell/issues/169
            if "|" in sent:
                continue
            sentences += [sent]
    return sentences


def get_article_wikitext(page_title: str, lang: str = "en") -> str:
    """
    Method that implements page text extraction in multilingual setup (handling redirection)
    :param page_title: name of the page
    :param lang: desired language
    :return: wikitext
    """
    api_url = f"https://{lang}.wikipedia.org/w/api.php"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": page_title,
        "format": "json",
        "formatversion": "2",
    }
    req = requests.get(api_url, headers=headers, params=params).json()
    req_query = req.get("query")
    req_pages = req_query.get("pages")
    page = req_pages[0]
    wikitext = page.get("revisions", [])[0].get("content", "")

    # Check for redirect:
    redirect_pattern = r"^#[^\s]+ \[\[([^]]+)]]$"
    redirect_match = re.search(redirect_pattern, wikitext)
    if redirect_match:
        new_page_title = redirect_match.group(1)
        return get_article_wikitext(new_page_title, lang)
    return wikitext
