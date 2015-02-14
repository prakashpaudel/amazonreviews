from amazon_scraper import AmazonScraper, user_agent
import warnings
from bs4 import BeautifulSoup
import time
from xlrd import open_workbook
from xlwt import Workbook               #packages for working with excel files
import xlutils
from xlrd.sheet import Sheet
import itertools
from types import NoneType
import requests

#Global defaults
warnings.filterwarnings("ignore")
AWS_ACCESS_KEY_ID = "AKIAJ7B6ZL65HM7GQWEQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_ASSOCIATE_TAG = "personaltwi08-20"

def shipping(p):
    result = p.product._safe_get_element_text('Offers.Offer.OfferListing.Availability')
    return result

def releaseDate(p):
    date = p.product._safe_get_element_text('SellerListing.StartDate')
    print date

def isPrime(p):
    isPrime = p.product._safe_get_element_text('Offers.Offer.OfferListing.IsEligibleForSuperSaverShipping')
    return int(isPrime) if isPrime else 0

def avg_rating(p_ratings):
    return (p_ratings[0]*1 + p_ratings[1]*2 + p_ratings[2]*3 + p_ratings[3]*4 + p_ratings[4]*5)/(total_ratings(p_ratings)+0.0)

def total_ratings(p_ratings):
    result = 0
    for i in p_ratings:
        result += i
    return result

#This function takes in a product object and returns the rank of it as an string
def rank(p):
    rank = p.product.sales_rank
    return int(rank) if rank else 0

def add_data(sheet, count, data_list):
    for i in range(len(data_list)):
        sheet.write(count, i, data_list[i])

def recent_ratings(amzn, p, rs_soup):
#     ratings = [0, 0, 0, 0, 0]
#     rating_list = []
    ids = []
    if rs_soup:
        reviews_div = rs_soup.find('table', id='productReviews')
        if reviews_div:
            td = reviews_div.find('td')
            if td:
                for a in td.find_all('a',recursive=False):
                    ids.append(a['name']+',')
    return ids
    
    
#     ratings = [0, 0, 0, 0, 0]
#     rating_list = []
#     page = amzn.reviews(URL=p.reviews_url)
#     for r_id in page.ids:
#         r = amzn.review(Id=r_id)
#         rating_list.append(r.rating)
#     for rating in rating_list:
#         if(rating == .2): ratings[0] +=1
#         if(rating == .4): ratings[1] +=1
#         if(rating == .6): ratings[2] +=1
#         if(rating == .8): ratings[3] +=1
#         if(rating == 1.0): ratings[4] +=1
#     return ratings

def helpful_ratings(amzn, p, rs_soup):
#     ratings = [0, 0, 0, 0, 0]
#     rating_list = []
    ids = []
    if rs_soup:
        reviews_div = rs_soup.find('table', id='productReviews')
        if reviews_div:
            td = reviews_div.find('td')
            if td:
                for a in td.find_all('a',recursive=False):
                    ids.append(a['name']+',')
#     
#     for id in ids:
#         r = amzn.review(Id=id)
#         rating_list.append(r.rating)
#     for rating in rating_list:
#         if(rating == .2): ratings[0] +=1
#         if(rating == .4): ratings[1] +=1
#         if(rating == .6): ratings[2] +=1
#         if(rating == .8): ratings[3] +=1
#         if(rating == 1.0): ratings[4] +=1
    return ids    



#This function takes in a product object and returns the # of 1-5 star ratings as a list
def all_ratings(amzn, p, rs_soup):
    ratings = [0, 0, 0, 0, 0]
    if rs_soup:
        summary = rs_soup.find('table', id='productSummary')
        if summary:
            table = summary.find('table')
            if table:
                for rating, row in zip([4,3,2,1,0], table.find_all('tr')):
                    children = [child for child in row.find_all('td', recursive=False)]
                    td = children[2]
                    value = td.string
                    value = value[2:-1]
                    value = value.replace(',', '')
                    ratings[rating] = int(value)
    return ratings

def reviewdata(amzn, p, p_url):
    ratings = [0, 0, 0, 0, 0]
    recent_ids = []
    helpful_ids = []
     
    soup = my_soup(p_url)
    if soup:
        container = soup.find('div', id='reviewContainer')
        if container:
            #ratings
            table = container.find('table', id='histogramTable')
            if table:
                for rating, row in zip([4,3,2,1,0], table.find_all('tr', class_='a-histogram-row')):
                # get the third td tag
                    children = [child for child in row.find_all('td', recursive=False)]
                    td = children[2]
                    data = td.text
                    if data:
                        # number could have , in it which fails during int conversion
                        value = str(data)
                        value = value[2:]
                        value = value.replace(',', '').replace(' ','')
                        ratings[rating] = int(value)
            #helpful
            div = container.find('div', id='revMHRL')
            if div:
                for row in div.find_all('div', recursive=False):
                    helpful_ids.append(row['id'].split('-')[2]+',')
            #recent
            div = container.find('div', id='revMRRL')
            if div:
                for row in div.find_all('div', recursive=False):
                    a = row.find('a')
                    recent_ids.append(a['href'].split('#')[-1]+',')
        else:
            reviews_url = p.reviews_url
            rrs_soup = my_soup(reviews_url)
            url_split = reviews_url.split('/')
            url_split[5] = url_split[5].replace('recent','helpful').replace('SubmissionDate','Rank')
            p_helpful_url = "/".join(str(bit) for bit in url_split)
            hrs_soup = my_soup(p_helpful_url)
             
            ratings = all_ratings(amzn, p, rrs_soup)
            helpful_ids = helpful_ratings(amzn, p, hrs_soup)
            recent_ids = recent_ratings(amzn, p, rrs_soup)
            
    return ratings, recent_ids, helpful_ids        

def my_soup(url):
    html = requests.get(url, headers={'User-Agent':user_agent}, verify=False)
    html.raise_for_status()
    return BeautifulSoup(html.text, 'html5lib')

def data(amzn, p, p_category):
    p_name = p.title
    p_id = p.asin
    p_price = p.product.price_and_currency[0]
    p_list_price = p.product.list_price[0]
    p_rank = rank(p)
    p_shipping = shipping(p)
    
    #reviews and ratings
    p_url = p.url
    p_ratings, p_recent_ids, p_helpful_ids = reviewdata(amzn, p, p_url)
    p_total_ratings = total_ratings(p_ratings)
    p_avg_rating = 0 if p_total_ratings == 0 else avg_rating(p_ratings)
    
    return [p_category, p_id, p_name, p_rank, p_price, p_list_price, p_shipping, 
            p_ratings[0], p_ratings[1], p_ratings[2], p_ratings[3], p_ratings[4],
            p_avg_rating, p_total_ratings,
            p_recent_ids, p_helpful_ids,
            p_url]

#adds variable headers to the first row of the given sheet
def add_data_headers(sheet):
    data_headers = ('category', 'id', 'name', 'rank', 'price', 'list_price', 'shipping',
                    'stars_1', 'stars_2', 'stars_3', 'stars_4', 'stars_5', 'rating', 'num_reviews',
                    'recent_ids', 'helpful_ids',
                    'url')
    for c in range(len(data_headers)):
        sheet.write(0,c,data_headers[c])

def reviewmain():
    input_file_name = 'data/reviews.xlsx'
    output_file_name = 'data/reviews_out'
    input_sheet_name = 'reviews'
    output_sheet_name = 'reviews'
    
    #Initialize from given settings
    book_in = open_workbook(input_file_name)
    sheet_in = book_in.sheet_by_name(input_sheet_name)
    
    amzn = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    book_out = Workbook()
    sheet_out = book_out.add_sheet(output_sheet_name)
    
    ids = sheet_in.col_values(0,1)
    
    io = input('starting point?')
    i = io
    
    
    while i < len(ids):
        row = ids[i][:-1]
        print 'Item ',i+1
        result = 0
        count = 0.0
        for j in row.split(','):
            r = amzn.review(Id=j)
            count +=1
            result += r.rating*5
        add_data(sheet_out, i, [result/count])
        book_out.save(output_file_name + 'helpdec19.xls')
        i += 1
    
    



#Main function of this program
def main():
    #user settings
    input_file_name = 'data/input.xlsx'
    output_file_name = 'data/output_data'
    input_sheet_name = 'product_list'
    output_sheet_name = 'processed_data'
    
    number_of_items = 100

    #Initialize from given settings
    book_in = open_workbook(input_file_name)
    sheet_in = book_in.sheet_by_name(input_sheet_name)
    
    #Get list of items from excel file
    ids = sheet_in.col_values(0,1)
    product_types = sheet_in.col_values(1,1)
    
    io = input('starting point?')
    i = io
    amzn = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    book_out = Workbook()
    sheet_out = book_out.add_sheet(output_sheet_name)
    add_data_headers(sheet_out)
    p_count = 0
    
    #iterate through items
    while i < len(ids):
        p = amzn.lookup(ItemId=ids[i])
        p_count += 1
        print 'Processing', p_count
        p_data = data(amzn, p, product_types[i])
        add_data(sheet_out, p_count, p_data)
        book_out.save(output_file_name + '_' + product_types[i] + '3.xls')
        i = i+1
# #Main function of this program
# def main():
#     #user settings
#     input_file_name = 'data/input.xlsx'
#     output_file_name = 'data/output_data'
#     input_sheet_name = 'product_list'
#     output_sheet_name = 'processed_data'
#     
#     number_of_items = 100
# 
#     #Initialize from given settings
#     book_in = open_workbook(input_file_name)
#     sheet_in = book_in.sheet_by_name(input_sheet_name)
#     
#     #Get list of items from excel file
#     search_indices = sheet_in.col_values(0,1)
#     product_types = sheet_in.col_values(1,1)
#     browse_nodes = sheet_in.col_values(2,1)
#     for i in range(len(browse_nodes)):
#         browse_nodes[i] = int(browse_nodes[i])
#     
#     amzn = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
#     #iterate through products
#     i,j = 0,0
#     io = input('category number?')
#     if isinstance(io,int):
#         i = io
#     else:
#         i,j = io
#     #intialize for each product_types
#     book_out = Workbook()
#     sheet_out = book_out.add_sheet(output_sheet_name)
#     add_data_headers(sheet_out)
#     p_count = 0
#     #iterate through items
#     for p in itertools.islice(amzn.search(BrowseNode=browse_nodes[i],
#                                           SearchIndex=search_indices[i],
#                                           Sort='salesrank',
#                                           MerchantId='Amazon',
#                                           Availability='Available',
#                                           ),number_of_items):
#         p_count += 1
#         if p_count >= j:
#             print 'Processing', product_types[i], p_count
#             p_data = data(amzn, p, product_types[i])
#             add_data(sheet_out, p_count, p_data)
#             book_out.save(output_file_name + '_' + product_types[i] + '.xls')
    
# main()



reviewmain()
