#import get to call a get request on the site
from requests import get
from bs4 import BeautifulSoup
from dateutil import parser
from . import cleanUtils as clean
from . import dbUtils

def getHousingArray(searchUrl):

    # get the first page of the east bay housing prices
    print(f"Calling craigslist for results: {searchUrl}")
    response = get(searchUrl) #get rid of those lame-o's that post a housing option without a pic using their filter
    html_soup = BeautifulSoup(response.text, 'html.parser')
    print("Obtained results from Craigslist")

    #get the macro-container for the housing postsHTML
    postsHTML = html_soup.find_all('li', class_= 'result-row')
    print(f"Obtained {len(postsHTML)} posts from CL")

    skippedPosts = 0
    posts = []

    for post in postsHTML:

        try:
            main = post.find('a', class_='result-title hdrlnk')

            title = main.text
            link = main['href']
            price = clean.getPrice(post.find('span', class_='result-price').text)
            date = parser.parse(post.find('time', class_='result-date')['datetime'])
            day = parser.parse(post.find('time', class_='result-date').text)
            hood = clean.cleanHood(post.find('span', class_='result-hood').text)

            housing = clean.getHousing(post)
            h = clean.getPostId(date, title)

            post_info = {
                "PartitionKey" : hood,
                "RowKey" : h,

                "date": date,
                "title": title,
                "link": link,
                "price": price,
                "hood": hood,

                "rooms": housing['br'],
                "size": housing['size']
            }

            posts.append(post_info)

        except Exception as e:
            skippedPosts += 1
            print(f'Failed to parse or insert post. Skipping ({skippedPosts})\n\n{e}\n\n{str(post)}\n')

    return posts

def collectSouthBayPosts():
    searchUrl = r'https://sfbay.craigslist.org/d/rooms-shares/search/sby/roo?availabilityMode=0&s=334'

    posts = getHousingArray(searchUrl)

    dbUtils.insertPosts(posts)
    print(f"Completed CL entry insertion")

def collectTahoeRentals():

    searchUrl = r'https://reno.craigslist.org/d/apartments-housing-for-rent/search/apa?query=south%20lake%20tahoe'

    posts = getHousingArray(searchUrl)

    dbUtils.insertPosts(posts)
    print(f"Completed CL entry insertion")

if __name__ == "__main__":
    collectSouthBayPosts()