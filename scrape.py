import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_the_verge():
    base_url = "https://www.theverge.com/archives/"
    start_date = datetime(2022, 1, 1)
    articles = []
    target_date = datetime(2022, 1, 1)

    current_date = start_date

    while True:
        year = current_date.year
        month = current_date.month
        url = f"{base_url}{year}/{month}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Save soup data to JSON for inspection
        with open(f'soup_data_{year}_{month}.json', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        new_articles = []
        for item in soup.find_all('h2'):
            title_tag = item.find('a')
            if not title_tag:
                continue

            title = title_tag.get_text()
            link = title_tag['href']

            # Check if the link is relative and prepend the base URL if necessary
            if link.startswith('/'):
                link = base_url + link

            # Attempt to find the date
            date_tag = item.find_previous('time')
            date = date_tag['datetime'] if date_tag else None

            # Convert date to datetime object for filtering
            if date:
                pub_date = datetime.fromisoformat(date.rstrip('Z'))
                # Break the loop if an article older than the target date is found
                if pub_date < target_date:
                    return articles

                new_articles.append({'title': title, 'link': link, 'date': pub_date})

        # If no new articles are found, break the loop
        if not new_articles:
            break

        articles.extend(new_articles)

        # Increment month
        next_month = current_date + timedelta(days=31)
        current_date = next_month.replace(day=1)

    # Sort articles anti-chronologically
    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles

def generate_html(articles):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Verge Titles</title>
        <style>
            body { background-color: white; color: black; font-family: Arial, sans-serif; }
            a { color: black; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>The Verge Article Titles</h1>
        <p>Below are the titles of the latest articles from The Verge. You can click each item and it will lead 
        to the article on verge.
        </p>
        <ul>
    """
    
    for article in articles:
        html_content += f'<li><a href="{article["link"]}">{article["title"]}</a></li>\n'
    
    html_content += """
        </ul>
    </body>
    </html>
    """
    
    with open('index.html', 'w') as file:
        file.write(html_content)

def main():
    articles = scrape_the_verge()
    generate_html(articles)

if __name__ == "__main__":
    main()
