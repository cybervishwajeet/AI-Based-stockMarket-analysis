from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from rest_framework import status
import re
import os
from django.conf import settings
from .generator import (
    fetch_company_data,
    create_prompt_template,
    generate_long_report,
    generate_graph,
    generate_seaborn_graph,
    generate_pdf,
    generate_docx,
)


@api_view(["POST"])
def ai_query_view(request):
    try:
        query = request.data.get("query", "").strip()

        if not query:
            return Response({"error": "Please enter a query."}, status=400)

        ai_response = f"AI Response to: {query}"

        # Debugging output
        print(f"✅ Sending Response: {ai_response}")

        response_data = {
                "response":query,
                "confidence": 0.85,
                "sources": [{
                    "id": "1",
                    "title": "Impact on Society",
                    "url": "https://www.ibm.com/impact-on-society",
                    "type": "article",
                    "publisher": "IBM Research",
                    "date": "2025-03-20",
                    "relevance": 95,
                    "favicon": "https://www.ibm.com/favicon.ico"
                }]
            }
        print(response_data)  # Debugging
        return JsonResponse(response_data)
    except Exception as e:
        print(f"❌ Error in AI query view: {e}")  
        return Response({"error": "Something went wrong. Please try again later."}, status=500)


@api_view(["GET"])
def news_articles(request):
    category = request.GET.get("category", "")
    articles = [
        {
            "id": "1",
            "title": "AI Breakthrough in 2025",
            "source": "Tech Times",
            "summary": " major breakthrough in AI has been achieved, changing the landscape of technology.",
            "url": "https://www.techtimes.com/ai-breakthrough-2025",
            "publishedAt": datetime.datetime.now().isoformat(),
            "category": "Technology",
            "imageUrl": "https://www.techtimes.com/images/ai.jpg"
        }
    ]

    # Filter by category if provided
    if category:
        filtered_articles = [
            article for article in articles 
            if article["category"].lower() == category.lower()
        ]
    else:
        filtered_articles = articles

    # Return direct array instead of wrapped object
    return Response(filtered_articles)


@api_view(["GET"])
def search_news(request):
    query = request.GET.get("query", "")
    articles = [
        {
            "id": "1",
            "title": "AI Breakthrough in 2025",
            "source": "Tech Times",
            "summary": "A major breakthrough in AI has been achieved, changing the landscape of technology.",
            "url": "https://www.techtimes.com/ai-breakthrough-2025",
            "publishedAt": datetime.datetime.now().isoformat(),
            "category": "Technology",
            "imageUrl": "https://www.techtimes.com/images/ai.jpg"
        }
        
    ]

    if query:
        filtered_articles = [
            article for article in articles 
            if query.lower() in article["title"].lower() or 
               query.lower() in article["summary"].lower()
        ]
    else:
        filtered_articles = articles

    # Return direct array
    return Response(filtered_articles)



mock_stock_data = {
    "1d": {
        "data": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "prices": [100, 100, 100, 100, 100, 100, 100, 100],
                "dates": [
                    "9:30 AM", "10:30 AM", "11:30 AM", "12:30 PM",
                    "1:30 PM", "2:30 PM", "3:30 PM", "4:00 PM"
                ],
                "change": 6.2,
                "changePercent": 3.75,
            }
        ],
        "lastUpdated": datetime.datetime.utcnow().isoformat(),
    }
}

@api_view(["GET"])
def get_stock_data(request, time_range="1w"):
    """
    Fetch stock data based on the provided time range.
    """
    try:
        # Create more realistic mock data
        mock_stock_data = {
            "1d": {
                "data": [
                    {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "prices": [165.3, 166.1, 167.5, 168.2, 167.8, 169.1, 170.2, 171.5],
                        "dates": [
                            "tuesday", "10:30 AM", "11:30 AM", "12:30 PM",
                            "1:30 PM", "2:30 PM", "3:30 PM", "4:00 PM"
                        ],
                        "change": 6.2,
                        "changePercent": 3.75,
                    },
                    {
                        "symbol": "GOOGL",
                        "name": "Alphabet Inc.",
                        "prices": [138.5, 139.2, 140.1, 139.8, 170, 142.5, 143.1, 144.2],
                        "dates": [
                            "tuesday", "10:30 AM", "11:30 AM", "12:30 PM",
                            "1:30 PM", "2:30 PM", "3:30 PM", "4:00 PM"
                        ],
                        "change": 5.7,
                        "changePercent": 4.12,
                    }
                ],
                "lastUpdated": datetime.datetime.utcnow().isoformat()
            }
        }

        # Use the requested time range or fall back to "1d"
        data = mock_stock_data.get(time_range, mock_stock_data["1d"])
        
        return Response({
            "data": data["data"],
            "lastUpdated": data["lastUpdated"]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return Response(
            {"error": "Failed to fetch stock data"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def search_stocks(request):
    """
    Search for stocks based on a query string.
    """
    query = request.GET.get("query", "").lower()
    if not query:
        return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    results = [
        stock for stock in mock_stock_data["1w"]["data"]
        if query in stock["symbol"].lower() or query in stock["name"].lower()
    ]

    return Response(results, status=status.HTTP_200_OK)


@api_view(["POST"])
def generate_report(request):
    query = request.data.get("ticker", "").strip()
    if not query:
        return Response({"error": "No ticker provided"}, status=400)

    ticker_symbol = query
    company_data = fetch_company_data(ticker_symbol)

    if not company_data:
        print(f"❌ Could not fetch data for {ticker_symbol}. Falling back to general report.")
        user_topic = ticker_symbol
        ticker_symbol = None
        company_data = None
    else:
        user_topic = ticker_symbol
        print(f"✅ Successfully fetched data for {ticker_symbol}")

    # Generate filename
    filename = re.sub(r'[^a-zA-Z0-9_]', '', user_topic.replace(' ', '_'))[:50].lower()
    print("\nGenerating a detailed report with statistical analysis. Please wait...")

    # Generate content and graphs
    user_prompt = create_prompt_template(user_topic, ticker_symbol)
    content = generate_long_report(user_prompt, target_words=5000)
    pdf_path = generate_pdf(content, filename, company_data, ticker_symbol)

    # Move the file to MEDIA_ROOT
    media_folder = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(media_folder, exist_ok=True)
    final_pdf_path = os.path.join(media_folder, f"{filename}.pdf")
    os.rename(pdf_path, final_pdf_path)  # Move file

    # Get file details
    file_size = os.path.getsize(final_pdf_path) if os.path.exists(final_pdf_path) else 0
    file_size_str = f"{round(file_size / 1024, 2)} KB"  # Convert bytes to KB
    generated_at = datetime.datetime.now().isoformat()

    # **Fix: Generate a valid URL**
    file_url = f"{settings.MEDIA_URL}reports/{filename}.pdf"

    # Prepare response in PDFResponse format
    response_data = {
        "url": request.build_absolute_uri(file_url),  # Converts to a full URL
        "fileName": f"{filename}.pdf",
        "generatedAt": generated_at,
        "fileSize": file_size_str,
    }

    return Response(response_data, status=200)