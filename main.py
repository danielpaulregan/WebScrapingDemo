import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize, word_tokenize

# Create a user agent
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

# Try switching "URL" on line 31 to see data scraped from different pages. 
# Amazon product page showing reviews. Sorted by critical. This can currently only handle the first page of reviews since the others require a solution for scraping dynamic page content
URL = "https://www.amazon.com/054H-Cartridge-Compatible-Replacement-ImageClass/product-reviews/B0BFHJ1WQG/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1"
URL2="https://www.amazon.com/product-reviews/B01LR5S6HK/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=critical&reviewerType=all_reviews&pageNumber=1"
URL3="https://www.amazon.com/product-reviews/B074P8MZW9/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=critical&reviewerType=all_reviews&pageNumber=1"

# Define a class to hold a review and its associated data
class Review:
    def __init__(self, text, userName, locationAndDate, userRating, reviewTitle):
        self.text = text
        self.userName = userName
        self.locationAndDate = locationAndDate
        self.userRating = userRating
        self.reviewTitle = reviewTitle


### SCRAPING CODE

# Download the page HTML
page = requests.get(URL, headers=HEADERS)

# Use BeautifulSoup to load the HTML document and parse for review data
soup = BeautifulSoup(page.content, "html.parser")

# Locate the reviews on the page
reviewsOnPage = soup.select(".review-text")

reviews = []

for review in reviewsOnPage:
    # Get the parent element of the review
    reviewParent = review.parent.parent

    # Save (scrape) the review text into an object and add it to our list
    reviewText = review.get_text()

    # Extract the user's name from the review
    userName = reviewParent.find("span", {"class":"a-profile-name"}).get_text()

    # Extract the location and date of the review
    locationAndDate = reviewParent.find("span", {"class":"review-date"}).get_text()

    # Extract the user's rating
    userRating = reviewParent.find("span", {"class":"a-icon-alt"}).get_text()

    # Extract the review title
    reviewTitleUnformatted = reviewParent.find("a", {"class":"review-title"}).get_text()
    reviewTitleWords = word_tokenize(reviewTitleUnformatted)
    reviewTitle = ""

    # Need to cut out unwanted text from the review title
    for idx, word in enumerate(reviewTitleWords):
        if idx > 4:
            reviewTitle += word + " "

    # Store the data in a Review object and append it to our list
    reviewObj = Review(reviewText, userName, locationAndDate, userRating, reviewTitle)
    reviews.append(reviewObj)

### ANALYSIS AND OUTPUT CODE

# After gathering all review data on the page, create an analyzer which we can use for sentiment analysis
analyzer = SentimentIntensityAnalyzer()

# For every review we scraped, calculate the most negative sentence, and the sentiment score (-1 to 1)
for review in reviews:
    sentences = sent_tokenize(review.text)

    mostNegativeScore = 1.0
    mostNegativeSentence = ""

    for sentence in sentences:
        sentimentScore = analyzer.polarity_scores(sentence)
        
        if float(sentimentScore['compound']) < mostNegativeScore:
            mostNegativeScore = float(sentimentScore['compound'])
            mostNegativeSentence = sentence

    #print(review)
    print("User Name: " + review.userName)
    print("Location and Date: " + review.locationAndDate)
    print("User Rating: " + review.userRating)
    print("Review Title: " + review.reviewTitle)
    print("Most negative sentence: " + mostNegativeSentence + "\nSentiment score [-1,1]: " + str(mostNegativeScore) + "\n")