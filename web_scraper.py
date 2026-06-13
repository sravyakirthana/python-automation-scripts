"""
Business Leads Web Scraper
===========================
Scrapes business info (name, address, phone, website) from public directories.
Usage: python web_scraper.py --keyword "restaurants" --city "Hyderabad" --pages 3
Output: leads.csv (ready to hand to client!)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
import random

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_yellow_pages(keyword, city, pages=2):
    """Scrape business leads from YellowPages-style public listings."""
    leads = []
    keyword_slug = keyword.replace(' ', '+')
    city_slug = city.replace(' ', '+')

    print(f"\n🔍 Searching: '{keyword}' in '{city}'")
    print(f"📄 Scraping {pages} pages...\n")

    for page in range(1, pages + 1):
        url = f"https://www.yellowpages.com/search?search_terms={keyword_slug}&geo_location_terms={city_slug}&page={page}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('div', class_='result')

            if not listings:
                print(f"  ⚠️  No listings found on page {page} (site may block scrapers, try local sites)")
                break

            for item in listings:
                name = item.find('a', class_='business-name')
                phone = item.find('div', class_='phones')
                address = item.find('div', class_='street-address')
                locality = item.find('div', class_='locality')
                website = item.find('a', class_='track-visit-website')

                leads.append({
                    'Business Name': name.text.strip() if name else '',
                    'Phone': phone.text.strip() if phone else '',
                    'Address': (address.text.strip() if address else '') + ' ' + (locality.text.strip() if locality else ''),
                    'Website': website['href'] if website else '',
                    'Keyword': keyword,
                    'City': city
                })

            print(f"  ✅ Page {page}: Found {len(listings)} listings")
            time.sleep(random.uniform(1.5, 3.0))  # polite delay

        except Exception as e:
            print(f"  ❌ Error on page {page}: {e}")
            continue

    return leads


def scrape_demo_data(keyword, city, pages):
    """Generates sample leads data to demonstrate the script output format."""
    print(f"\n📦 Generating DEMO leads for '{keyword}' in '{city}'...")
    print("  (In real projects, point this at a client-specified public site)\n")

    sample_businesses = [
        ("Star Cafe", "+91 98765 43210", "MG Road, Hyderabad", "www.starcafe.in"),
        ("Green Bites Restaurant", "+91 91234 56789", "Banjara Hills, Hyderabad", ""),
        ("TechHub Solutions", "+91 99887 76655", "HITEC City, Hyderabad", "www.techhub.co.in"),
        ("Quick Mart Store", "+91 88776 65544", "Ameerpet, Hyderabad", ""),
        ("Sunrise Pharmacy", "+91 77665 54433", "Secunderabad, Hyderabad", "www.sunrisepharma.com"),
        ("Royal Catering Services", "+91 66554 43322", "Kukatpally, Hyderabad", ""),
        ("BlueSky Travels", "+91 55443 32211", "Jubilee Hills, Hyderabad", "www.bluesky.in"),
        ("City Dental Clinic", "+91 44332 21100", "Dilsukhnagar, Hyderabad", ""),
        ("Spice Garden Hotel", "+91 33221 10099", "Charminar, Hyderabad", "www.spicegarden.com"),
        ("Swifty Courier", "+91 22110 09988", "LB Nagar, Hyderabad", ""),
    ]

    leads = []
    for i, (name, phone, address, website) in enumerate(sample_businesses * pages):
        leads.append({
            'Business Name': name,
            'Phone': phone,
            'Address': address,
            'Website': website,
            'Keyword': keyword,
            'City': city
        })

    return leads[:pages * 10]


def main():
    parser = argparse.ArgumentParser(description='Scrape business leads from the web')
    parser.add_argument('--keyword', default='restaurants', help='Type of business to search')
    parser.add_argument('--city', default='Hyderabad', help='City to search in')
    parser.add_argument('--pages', type=int, default=2, help='Number of pages to scrape')
    parser.add_argument('--output', default='leads.csv', help='Output CSV filename')
    parser.add_argument('--demo', action='store_true', help='Run with demo data (no internet needed)')
    args = parser.parse_args()

    # Get leads
    if args.demo:
        leads = scrape_demo_data(args.keyword, args.city, args.pages)
    else:
        leads = scrape_yellow_pages(args.keyword, args.city, args.pages)

    if not leads:
        print("❌ No leads found. Try --demo mode or a different keyword.")
        return

    # Save to CSV
    df = pd.DataFrame(leads)
    df.drop_duplicates(subset=['Business Name', 'Phone'], inplace=True)
    df.to_csv(args.output, index=False)

    print(f"\n📊 RESULTS SUMMARY")
    print(f"  Total Leads Found : {len(df)}")
    print(f"  With Phone Numbers: {df['Phone'].astype(bool).sum()}")
    print(f"  With Websites     : {df['Website'].astype(bool).sum()}")
    print(f"  Saved To          : {args.output}")
    print(f"\n🎉 Done! Share '{args.output}' with your client.")


if __name__ == "__main__":
    main()
