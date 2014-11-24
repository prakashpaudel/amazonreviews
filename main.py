from amazon_scraper import AmazonScraper
import warnings

warnings.filterwarnings("ignore")

AWS_ACCESS_KEY_ID = "AKIAIETM24OXNYX6EKAQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_ASSOCIATE_TAG = "personaltwi08-20"


a = AmazonScraper(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)

p = a.lookup(ItemId='B0014IKQKG')
rs = a.reviews(URL=p.reviews_url)
r = a.review(Id=rs.ids[0])

##from amazon.api import AmazonAPI
##from bottlenose import Amazon
##
##
##a = AmazonAPI(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
##
##p = a.Reviews(ItemId='B00EOE0WKQ')
