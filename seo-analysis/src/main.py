import pandas as pd
import numpy as np
from ecommercetools import seo
import datetime
import os
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def in_title(row: pd.Series) -> int:
    """Check if query appears in title"""
    if pd.isna(row.get('title')) or pd.isna(row.get('query')):
        return 0
    return 1 if str(row['query']).lower() in str(row['title']).lower() else 0

def in_subheading(row: pd.Series, subheading: str) -> int:
    """Check if query appears in specified subheading"""
    subheading_name = f"{subheading}s"
    
    if pd.isna(row.get(subheading_name)) or pd.isna(row.get('query')):
        return 0
    return 1 if str(row['query']).lower() in str(row[subheading_name]).lower() else 0

def in_h1s(row: pd.Series) -> int:
    return in_subheading(row, "h1")

def in_h2s(row: pd.Series) -> int:
    return in_subheading(row, "h2")

def in_h3s(row: pd.Series) -> int:
    return in_subheading(row, "h3")

def in_h4s(row: pd.Series) -> int:
    return in_subheading(row, "h4")

def in_h5s(row: pd.Series) -> int:
    return in_subheading(row, "h5")

def in_h6s(row: pd.Series) -> int:
    return in_subheading(row, "h6")

def in_description(row: pd.Series) -> int:
    """Check if query appears in description"""
    if pd.isna(row.get('description')) or pd.isna(row.get('query')):
        return 0
    return 1 if str(row['query']).lower() in str(row['description']).lower() else 0

def scrape_website(sitemap_url: str, dry_run: str) -> bool:
    """Scrape website data from sitemap"""
    try:
        if dry_run.lower() == 'true':
            logger.info("In dry run mode, not scraping!")
            return False
        
        logger.info(f"Scraping sitemap: {sitemap_url}")
        df_sitemap = seo.get_sitemap(sitemap_url)
        
        if df_sitemap.empty:
            logger.warning("Sitemap is empty")
            return False
        
        logger.info(f"Found {len(df_sitemap)} URLs in sitemap")
        df_pages = seo.scrape_site(df_sitemap, 'loc', verbose=False)
        
        if df_pages.empty:
            logger.warning("No pages scraped")
            return False
        
        df_pages.to_csv("scraped_data.csv", index=False)
        logger.info(f"Scraped {len(df_pages)} pages successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return False

def validate_search_console_data(sc_df: pd.DataFrame) -> bool:
    """Validate Google Search Console data"""
    required_columns = ['page', 'query', 'impressions', 'clicks', 'ctr', 'position']
    
    if sc_df.empty:
        logger.warning("Google Search Console data is empty")
        return False
    
    missing_columns = [col for col in required_columns if col not in sc_df.columns]
    if missing_columns:
        logger.error(f"Missing required columns in Search Console data: {missing_columns}")
        return False
    
    logger.info(f"Search Console data validated: {len(sc_df)} rows")
    return True

def create_empty_optimization_files():
    """Create empty CSV files when no data is available"""
    logger.info("Creating empty optimization files due to no data")
    
    # Create empty traffic file
    empty_traffic_df = pd.DataFrame(columns=[
        "url", "query", "clicks", "impressions", "ctr", "position", 
        "in_title", "in_description", "in_h1s", "in_h2s", "in_h3s", 
        "in_h4s", "in_h5s", "in_h6s", "in_both", "hreflang", 
        "generator", "title", "description", "h1s", "h2s", "h3s", 
        "h4s", "h5s", "h6s", "absolute_links", "canonical", "robots"
    ])
    empty_traffic_df.to_csv('traffic.csv', index=False)
    
    # Create empty no traffic file
    empty_no_traffic_df = pd.DataFrame(columns=["url", "title", "description"])
    empty_no_traffic_df.to_csv('no_traffic.csv', index=False)
    
    # Create empty optimization priority file
    empty_traffic_df.to_csv("to_optimize_priority.csv", index=False)

def generate_optimizations(sitemap_url: str, service_account_json_file_path: str, 
                         site_url: str, start_date: str, end_date: str) -> bool:
    """Generate SEO optimizations based on scraped data and Google Search Console data"""
    
    logger.info(f"Generating SEO optimizations for {sitemap_url}")
    logger.info(f"Using service account: {service_account_json_file_path}")
    logger.info(f"Site URL: {site_url}")
    logger.info(f"Date range: {start_date} to {end_date}")
    
    try:
        # Check if scraped data exists
        if not os.path.exists("scraped_data.csv"):
            logger.error("Scraped data file not found. Run scraping first.")
            create_empty_optimization_files()
            return False
        
        # Load the scraped data
        df_pages = pd.read_csv("scraped_data.csv")
        logger.info(f"Loaded {len(df_pages)} scraped pages")
        
        if df_pages.empty:
            logger.warning("No scraped data available")
            create_empty_optimization_files()
            return False

        # Prepare Google Search Console query
        payload = {
            'startDate': start_date, 
            'endDate': end_date,
            'dimensions': ['page', 'query'],  
            'rowLimit': 10000,
            'startRow': 0
        }

        logger.info("Querying Google Search Console...")
        try:
            sc_df = seo.query_google_search_console(service_account_json_file_path, site_url, payload)
        except Exception as e:
            logger.error(f"Error querying Google Search Console: {str(e)}")
            create_empty_optimization_files()
            return False

        logger.info(f"Google Search Console returned {len(sc_df)} rows")
        
        # Validate Search Console data
        if not validate_search_console_data(sc_df):
            create_empty_optimization_files()
            return False

        # Process the data only if we have valid Search Console data
        df = sc_df.sort_values(by=['page', 'impressions'], ascending=False)
        df = df.drop_duplicates(subset='page', keep='first')
        
        logger.info("Merging scraped data with Google Search Console data")
        df_all = df_pages.merge(df, how='left', left_on='url', right_on='page')

        # Generate no traffic data
        logger.info("Generating no traffic data")
        df_no_traffic = df_all[df_all['query'].isnull()].fillna(0)
        df_no_traffic.to_csv('no_traffic.csv', index=False)
        logger.info(f"Found {len(df_no_traffic)} pages with no traffic")

        # Generate traffic data
        logger.info("Generating traffic data")
        df_traffic = df_all[df_all['query'].notnull()].copy()
        
        if df_traffic.empty:
            logger.warning("No traffic data available")
            create_empty_optimization_files()
            return True
        
        # Remove duplicate 'page' column if it exists
        if 'page' in df_traffic.columns:
            df_traffic = df_traffic.drop('page', axis=1)
        
        df_traffic = df_traffic.sort_values(by='impressions', ascending=False)
        logger.info(f"Found {len(df_traffic)} pages with traffic")

        # Apply analysis functions safely
        logger.info("Analyzing keyword placement...")
        
        analysis_functions = {
            'in_title': in_title,
            'in_description': in_description,
            'in_h1s': in_h1s,
            'in_h2s': in_h2s,
            'in_h3s': in_h3s,
            'in_h4s': in_h4s,
            'in_h5s': in_h5s,
            'in_h6s': in_h6s
        }
        
        for col_name, func in analysis_functions.items():
            try:
                df_traffic[col_name] = df_traffic.apply(func, axis=1)
                logger.info(f"Applied {col_name} analysis")
            except Exception as e:
                logger.warning(f"Error applying {col_name} analysis: {str(e)}")
                df_traffic[col_name] = 0

        # Calculate combined metric
        df_traffic['in_both'] = np.where(
            df_traffic['in_title'] + df_traffic['in_description'] == 2, 1, 0
        )

        # Save traffic data
        df_traffic.to_csv('traffic.csv', index=False)
        logger.info("Saved traffic analysis")

        # Generate optimization priorities
        logger.info("Generating optimization priorities")
        df_optimize_priority = df_traffic.sort_values(by='in_both', ascending=True).head(50).copy()
        
        # Remove paragraphs column if it exists (it can be very large)
        if 'paragraphs' in df_optimize_priority.columns:
            df_optimize_priority = df_optimize_priority.drop('paragraphs', axis=1)

        # Reorganize columns (only include existing columns)
        desired_columns = [
            "url", "query", "clicks", "impressions", "ctr", "position", 
            "in_title", "in_description", "in_h1s", "in_h2s", "in_h3s", 
            "in_h4s", "in_h5s", "in_h6s", "in_both", "hreflang", 
            "generator", "title", "description", "h1s", "h2s", "h3s", 
            "h4s", "h5s", "h6s", "absolute_links", "canonical", "robots"
        ]
        
        # Only include columns that actually exist in the dataframe
        available_columns = [col for col in desired_columns if col in df_optimize_priority.columns]
        df_optimize_priority = df_optimize_priority[available_columns]
        
        df_optimize_priority.to_csv("to_optimize_priority.csv", index=False)
        logger.info(f"Generated optimization priorities for {len(df_optimize_priority)} pages")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in generate_optimizations: {str(e)}")
        create_empty_optimization_files()
        return False

def main():
    """Main function with proper error handling"""
    try:
        # Get environment variables with defaults
        sitemap_url = os.getenv("INPUT_SITEMAP_URL")
        service_account_json_file_path = os.getenv("INPUT_SERVICE_ACCOUNT_JSON_FILE_PATH")
        dry_run = os.getenv("INPUT_DRY_RUN", 'true')
        date_offset = int(os.getenv("INPUT_DATE_OFFSET", "-1"))
        date_duration = int(os.getenv("INPUT_DATE_DURATION", "-90"))
        site_url = os.getenv("INPUT_SITE_URL")

        # Validate required inputs
        if not sitemap_url:
            logger.error("INPUT_SITEMAP_URL is required")
            return False
            
        if not site_url:
            logger.error("INPUT_SITE_URL is required")
            return False
            
        if dry_run.lower() != 'true' and not service_account_json_file_path:
            logger.error("INPUT_SERVICE_ACCOUNT_JSON_FILE_PATH is required when not in dry run mode")
            return False

        # Calculate dates
        end_date = datetime.date.today() + datetime.timedelta(days=date_offset)
        start_date = datetime.date.today() + datetime.timedelta(days=(date_offset + date_duration))
        
        logger.info(f"Date range: {start_date} to {end_date}")

        # Scrape website
        scrape_success = scrape_website(sitemap_url, dry_run)
        
        if dry_run.lower() == 'true':
            logger.info("Dry run completed successfully")
            return True
            
        if not scrape_success:
            logger.error("Website scraping failed")
            create_empty_optimization_files()
            return False

        # Generate optimizations
        optimization_success = generate_optimizations(
            sitemap_url, 
            service_account_json_file_path, 
            site_url, 
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        if optimization_success:
            logger.info("SEO analysis completed successfully")
        else:
            logger.warning("SEO analysis completed with issues")
            
        return optimization_success
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        create_empty_optimization_files()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)