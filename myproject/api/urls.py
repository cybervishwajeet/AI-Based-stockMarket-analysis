from django.urls import path
from .views import ai_query_view,news_articles,search_news,get_stock_data,search_stocks,generate_report

urlpatterns = [
    path("ai/query/", ai_query_view, name="ai-search"),
    path('news/search/', news_articles, name='news-list'),
    path('news/articles/', search_news, name='news-search'),
    path("stocks/data/", get_stock_data, name="get_stock_data"),
    path("stocks/search/", search_stocks, name="search_stocks"),
    path("stocks/generate-finance-document/",generate_report, name="generate_finance_document"),
    
]
