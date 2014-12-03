from amazon_scraper import AmazonScraper
import warnings
from bs4 import BeautifulSoup
import time
from xlrd import open_workbook
from xlwt import Workbook               #packages for working with excel files
import xlutils
from xlrd.sheet import Sheet
import itertools

#Global defaults
warnings.filterwarnings("ignore")
AWS_ACCESS_KEY_ID = "AKIAIETM24OXNYX6EKAQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_ASSOCIATE_TAG = "personaltwi08-20"

#adds variable headers to the first row of the given sheet
def add_data_headers(sheet):
    data_headers = ('data_id','amazon_id','product_name', 'product_type', 'category', 'sub_category', 'sales_rank', 'URL')
    for c in range(len(data_headers)):
        sheet.write(0,c,data_headers[c])

#This function takes in a product object and returns the # of 1-5 star ratings as a list
def ratings(product):
    ratings = [0, 0, 0, 0, 0]
    reviews_div = product.soup.find('div', class_='reviews')
    if reviews_div:
        for rating, rating_class in [
            (4, 'histoRowfive'),
            (3, 'histoRowfour'),
            (2, 'histoRowthree'),
            (1, 'histoRowtwo'),
            (0, 'histoRowone'),
        ]:
            rating_div = reviews_div.find('div', class_=rating_class)
            if rating_div:
                # no ratings means this won't exist
                tag = rating_div.find('div', class_='histoCount')
                if tag:
                    value = tag.string
                    value = value.replace(',', '')
                    ratings[rating] = int(value)
        return ratings

    table = product.soup.find('table', id='histogramTable')
    if table:
        for rating, row in zip([4,3,2,1,0], table.find_all('tr', class_='a-histogram-row')):
            # get the third td tag
            children = [child for child in row.find_all('td', recursive=False)]
            td = children[2]
            data = td.find('a')
            if data:
                # number could have , in it which fails during int conversion
                value = data.string
                value = value.replace(',', '')
                ratings[rating] = int(value)
        return ratings

    return ratings


#Main function of this program

def main():
    #user settings
    input_file_name = 'data/raw_data_1203.xlsx'
    output_file_name = 'data/output_data.xls'
    input_sheet_name = 'raw_data'
    output_sheet_name = 'processed_data'
    

#     #Initialize from given settings
#     book_in = open_workbook(input_file_name)
#     sheet_in = book_in.sheet_by_name(input_sheet_name)
#     book_out = Workbook()
#     sheet_out = book_out.add_sheet(output_sheet_name)
#     add_data_headers(sheet_out)
#     
#     #Get list of items from excel file
#     url_list = sheet_in.col_values(8,1)
    
    
    amzn = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)    
    for p in itertools.islice(amzn.search(Keywords='toasters',SearchIndex='Kitchen'), 5):
        print p.title
    
#     for url in url_list:
#         p = amzn.lookup(URL=url)
        
    
    
    #Saving the workbook
#     book_out.save(output_file_name)
    
    #p = amzn.lookup(ItemId='B0014IKQKG')
    
    
#     for i in range(0,3):
#         rs = amzn.reviews(URL=p.reviews_url)
#         if(len(rs.ids) == 0):
#             time.sleep(3)
#         else:
#             break
#     r = amzn.review(Id=rs.ids[0])
#     
#     print r.text
    
    #print(ratings(p))

main()
