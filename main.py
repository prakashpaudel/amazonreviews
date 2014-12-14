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



def avg_rating(p_ratings):
    return (p_ratings[0]*1 + p_ratings[1]*2 + p_ratings[2]*3 + p_ratings[3]*4 + p_ratings[4]*5)/(total_ratings(p_ratings)+0.0)

def total_ratings(p_ratings):
    result = 0
    for i in p_ratings:
        result += i
    return result

#This function takes in a product object and returns the rank of it as an string
def rank(p):
    rank = p.__getattr__('sales_rank')
    return int(rank) if rank else 0

def price(p):
    return p.price_and_currency[0]

def list_price(p):
    return p.product.list_price[0]

def add_data(sheet, count, data_list):
    for i in range(len(data_list)):
        sheet.write(count, i, data_list[i])


#adds variable headers to the first row of the given sheet
def add_data_headers(sheet):
    data_headers = ('a_id','name', 'type', 'category', 'rank', 'price', 'stars_1', 'stars_2', 'stars_3', 'stars_4', 'stars_5', 'rating', 'total_reviews', 'url')
    for c in range(len(data_headers)):
        sheet.write(0,c,data_headers[c])

#This function takes in a product object and returns the # of 1-5 star ratings as a list
def ratings(amzn, p):
    ratings = [0, 0, 0, 0, 0]
    has_reviews, reviews_url = p.product.reviews
    if has_reviews:
        rs = amzn.reviews(URL=p.reviews_url)
        soup = rs.soup
        div = soup.find("div","class":"crIFrameHeaderHistogram")
        if div:
            table = div.find('table')
            if table:
                
        
    return ratings
    
    
    
    
    
#     table = product.soup.find('table', id='histogramTable')
#     if table:
#         for rating, row in zip([4,3,2,1,0], table.find_all('tr', class_='a-histogram-row')):
#             # get the third td tag
#             children = [child for child in row.find_all('td', recursive=False)]
#             td = children[2]
#             data = td.find('a')
#             if data:
#                 # number could have , in it which fails during int conversion
#                 value = data.string
#                 value = value.replace(',', '')
#                 ratings[rating] = int(value)
#         return ratings
#     
#     reviews_div = product.soup.find('div', class_='reviews')
#     if reviews_div:
#         for rating, rating_class in [
#             (4, 'histoRowfive'),
#             (3, 'histoRowfour'),
#             (2, 'histoRowthree'),
#             (1, 'histoRowtwo'),
#             (0, 'histoRowone'),
#         ]:
#             rating_div = reviews_div.find('div', class_=rating_class)
#             if rating_div:
#                 # no ratings means this won't exist
#                 tag = rating_div.find('div', class_='histoCount')
#                 if tag:
#                     value = tag.string
#                     value = value.replace(',', '')
#                     ratings[rating] = int(value)
#         return ratings
#     
#     return ratings


#Main function of this program

def main():
    #user settings
    input_file_name = 'data/input.xlsx'
    output_file_name = 'data/output_data'
    input_sheet_name = 'product_list'
    output_sheet_name = 'processed_data'
    
    number_of_items = 2

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
            p_name = p.title
            p_id = p.asin
            p_ratings = ratings(amzn, p)
            p_total_ratings = total_ratings(p_ratings)
            p_avg_rating = 0 if p_total_ratings == 0 else avg_rating(p_ratings)
            p_price = price(p)
            p_list_price = list_price(p)
            p_rank = rank(p)
            p_url = p.url
            add_data(sheet_out, p_count, [p_id, p_name, product_type_list[i], search_index_list[i], p_rank, p_price, p_ratings[0], p_ratings[1], p_ratings[2], p_ratings[3], p_ratings[4], p_avg_rating, p_total_ratings, p_url])
            book_out.save(output_file_name + '_' + product_type_list[i] + '.xls') 
        
            
         
    
    
#     rs_all = []
#     rs_url = p.reviews_url
#     for i in range(0,3):
#         page = amzn.reviews(URL=rs_url)
#         time.sleep(3)
#         if(len(page.ids) != 0):
#             break
        
    #iterating through all reviews
#     for r_id in rs:
#         print r_id
    
main()
