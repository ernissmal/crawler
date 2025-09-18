#!/usr/bin/env python3
"""
Universal Scraper CLI Tool
Command line interface for the multi-purpose scraping tool
"""

import asyncio
import argparse
import json
import yaml
import os
from typing import List, Optional
from universal_scraper import UniversalSearchRequest, SearchType, ExtractionMode, universal_scraper

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Universal Multi-Purpose Scraper - Search for products, companies, people, social media, emails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for John Doe contacts (using template)
  python cli.py person "John Doe Lisburn" --template john_doe_contacts --max-results 10

  # Search for oak tables with dimensions (using template)
  python cli.py product "solid oak table" --template oak_table_dimensions --include "dimensions,cm"

  # Search for Vilnius IT companies (using template)  
  python cli.py company "IT Vilnius WordPress" --template vilnius_it_wordpress --cities "Vilnius"

  # Custom field extraction
  python cli.py company "restaurants Dublin" --fields "name,phone,address,rating" --field-mode custom

  # Hybrid approach
  python cli.py product "electronics" --template oak_table_dimensions --fields "warranty,brand" --field-mode hybrid

  # Legacy examples (without field selection)
  python cli.py product "oak furniture Kaunas" --include "table,chair" --max-results 20
  python cli.py company "IT companies Lisburn" --regions "Northern Ireland" --exclude "jobs,careers"
        """)
    
    parser.add_argument(
        "search_type",
        choices=["product", "company", "person", "social_media", "email", "custom"],
        help="Type of search to perform"
    )
    
    parser.add_argument(
        "query",
        help="Main search query"
    )
    
    parser.add_argument(
        "--secondary-queries", "-sq",
        help="Additional search queries (comma-separated)"
    )
    
    parser.add_argument(
        "--regions", "-r",
        help="Geographic regions to search (comma-separated)"
    )
    
    parser.add_argument(
        "--cities", "-c",
        help="Specific cities to search (comma-separated)"
    )
    
    parser.add_argument(
        "--countries",
        help="Country codes (comma-separated)"
    )
    
    parser.add_argument(
        "--include", "-i",
        help="Keywords that must be included (comma-separated)"
    )
    
    parser.add_argument(
        "--exclude", "-e", 
        help="Keywords to exclude (comma-separated)"
    )
    
    parser.add_argument(
        "--max-results", "-m",
        type=int,
        default=50,
        help="Maximum number of results (default: 50)"
    )
    
    parser.add_argument(
        "--extraction",
        choices=["basic", "detailed", "custom"],
        default="detailed",
        help="Data extraction mode (default: detailed)"
    )
    
    parser.add_argument(
        "--output-formats", "-o",
        default="json,csv",
        help="Output formats (comma-separated: json,csv,excel)"
    )
    
    parser.add_argument(
        "--output-filename", "-f",
        help="Custom output filename (without extension)"
    )
    
    parser.add_argument(
        "--config", "-cfg",
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--search-depth",
        choices=["shallow", "medium", "deep"],
        default="medium",
        help="Search depth (default: medium)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be searched without actually scraping"
    )
    
    # Field Selection Options
    parser.add_argument(
        "--template", "-t",
        choices=["john_doe_contacts", "oak_table_dimensions", "vilnius_it_wordpress"],
        help="Use pre-built extraction template"
    )
    
    parser.add_argument(
        "--fields",
        help="Custom fields to extract (comma-separated: phone,email,price,dimensions,address)"
    )
    
    parser.add_argument(
        "--field-mode",
        choices=["template", "custom", "hybrid"],
        default="template",
        help="Field selection mode (default: template)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser

def parse_comma_separated(value: str) -> List[str]:
    """Parse comma-separated string into list"""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def create_search_request(args) -> UniversalSearchRequest:
    """Create search request from command line arguments"""
    
    # Parse search type
    search_type = SearchType(args.search_type)
    
    # Parse extraction mode
    extraction_mode = ExtractionMode(args.extraction)
    
    # Parse lists
    secondary_queries = parse_comma_separated(args.secondary_queries)
    regions = parse_comma_separated(args.regions)
    cities = parse_comma_separated(args.cities)
    countries = parse_comma_separated(args.countries)
    include_keywords = parse_comma_separated(args.include)
    exclude_keywords = parse_comma_separated(args.exclude)
    output_formats = parse_comma_separated(args.output_formats)
    custom_fields = parse_comma_separated(args.fields)
    
    # Create request
    request = UniversalSearchRequest(
        search_type=search_type,
        config_file=args.config,
        extraction_template=args.template,
        custom_fields=custom_fields,
        field_selection_mode=args.field_mode,
        primary_query=args.query,
        secondary_queries=secondary_queries,
        regions=regions,
        cities=cities,
        countries=countries,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords,
        max_results=args.max_results,
        search_depth=args.search_depth,
        extraction_mode=extraction_mode,
        output_formats=output_formats,
        output_filename=args.output_filename
    )
    
    return request

def print_search_preview(request: UniversalSearchRequest):
    """Print what will be searched (dry run)"""
    print("🔍 SEARCH PREVIEW")
    print("=" * 40)
    print(f"Search Type: {request.search_type.value}")
    print(f"Primary Query: {request.primary_query}")
    
    # Field selection info
    if request.extraction_template:
        print(f"🎯 Template: {request.extraction_template}")
    if request.custom_fields:
        print(f"🔧 Custom Fields: {', '.join(request.custom_fields)}")
    if request.field_selection_mode != "template":
        print(f"⚙️ Field Mode: {request.field_selection_mode}")
    
    if request.secondary_queries:
        print(f"Secondary Queries: {', '.join(request.secondary_queries)}")
    
    if request.regions:
        print(f"Regions: {', '.join(request.regions)}")
    
    if request.cities:
        print(f"Cities: {', '.join(request.cities)}")
    
    if request.include_keywords:
        print(f"Include Keywords: {', '.join(request.include_keywords)}")
    
    if request.exclude_keywords:
        print(f"Exclude Keywords: {', '.join(request.exclude_keywords)}")
    
    print(f"Max Results: {request.max_results}")
    print(f"Extraction Mode: {request.extraction_mode.value}")
    print(f"Output Formats: {', '.join(request.output_formats)}")
    
    if request.config_file:
        print(f"Config File: {request.config_file}")
    
    print("=" * 40)

async def main():
    """Main CLI function"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Create search request
    try:
        request = create_search_request(args)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    # Dry run mode
    if args.dry_run:
        print_search_preview(request)
        print("\n✅ Dry run completed. Use without --dry-run to execute the search.")
        return
    
    # Print search info
    if args.verbose:
        print_search_preview(request)
        print()
    
    # Execute search
    print(f"🚀 Starting {request.search_type.value} search...")
    print(f"🔍 Query: {request.primary_query}")
    
    if request.extraction_template:
        print(f"🎯 Using template: {request.extraction_template}")
    elif request.custom_fields:
        print(f"🔧 Custom fields: {', '.join(request.custom_fields)}")
    
    try:
        results = await universal_scraper.search_and_scrape(request)
        
        # Print results summary
        print("\n" + "=" * 50)
        print("📊 SEARCH RESULTS SUMMARY")
        print("=" * 50)
        print(f"✅ Search Type: {results['search_type']}")
        print(f"🎯 Template Used: {results.get('extraction_template', 'N/A')}")
        print(f"🔗 URLs Found: {results['total_urls_found']}")
        print(f"📦 Results Extracted: {results['total_results']}")
        
        if results['output_files']:
            print(f"📁 Output Files:")
            for format_type, filename in results['output_files'].items():
                print(f"   - {format_type.upper()}: {filename}")
        
        # Print session summary if verbose
        if args.verbose and 'session_summary' in results:
            summary = results['session_summary']
            print(f"\n📈 Session Summary:")
            print(f"   - Operations: {summary.get('total_operations', 0)}")
            print(f"   - Errors: {summary.get('total_errors', 0)}")
            print(f"   - Success Rate: {summary.get('success_rate', 0):.1%}")
        
        # Show sample results with template-aware display
        if results['results'] and args.verbose:
            print(f"\n📝 Sample Results (first 3):")
            for i, result in enumerate(results['results'][:3], 1):
                print(f"\n{i}. {result.get('url', 'No URL')}")
                
                # Show template-specific fields if available
                if request.extraction_template == "john_doe_contacts":
                    print(f"   Phone: {result.get('phone_number', 'N/A')}")
                    print(f"   Email: {result.get('email_address', 'N/A')}")
                    print(f"   Name: {result.get('name', 'N/A')}")
                    print(f"   Location: {result.get('location', 'N/A')}")
                
                elif request.extraction_template == "oak_table_dimensions":
                    print(f"   Company: {result.get('company_name', 'N/A')}")
                    print(f"   Price: {result.get('price', 'N/A')}")
                    print(f"   Dimensions: {result.get('dimensions', 'N/A')}")
                    print(f"   Material: {result.get('material', 'N/A')}")
                
                elif request.extraction_template == "vilnius_it_wordpress":
                    print(f"   Company: {result.get('company_name', 'N/A')}")
                    print(f"   Address: {result.get('address', 'N/A')}")
                    print(f"   Phone: {result.get('phone_number', 'N/A')}")
                    print(f"   Website: {result.get('website', 'N/A')}")
                    print(f"   Price Range: {result.get('price_range', 'N/A')}")
                
                elif request.custom_fields:
                    # Show custom fields
                    for field in request.custom_fields:
                        print(f"   {field.title()}: {result.get(field, 'N/A')}")
                
                else:
                    # Show standard fields based on search type
                    if request.search_type == SearchType.PRODUCT:
                        print(f"   Name: {result.get('name', 'N/A')}")
                        if 'price_amount' in result:
                            print(f"   Price: {result.get('price_currency', '')} {result.get('price_amount', 'N/A')}")
                    
                    elif request.search_type == SearchType.COMPANY:
                        print(f"   Company: {result.get('name', 'N/A')}")
                        print(f"   Industry: {result.get('industry', 'N/A')}")
                        print(f"   Location: {result.get('location', 'N/A')}")
                    
                    elif request.search_type == SearchType.PERSON:
                        print(f"   Name: {result.get('name', 'N/A')}")
                        print(f"   Profession: {result.get('profession', 'N/A')}")
                        print(f"   Company: {result.get('company', 'N/A')}")
        
        print(f"\n🎉 Search completed successfully!")
        
        # Return success
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def cli():
    """CLI entry point"""
    try:
        exit_code = asyncio.run(main())
        exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n⏹️  Search interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    cli()