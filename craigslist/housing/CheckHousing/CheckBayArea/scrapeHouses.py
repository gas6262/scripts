#import get to call a get request on the site
from argparse import ArgumentError
from requests import get
from bs4 import BeautifulSoup
from dateutil import parser
import cleanUtils as clean
import dbUtils

# Get the listings using a craigslist URL
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

def tryIntConvertInt(val):

    valInt = None

    try:
        valInt = int(val)
        print(f"Integer conversion succeeded: {valInt}")
    except ValueError:
        print("Int Conversion failed")
    
    return valInt

# Apply an integer filter
def applyIntFilter(post, key, operator, comparatorInt):

    if(post[key] == None):
        return False

    postVal = int(post[key])
    
    if operator == '>':
        return postVal > comparatorInt
    elif operator == '=':
        return postVal == comparatorInt
    elif operator == '<':
        return postVal < comparatorInt
    else:
        raise ArgumentError(f'Invalid operator {operator}')

def applyStringFilter():
    raise NotImplementedError(f'applyStringFilter is not implemented yet')

def filterPostByAll(post, filters):
            
    for filter in filters:
        
        # Apply the specific filters
        for key, condition in filter.items():
            
            res = False
            operator = condition[0]
            comparator = condition[1:]

            comparatorInt = tryIntConvertInt(comparator)

            if(comparatorInt):
                res = applyIntFilter(post, key, operator, comparatorInt)
            else:
                res = applyStringFilter()
            if(res == False):
                return res
    
    return True


# Filter out posts that do not meet the criteria specified in filters
def applyFilters(posts, filters):

    filteredPosts = []

    # Iterate through posts
    for post in posts:
        res = filterPostByAll(post, filters)

        if(res):
            filteredPosts.append(post)

    return filteredPosts

# Method specifically for South Bay
def collectSouthBayPosts(filters):
    searchUrl = r'https://sfbay.craigslist.org/d/rooms-shares/search/sby/roo?availabilityMode=0&s=334'

    filters = [
        {
            "rooms" : ">3",
            "price" : ">3000"
        }
    ]

    posts = getHousingArray(searchUrl)
    filteredPosts = applyFilters(posts, filters)    

    dbUtils.insertPosts(filteredPosts)
    mailPosts
    print(f"Completed CL entry insertion")

# Method specifically for Tahoe
def collectTahoeRentals():

    searchUrl = r'https://reno.craigslist.org/d/apartments-housing-for-rent/search/apa?query=south%20lake%20tahoe'
    posts = getHousingArray(searchUrl)

    print(f"Completed CL entry insertion")

if __name__ == "__main__":

    filters = [
        {
            "rooms" : ">3",
            "price" : ">3000"
        }
    ]

    collectSouthBayPosts(filters)