#!/usr/bin/env python3
"""
Universal Scraper Examples
Demonstrates how to use the multi-purpose scraping tool for different search types
"""

import asyncio
import json
from universal_scraper import UniversalSearchRequest, SearchType, ExtractionMode, universal_scraper

async def example_product_search():
    """Example: Search for products (oak furniture)"""
    print("=== PRODUCT SEARCH EXAMPLE ===")
    print("Searching for oak furniture in Kaunas...")
    
    request = UniversalSearchRequest(
        search_type=SearchType.PRODUCT,
        primary_query="oak furniture Kaunas",
        secondary_queries=["oak table Kaunas", "oak chair Kaunas"],
        regions=["Lithuania", "Kaunas"],
        include_keywords=["oak", "furniture", "table", "chair"],
        exclude_keywords=["blog", "news", "article"],
        max_results=20,
        extraction_mode=ExtractionMode.DETAILED,
        type_specific_params={
            "price_range": {"min": 50, "max": 2000},
            "categories": ["furniture", "home", "decor"]
        },
        output_formats=["json", "csv", "excel"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"✅ Found {results['total_results']} products")
    print(f"📁 Exported to: {list(results['output_files'].values())}")
    
    # Show sample results
    if results['results']:
        sample = results['results'][0]
        print(f"📦 Sample product: {sample.get('name', 'Unknown')}")
        if 'price_amount' in sample:
            print(f"💰 Price: {sample.get('price_currency', '')} {sample.get('price_amount', 'N/A')}")
    
    return results

async def example_company_search():
    """Example: Search for companies (IT companies in Lisburn)"""
    print("\n=== COMPANY SEARCH EXAMPLE ===")
    print("Searching for IT companies in Lisburn...")
    
    request = UniversalSearchRequest(
        search_type=SearchType.COMPANY,
        primary_query="IT companies Lisburn",
        secondary_queries=["software companies Lisburn", "tech firms Lisburn"],
        regions=["Northern Ireland", "Belfast", "Lisburn"],
        cities=["Lisburn", "Belfast"],
        include_keywords=["IT", "software", "technology", "development"],
        exclude_keywords=["jobs", "careers", "recruitment"],
        max_results=15,
        extraction_mode=ExtractionMode.DETAILED,
        type_specific_params={
            "company_size": ["small", "medium", "large"],
            "industries": ["IT", "software", "technology"]
        },
        output_formats=["json", "csv"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"✅ Found {results['total_results']} companies")
    print(f"📁 Exported to: {list(results['output_files'].values())}")
    
    # Show sample results
    if results['results']:
        sample = results['results'][0]
        print(f"🏢 Sample company: {sample.get('name', 'Unknown')}")
        print(f"📍 Location: {sample.get('location', 'N/A')}")
        print(f"💼 Industry: {sample.get('industry', 'N/A')}")
    
    return results

async def example_person_search():
    """Example: Search for people (person from public database)"""
    print("\n=== PERSON SEARCH EXAMPLE ===")
    print("Searching for people in public databases in Dubai...")
    
    request = UniversalSearchRequest(
        search_type=SearchType.PERSON,
        primary_query="business executives Dubai public directory",
        secondary_queries=["CEO Dubai public profile", "director Dubai business"],
        regions=["UAE", "Dubai"],
        cities=["Dubai"],
        include_keywords=["executive", "director", "CEO", "public", "profile"],
        exclude_keywords=["private", "personal", "blog"],
        max_results=10,
        extraction_mode=ExtractionMode.BASIC,  # Only public information
        type_specific_params={
            "public_only": True,
            "profession_types": ["executive", "director", "manager"]
        },
        output_formats=["json", "csv"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"✅ Found {results['total_results']} public profiles")
    print(f"📁 Exported to: {list(results['output_files'].values())}")
    
    # Show sample results
    if results['results']:
        sample = results['results'][0]
        print(f"👤 Sample person: {sample.get('name', 'Unknown')}")
        print(f"💼 Profession: {sample.get('profession', 'N/A')}")
        print(f"🏢 Company: {sample.get('company', 'N/A')}")
    
    return results

async def example_social_media_search():
    """Example: Search for social media accounts"""
    print("\n=== SOCIAL MEDIA SEARCH EXAMPLE ===")
    print("Searching for tech startup social media accounts...")
    
    request = UniversalSearchRequest(
        search_type=SearchType.SOCIAL_MEDIA,
        primary_query="tech startup Ireland social media",
        secondary_queries=["startup Dublin Twitter", "tech company LinkedIn Ireland"],
        regions=["Ireland"],
        include_keywords=["startup", "tech", "technology", "innovation"],
        exclude_keywords=["fake", "spam", "bot"],
        max_results=15,
        extraction_mode=ExtractionMode.DETAILED,
        type_specific_params={
            "platforms": ["twitter", "linkedin", "instagram"],
            "account_types": ["business", "company", "startup"]
        },
        output_formats=["json", "csv"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"✅ Found {results['total_results']} social media accounts")
    print(f"📁 Exported to: {list(results['output_files'].values())}")
    
    # Show sample results
    if results['results']:
        sample = results['results'][0]
        print(f"📱 Sample account: {sample.get('username', 'Unknown')}")
        print(f"🌐 Platform: {sample.get('platform', 'N/A')}")
        print(f"🔗 Profile: {sample.get('profile_url', 'N/A')}")
    
    return results

async def example_email_search():
    """Example: Search for email addresses"""
    print("\n=== EMAIL SEARCH EXAMPLE ===")
    print("Searching for business contact emails...")
    
    request = UniversalSearchRequest(
        search_type=SearchType.EMAIL,
        primary_query="tech companies contact email Ireland",
        secondary_queries=["startup contact Dublin", "IT company email Belfast"],
        regions=["Ireland", "Northern Ireland"],
        include_keywords=["contact", "email", "info", "business"],
        exclude_keywords=["noreply", "no-reply", "spam"],
        max_results=10,
        extraction_mode=ExtractionMode.DETAILED,
        type_specific_params={
            "email_types": ["business", "contact", "info"],
            "domains_only": False
        },
        output_formats=["json", "csv"]
    )
    
    results = await universal_scraper.search_and_scrape(request)
    
    print(f"✅ Found {results['total_results']} email addresses")
    print(f"📁 Exported to: {list(results['output_files'].values())}")
    
    # Show sample results
    if results['results']:
        sample = results['results'][0]
        print(f"📧 Sample email: {sample.get('email', 'Unknown')}")
        print(f"🏢 Organization: {sample.get('organization', 'N/A')}")
        print(f"🌐 Domain: {sample.get('domain', 'N/A')}")
    
    return results

async def run_all_examples():
    """Run all example searches to demonstrate versatility"""
    print("🚀 Universal Multi-Purpose Scraper Demo")
    print("=" * 50)
    
    # Run all examples
    examples = [
        example_product_search,
        example_company_search, 
        example_person_search,
        example_social_media_search,
        example_email_search
    ]
    
    all_results = {}
    
    for example_func in examples:
        try:
            result = await example_func()
            all_results[example_func.__name__] = {
                "total_results": result.get('total_results', 0),
                "output_files": result.get('output_files', {}),
                "search_type": result.get('search_type', 'unknown')
            }
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {str(e)}")
            all_results[example_func.__name__] = {"error": str(e)}
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEMO SUMMARY")
    print("=" * 50)
    
    total_results = 0
    total_files = 0
    
    for example_name, result in all_results.items():
        if "error" in result:
            print(f"❌ {example_name}: {result['error']}")
        else:
            results_count = result.get('total_results', 0)
            files_count = len(result.get('output_files', {}))
            total_results += results_count
            total_files += files_count
            
            print(f"✅ {example_name}: {results_count} results, {files_count} files")
    
    print(f"\n📈 TOTAL: {total_results} results extracted, {total_files} output files created")
    print("🎉 Demo completed successfully!")
    
    # Save summary
    with open("demo_summary.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print("💾 Demo summary saved to demo_summary.json")

if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(run_all_examples())