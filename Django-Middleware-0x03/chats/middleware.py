import logging
import os
from datetime import datetime
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log each user's requests to a file with timestamp, user, and request path.
    """
    
    def __init__(self, get_response=None):
        """
        Initialize the middleware and set up the logger.
        """
        self.get_response = get_response
        
        # Set up logging configuration
        self.setup_logger()
        super().__init__(get_response)
    
    def setup_logger(self):
        """
        Set up the logger for request logging.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if the logger already exists
        if not self.logger.handlers:
            # Create file handler
            log_file_path = os.path.join(log_dir, 'requests.log')
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        """
        Process the request and log the information.
        """
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or f"User({request.user.user_id})"
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response
    
    def process_request(self, request):
        """
        Alternative method for Django's old-style middleware (optional).
        This method is called for compatibility with older Django versions.
        """
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or f"User({request.user.user_id})"
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        return None  # Continue processing the request


class DetailedRequestLoggingMiddleware(MiddlewareMixin):
    """
    Enhanced middleware with more detailed logging including HTTP method, IP, and response status.
    """
    
    def __init__(self, get_response=None):
        """
        Initialize the middleware and set up the logger.
        """
        self.get_response = get_response
        self.setup_logger()
        super().__init__(get_response)
    
    def setup_logger(self):
        """
        Set up the logger for detailed request logging.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        self.logger = logging.getLogger('detailed_request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if the logger already exists
        if not self.logger.handlers:
            # Create file handler
            log_file_path = os.path.join(log_dir, 'detailed_requests.log')
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        """
        Process the request and log detailed information.
        """
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or f"User({request.user.user_id})"
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = (
            f"{datetime.now()} - "
            f"User: {user} - "
            f"Method: {request.method} - "
            f"Path: {request.path} - "
            f"IP: {ip}"
        )
        
        # Process the request
        response = self.get_response(request)
        
        # Log with response status
        complete_log_message = f"{log_message} - Status: {response.status_code}"
        self.logger.info(complete_log_message)
        
        return response


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware specifically for logging API requests with additional context.
    """
    
    def __init__(self, get_response=None):
        """
        Initialize the middleware and set up the logger.
        """
        self.get_response = get_response
        self.setup_logger()
        super().__init__(get_response)
    
    def setup_logger(self):
        """
        Set up the logger for API request logging.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        self.logger = logging.getLogger('api_request_logger')
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if the logger already exists
        if not self.logger.handlers:
            # Create file handler
            log_file_path = os.path.join(log_dir, 'api_requests.log')
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
    
    def __call__(self, request):
        """
        Process the request and log API-specific information.
        """
        # Only log API requests
        if request.path.startswith('/api/'):
            # Get user information
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user.username or f"User({request.user.user_id})"
                user_id = getattr(request.user, 'user_id', 'N/A')
            else:
                user = "Anonymous"
                user_id = "N/A"
            
            # Get additional request info
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            content_type = request.META.get('CONTENT_TYPE', 'Unknown')
            
            # Log the request information
            log_message = (
                f"{datetime.now()} - "
                f"User: {user} (ID: {user_id}) - "
                f"Method: {request.method} - "
                f"Path: {request.path} - "
                f"Content-Type: {content_type} - "
                f"User-Agent: {user_agent[:50]}..."  # Truncate user agent
            )
            self.logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response