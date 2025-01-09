from nyt_api import NYTNews
import os
from dotenv import load_dotenv

load_dotenv()

nyt_news = NYTNews(os.getenv("NYT_API_KEY"))
res = nyt_news.get_archives("junk", "2024-11", "2024-11")
print(res)