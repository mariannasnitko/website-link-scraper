import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import csv


# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0


def is_valid(url):
    
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
   
    # returns all URLs that is found on `url` in which it belongs to the same website
    
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        page = requests.get(url)
        rel = a_tag.attrs.get("rel")
        domain_name = urlparse(url).netloc

        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"External link: {href} {url} {page.status_code} {a_tag.string} {rel}")
                with open(f"{domain_name}_all_links.csv", "a") as f:
                        f.write('External,{},{},{},{},{}\n'.format(url, href, requests.get(href), a_tag.string, rel))
                external_urls.add(href)
            continue
        print(f"Internal link: {href} {url} {page.status_code} {a_tag.string} {rel}")
        with open(f"{domain_name}_all_links.csv", "a") as f:
                f.write('Internal,{},{},{},{},{}\n'.format(url, href, requests.get(href), a_tag.string, rel))
        urls.add(href)
        internal_urls.add(href)
    return urls


def crawl(url, max_urls=200):
    
    global total_urls_visited
    total_urls_visited += 1
    print(f"Crawling: {url}")
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    parser.add_argument("url", help="The URL to extract links from.")
    parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=30, type=int)
    
    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls

    crawl(url, max_urls=max_urls)

    print("Total Internal links:", len(internal_urls))
    print("Total External links:", len(external_urls))
    print("Total URLs:", len(external_urls) + len(internal_urls))
    print("Total crawled URLs:", max_urls)