import time

from selenium import webdriver


def fetch_image_urls_from_google(query: str, wd: webdriver, sleep_between_interactions: int = 1):
    """
    Fetches all the urls of images found on the first result page for received search query.

    :param query:                         query to search for
    :param wd:                            selenium web driver
    :param sleep_between_interactions:    time for browser to load photos
    :return:                              set of found urls
    """

    # Google search - large images
    search_url = "https://www.google.com/search?q={q}&tbm=isch&hl=en-US&hl=en-US&tbs=isz%3Al&client=ubuntu&hs=hdu&ved" \
                 "=0CAEQpwVqFwoTCKDZh9KqmOgCFQAAAAAdAAAAABAD&biw=1908&bih=955 "
    image_urls = set()

    # load the page
    wd.get(search_url.format(q=query))
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(sleep_between_interactions)
    # get all image thumbnail results
    thumbnails = wd.find_elements_by_css_selector("img.Q4LuWd")

    for thumbnail in thumbnails:
        try:
            # get big image from the thumbnail
            thumbnail.click()
            time.sleep(sleep_between_interactions)
        except Exception:
            continue

        # extract image urls
        images = wd.find_elements_by_css_selector('img.n3VNCb')
        for img in images:
            if img.get_attribute('src') and 'http' in img.get_attribute('src'):
                image_urls.add(img.get_attribute('src'))

    print(f"Found: {len(image_urls)} image links for the search query: {query}")

    return image_urls
