import os
from supabase import create_client, Client
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✓ Environment variables loaded successfully")
except ImportError:
    logger.warning("⚠ python-dotenv not installed, using system environment variables")

class SupabaseConfig:
    def __init__(self):
        logger.info("🔧 Initializing Supabase configuration...")
        
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        
        logger.info(f"SUPABASE_URL: {'✓ Set' if self.url else '✗ Missing'}")
        logger.info(f"SUPABASE_ANON_KEY: {'✓ Set' if self.key else '✗ Missing'}")
        logger.info(f"SUPABASE_SERVICE_ROLE_KEY: {'✓ Set' if self.service_role_key else '✗ Missing'}")
        
        if not self.url or not self.key:
            error_msg = "SUPABASE_URL and SUPABASE_ANON_KEY must be set"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info("✓ Supabase client created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create Supabase client: {e}")
            raise
        
        # Service role client for admin operations
        self.admin_client: Optional[Client] = None
        if self.service_role_key:
            self.admin_client = create_client(self.url, self.service_role_key)
    
    def get_client(self) -> Client:
        """Get the standard Supabase client"""
        return self.client
    
    def get_admin_client(self) -> Client:
        """Get the admin client with service role key"""
        if not self.admin_client:
            raise ValueError("Service role key not configured")
        return self.admin_client

# Global instance
supabase_config = SupabaseConfig()

# Export client for easy import
supabase_client = supabase_config.get_client()

# Export function for compatibility
def get_supabase_client() -> Client:
    """Get the Supabase client instance"""
    return supabase_config.get_client()