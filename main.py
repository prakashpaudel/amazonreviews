from amazon_scraper import AmazonScraper
import warnings
from bs4 import BeautifulSoup
import time
from xlrd import open_workbook
from xlwt import Workbook               #packages for working with excel files
import xlutils
from xlrd.sheet import Sheet
import itertools
from types import NoneType

#Global defaults
warnings.filterwarnings("ignore")

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

#This function takes in a product object and returns the # of 1-5 star ratings as a list
def ratings(amzn, p):
    ratings = [0, 0, 0, 0, 0]
    has_reviews = p.product.reviews[0]
    if has_reviews:
        rs = amzn.reviews(URL=p.reviews_url)
        rs_soup = rs.soup
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

def data(amzn, p, p_type, p_category):
    p_name = p.title
    p_id = p.asin
    p_ratings = ratings(amzn, p)
    p_total_ratings = total_ratings(p_ratings)
    p_avg_rating = 0 if p_total_ratings == 0 else avg_rating(p_ratings)
    p_price = p.product.price_and_currency[0]
    p_list_price = p.product.list_price[0]
    p_rank = rank(p)
    p_url = p.url
    p_isPrime = isPrime(p)
    p_releaseDate = releaseDate(p)
    return [p_type, p_category, p_id, p_name, p_rank, p_price, p_list_price, p_isPrime,
            p_ratings[0], p_ratings[1], p_ratings[2], p_ratings[3], p_ratings[4],
            p_avg_rating, p_total_ratings,
            p_url]

#adds variable headers to the first row of the given sheet
def add_data_headers(sheet):
    data_headers = ('type', 'category', 'a_id','name', 'rank', 'price', 'list_price', 'prime',
                    'stars_1', 'stars_2', 'stars_3', 'stars_4', 'stars_5', 'rating', 'num_reviews',
                    'url')
    for c in range(len(data_headers)):
        sheet.write(0,c,data_headers[c])


#Main function of this program
def main():
    #user settings
    input_file_name = 'data/input.xlsx'
    output_file_name = 'data/output_data'
    input_sheet_name = 'product_list'
    output_sheet_name = 'processed_data'
    
    number_of_items = 5

    #Initialize from given settings
    book_in = open_workbook(input_file_name)
    sheet_in = book_in.sheet_by_name(input_sheet_name)
    
    #Get list of items from excel file
    search_index_list = sheet_in.col_values(0,1)
    product_type_list = sheet_in.col_values(1,1)
    
    amzn = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
    #iterate through products
    for i in range(len(product_type_list)):
        #intialize for each product_type_list
        book_out = Workbook()
        sheet_out = book_out.add_sheet(output_sheet_name)
        add_data_headers(sheet_out)
        p_count = 0
        #iterate through items
        for p in itertools.islice(amzn.search(Keywords=product_type_list[i],SearchIndex=search_index_list[i]), number_of_items):
            p_count += 1
            print 'Processing', product_type_list[i], p_count
            p_data = data(amzn, p, product_type_list[i], search_index_list[i])
            add_data(sheet_out, p_count, p_data)
            book_out.save(output_file_name + '_' + product_type_list[i] + '.xls')
    
main()
