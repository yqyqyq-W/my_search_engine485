"""Test search interface."""

import pathlib
import subprocess
import re
import bs4
import utils


def test_search_page_forms(search_client):
    """Verify the search page has the required forms.

    'search_client' is a fixture function that provides a Flask test server
    interface

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load search server main page
    response = search_client.get("/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")

    form_input_names = [submit.get("name") for button in soup.find_all('form')
                        for submit in button.find_all("input") if submit]
    assert "q" in form_input_names
    assert "w" in form_input_names

    form_input_types = [submit.get("type") for button in soup.find_all('form')
                        for submit in button.find_all("input") if submit]
    assert "text" in form_input_types
    assert "range" in form_input_types
    assert "submit" in form_input_types


def test_search_page_content(search_client):
    """Verify a search returns any results at all.

    'search_client' is a fixture function that provides a Flask test server
    interface

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load search server main page after search
    response = search_client.get("/?q={}&w={}".format("hello+world", "0.01"))
    soup = response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")

    # Make sure some doc titles show up
    assert soup.find_all("div", {"class": "doc_title"})


def test_query_one_titles(search_client):
    """Query with one term.

    'search_client' is a fixture function that provides a Flask test server
    interface

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load search server page with search query
    response = search_client.get("/?q={}&w={}".format("dogs", "0.22"))
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")

    # Verify resulting document titles
    doc_titles = soup.find_all("div", {"class": "doc_title"})
    assert len(doc_titles) == 10

    doc_titles_text = [re.sub(r"\s+", " ", x.text.strip()) for x in doc_titles]
    assert doc_titles_text == [
        "Boerboel",
        "Fogelsville, Pennsylvania",
        "Frederick Forsyth",
        "Brits, North West",
        "Northeast Greenland National Park",
        "Alburquerque, Bohol",
        "DM",
        "Petplan USA",
        "Fictional African countries",
        "Kudremukh",
    ]


def test_query_one_summary_url(search_client):
    """Do a search and verify summary and url content.

    'search_client' is a fixture function that provides a Flask test server
    interface

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load search server page with search query
    response = search_client.get("/?q={}&w={}".format("pies", "0"))
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")

    # Verify resulting document titles
    doc_titles = soup.find_all("div", {"class": "doc_title"})
    assert len(doc_titles) == 3

    doc_titles_text = [re.sub(r"\s+", " ", x.text.strip()) for x in doc_titles]
    assert doc_titles_text == ["Eschweiler", "Gunge", "List of AT4W episodes"]

    doc_summaries = soup.find_all("div", {"class": "doc_summary"})
    assert len(doc_summaries) == 3

    doc_summary_text = [re.sub(r"\s+", " ", x.text.strip())
                        for x in doc_summaries]
    assert doc_summary_text == [
        "Eschweiler (German pronunciation: [ˈɛʃvaɪlɐ]) is a municipality in "
        "the district of Aachen in North Rhine-Westphalia in Germany on the "
        "river Inde, near the German-Belgian-Dutch border, and about 15 "
        "kilometres (9 mi) east of Aachen and 50 kilometres ...",
        "Gunge as it is known in the United Kingdom, or slime as it is known "
        "in the United States and most English-speaking areas of the world, "
        "is a thick, gooey, yet runny substance with a consistency somewhere "
        "between that of paint and custard. It has ...",
        "No summary available"]

    doc_urls = soup.find_all("a", {"class": "doc_url"})
    assert len(doc_urls) == 3

    doc_url_text = [re.sub(r"\s+", " ", x.text.strip())
                    for x in doc_urls]
    assert doc_url_text == [
        "https://en.wikipedia.org/wiki/Eschweiler",
        "https://en.wikipedia.org/wiki/Gunge",
        "No url available"]


def test_html(search_client):
    """Verify HTML5 compliance in HTML portion of the search pages.

    'search_client' is a fixture function that provides a Flask test server
    interface

    Fixtures are implemented in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Create temp dir for test
    utils.create_and_clean_testdir("tmp", "test_html")
    tmpdir = pathlib.Path("tmp/test_html")

    # Validate HTML of search page before a search
    download(search_client, "/", tmpdir/"index.html")
    subprocess.run(
        [
            "html5validator", "--ignore=JAVA_TOOL_OPTIONS",
            str(tmpdir/"index.html"),
        ],
        check=True,
    )

    # Validate HTML of search page after a search with no results
    download(search_client, "/?q=&w=0.01", tmpdir/"blank_query.html")
    subprocess.run(
        [
            "html5validator", "--ignore=JAVA_TOOL_OPTIONS",
            str(tmpdir/"blank_query.html"),
        ],
        check=True,
    )

    # Validate HTML of search page after a successful search
    download(search_client, "/?q=dogs&w=0.22", tmpdir/"simple_query.html")
    subprocess.run(
        [
            "html5validator", "--ignore=JAVA_TOOL_OPTIONS",
            str(tmpdir/"simple_query.html"),
        ],
        check=True,
    )


def download(search_client, url, outpath):
    """Load url using driver and save to outputpath."""
    response = search_client.get(url)
    assert response.status_code == 200

    soup = bs4.BeautifulSoup(response.data, "html.parser")
    html = soup.prettify()

    # Write HTML of current page source to file
    outpath.write_text(html)
