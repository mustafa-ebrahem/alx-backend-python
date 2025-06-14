import logging
import os
import time
from datetime import datetime
from collections import defaultdict
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.urls import resolve

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


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the messaging app during certain hours of the day.
    Only allows access between 9PM (21:00) and 6PM (18:00) the next day.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """
        Set up a logger for the access restriction middleware.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        logger = logging.getLogger('access_restriction_logger')
        logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if the logger already exists
        if not logger.handlers:
            # Create file handler
            log_file_path = os.path.join(log_dir, 'access_restrictions.log')
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
        
        return logger
    
    def __call__(self, request):
        """
        Process the request and check if access is allowed based on current time.
        
        Access is restricted outside the hours of 9PM (21:00) to 6PM (18:00).
        """
        # Get current hour in 24-hour format
        current_time = timezone.localtime(timezone.now())
        current_hour = current_time.hour
        
        # Define allowed hours (9PM to 6PM next day)
        # This means hours 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
        allowed_start = 21  # 9PM
        allowed_end = 18    # 6PM
        
        # Check if current hour is outside allowed range
        # If current hour is less than allowed_start (21) AND greater than allowed_end (18)
        if current_hour < allowed_start and current_hour > allowed_end:
            # User identification for logging
            user_info = "Anonymous"
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = request.user.username or f"User({request.user.id})"
            
            # Log the restricted access attempt
            self.logger.warning(
                f"Access attempt outside allowed hours by {user_info} from {request.META.get('REMOTE_ADDR')} - "
                f"Current time: {current_time.strftime('%H:%M:%S')}"
            )
            
            # Return 403 Forbidden response
            return HttpResponseForbidden("Access to the messaging app is restricted between 6PM and 9PM. Please try again during allowed hours.")
        
        # Process the request if within allowed hours
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware to limit the number of messages a user can send within a time window based on IP address.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with IP tracking and rate limiting.
        """
        self.get_response = get_response
        # Store message counts per IP: {ip: [(timestamp1, count1), (timestamp2, count2), ...]}
        self.ip_message_counts = defaultdict(list)
        # Configure rate limits
        self.time_window = 60  # Time window in seconds (1 minute)
        self.max_messages = 5  # Maximum messages per time window
        # Set up logging
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """
        Set up a logger for rate limiting events.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the logger
        logger = logging.getLogger('rate_limiting_logger')
        logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if the logger already exists
        if not logger.handlers:
            # Create file handler
            log_file_path = os.path.join(log_dir, 'rate_limiting.log')
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
        
        return logger
    
    def _clean_expired_entries(self, ip):
        """
        Remove message counts that are outside the current time window.
        """
        current_time = time.time()
        self.ip_message_counts[ip] = [
            (timestamp, count) for timestamp, count in self.ip_message_counts[ip]
            if current_time - timestamp < self.time_window
        ]
    
    def _is_rate_limited(self, ip):
        """
        Check if an IP address has exceeded the message rate limit.
        """
        # Clean up expired entries first
        self._clean_expired_entries(ip)
        
        # Count total messages within the window
        total_messages = sum(count for _, count in self.ip_message_counts[ip])
        
        return total_messages >= self.max_messages
    
    def _is_chat_post_request(self, request):
        """
        Determines if the request is a POST request to send a chat message.
        """
        # Check if this is a POST request to chat-related URLs
        # Adjust the URL patterns according to your application's URL structure
        is_post = request.method == 'POST'
        is_chat_url = any(path in request.path for path in [
            '/chats/', '/messages/', '/send_message/', '/api/messages/'
        ])
        
        return is_post and is_chat_url
    
    def __call__(self, request):
        """
        Process the request and check for rate limiting.
        """
        # Only apply rate limiting to chat message POST requests
        if self._is_chat_post_request(request):
            # Get the client's IP address
            ip = self._get_client_ip(request)
            
            # Check if this IP has reached the rate limit
            if self._is_rate_limited(ip):
                # Log the rate limit event
                user_info = "Anonymous"
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_info = request.user.username or f"User({request.user.id})"
                
                self.logger.warning(
                    f"Rate limit exceeded: {user_info} from IP {ip} - "
                    f"More than {self.max_messages} messages in {self.time_window} seconds."
                )
                
                # Return a 403 Forbidden response
                return HttpResponseForbidden(
                    f"You've sent too many messages. Please wait a moment before sending more."
                )
            
            # Update the message count for this IP
            current_time = time.time()
            self.ip_message_counts[ip].append((current_time, 1))
        
        # Process the request if not rate limited
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """
        Get the client's real IP address, accounting for proxy servers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP in the list (client's real IP)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware:
    """
    Middleware to check user's role before allowing access to specific admin actions.
    Only users with admin or moderator roles are allowed to access protected paths.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with role-based access control.
        """
        self.get_response = get_response
        
        # Define protected paths that require admin/moderator access
        self.protected_paths = [
            '/admin/',
            '/dashboard/',
            '/manage/',
            '/chats/delete/',
            '/chats/moderate/',
            '/users/manage/',
            '/api/admin/',
            '/reports/',
        ]
    
    def __call__(self, request):
        """
        Process the request and check for role-based permissions.
        """
        # Check if the path is protected
        if any(request.path.startswith(protected) for protected in self.protected_paths):
            # Check user's role
            user = request.user
            
            # Check if user is authenticated and has proper permissions
            if not self._has_admin_permissions(user):
                # Return 403 Forbidden response
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(
                    "Access denied: You must be an admin or moderator to access this resource."
                )
        
        # Process the request if authorized or not a protected path
        return self.get_response(request)
    
    def _has_admin_permissions(self, user):
        """
        Check if the user has admin or moderator permissions.
        """
        # Check if user is authenticated
        if not user.is_authenticated:
            return False
            
        # Check if user is superuser (admin)
        if user.is_superuser:
            return True
            
        # Check if user is staff
        if user.is_staff:
            return True
            
        # Check if user has specific groups
        if hasattr(user, 'groups'):
            user_groups = user.groups.values_list('name', flat=True)
            if 'moderator' in user_groups or 'admin' in user_groups:
                return True
        
        # Check for custom role field if it exists
        if hasattr(user, 'role'):
            return user.role in ['admin', 'moderator']
            
        return False