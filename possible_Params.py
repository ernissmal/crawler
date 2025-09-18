from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ProductSearchParams:
    # Basic product details
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = None

    # Pricing and availability
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: Optional[str] = None
    availability: Optional[str] = None  # e.g., "in_stock", "out_of_stock"
    discount_available: Optional[bool] = None

    # User feedback and ratings
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    reviews_min: Optional[int] = None
    reviews_max: Optional[int] = None

    # Advanced filtering and features
    features: Optional[Dict[str, Any]] = field(default_factory=dict)  # e.g., {"color": "red", "size": "M"}
    keywords: Optional[List[str]] = field(default_factory=list)
    advanced_filters: Optional[Dict[str, Any]] = field(default_factory=dict)

    # Search configuration parameters for Google advanced queries
    search_query: Optional[str] = None  # full query term if different from product name
    google_search_type: Optional[str] = None  # e.g., "images", "news", "shopping"
    results_per_page: Optional[int] = 10
    page: Optional[int] = 1
    date_range: Optional[str] = None  # e.g., "past_year", "past_month", "custom"

    # Locale and region parameters
    search_regions: Optional[List[str]] = field(default_factory=list)  # e.g., ["US", "UK"]
    languages: Optional[List[str]] = field(default_factory=list)  # e.g., ["en", "es"]

    # Sorting and ordering
    sort_by: Optional[str] = None  # e.g., "price", "rating", "relevance"
    order: Optional[str] = None  # e.g., "asc", "desc"

    # Miscellaneous Google parameters
    as_sitesearch: Optional[str] = None  # restrict search to a particular website
    hl: Optional[str] = None  # interface language
    cr: Optional[str] = None  # country code restriction
    lr: Optional[str] = None  # language restriction

# Example instantiation:
if __name__ == "__main__":
    params = ProductSearchParams(
        product_name="UltraWidget Pro",
        brand="WidgetCorp",
        category="Gadgets",
        model="Pro2023",
        price_min=100.0,
        price_max=500.0,
        currency="USD",
        availability="in_stock",
        discount_available=True,
        rating_min=4.0,
        reviews_min=50,
        features={"color": "black", "connectivity": "Bluetooth"},
        keywords=["ultra", "widget", "pro"],
        advanced_filters={"energy_efficiency": "A++"},
        search_query="buy UltraWidget Pro online",
        google_search_type="shopping",
        results_per_page=20,
        page=1,
        date_range="past_year",
        search_regions=["US", "CA"],
        languages=["en"],
        sort_by="price",
        order="asc",
        as_sitesearch="example.com",
        hl="en",
        cr="US",
        lr="lang_en"
    )
    print(params)

    @dataclass
    class CompanyResearchParams:
        # Basic company details
        company_name: str
        industry: Optional[str] = None
        sector: Optional[str] = None
        sub_industry: Optional[str] = None
        founded_year: Optional[int] = None
        headquarters: Optional[str] = None
        country: Optional[str] = None
        state: Optional[str] = None
        city: Optional[str] = None
        website: Optional[str] = None

        # Financial and performance metrics
        num_employees_min: Optional[int] = None
        num_employees_max: Optional[int] = None
        annual_revenue_min: Optional[float] = None
        annual_revenue_max: Optional[float] = None
        market_cap_min: Optional[float] = None
        market_cap_max: Optional[float] = None
        financials: Optional[Dict[str, Any]] = field(default_factory=dict)  # e.g., {"EBITDA": 5000000}

        # Leadership and key personnel
        ceo: Optional[str] = None
        board_members: Optional[List[str]] = field(default_factory=list)
        key_executives: Optional[Dict[str, str]] = field(default_factory=dict)  # e.g., {"CFO": "Jane Doe"}

        # Competitive landscape and industry positioning
        competitors: Optional[List[str]] = field(default_factory=list)
        partnerships: Optional[List[str]] = field(default_factory=list)
        affiliations: Optional[List[str]] = field(default_factory=list)

        # Public perception and reviews
        rating_min: Optional[float] = None
        rating_max: Optional[float] = None
        reviews_min: Optional[int] = None
        reviews_max: Optional[int] = None

        # Social media and online presence
        social_media: Optional[Dict[str, str]] = field(default_factory=dict)  # e.g., {"twitter": "@company"}
        news_keywords: Optional[List[str]] = field(default_factory=list)
        search_query: Optional[str] = None

        # Temporal filters for research (e.g., news or financial reports)
        date_range: Optional[str] = None  # e.g., "past_year", "quarter", "custom"

        # Additional filters and miscellaneous parameters
        extra_filters: Optional[Dict[str, Any]] = field(default_factory=dict)

        @dataclass
        class PersonSearchParams:
            # Basic personal details
            first_name: str
            last_name: str
            full_name: Optional[str] = None
            nickname: Optional[str] = None
            gender: Optional[str] = None
            age: Optional[int] = None
            date_of_birth: Optional[str] = None  # ISO format, e.g., "YYYY-MM-DD"
            ethnicity: Optional[str] = None

            # Contact and location details
            email: Optional[str] = None
            phone: Optional[str] = None
            address: Optional[str] = None
            city: Optional[str] = None
            state: Optional[str] = None
            country: Optional[str] = None
            postal_code: Optional[str] = None

            # Education and career
            education_level: Optional[str] = None  # e.g., "Bachelor's", "Master's", "PhD"
            institution: Optional[str] = None
            graduation_year: Optional[int] = None
            occupation: Optional[str] = None
            company: Optional[str] = None
            industry: Optional[str] = None
            years_experience: Optional[int] = None

            # Social media and online presence
            social_media_handles: Optional[Dict[str, str]] = field(default_factory=dict)  # e.g., {"twitter": "@username"}
            linkedin_profile: Optional[str] = None
            facebook_profile: Optional[str] = None
            twitter_profile: Optional[str] = None
            instagram_profile: Optional[str] = None
            personal_website: Optional[str] = None
            blog: Optional[str] = None

            # Professional skills and interests
            skills: Optional[List[str]] = field(default_factory=list)
            interests: Optional[List[str]] = field(default_factory=list)
            certifications: Optional[List[str]] = field(default_factory=list)

            # Online behavior and search queries
            keywords: Optional[List[str]] = field(default_factory=list)
            search_query: Optional[str] = None

            # Temporal and other filters
            date_range: Optional[str] = None  # e.g., "past_year", "custom"
            recent_activity: Optional[bool] = None  # indicates if the person is recently active online
            language: Optional[str] = None  # primary language

            # Miscellaneous parameters
            extra_filters: Optional[Dict[str, Any]] = field(default_factory=dict)