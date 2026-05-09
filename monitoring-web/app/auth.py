"""Authentication module for Entra ID integration via Proftask tenant."""
import logging
import msal
from flask import Flask, request, session, redirect, url_for, current_app
from functools import wraps

logger = logging.getLogger(__name__)


class EntraIDAuth:
    """Handle Entra ID OAuth2 authentication with Proftask tenant."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize authentication with Flask app."""
        self.app = app
    
    def get_auth_app(self):
        """Get MSAL confidential client application."""
        return msal.ConfidentialClientApplication(
            client_id=self.app.config["ENTRA_ID_CLIENT_ID"],
            client_credential=self.app.config["ENTRA_ID_CLIENT_SECRET"],
            authority=f"https://login.microsoftonline.com/{self.app.config['ENTRA_ID_TENANT_ID']}",
        )
    
    def login_required(self, f):
        """Decorator to protect routes with authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get("AUTH_ENABLED"):
                return f(*args, **kwargs)
            
            if "user_id" not in session:
                return redirect(url_for("auth.login", _external=True))
            
            return f(*args, **kwargs)
        return decorated_function
    
    def get_authorization_url(self):
        """Generate authorization URL for login."""
        auth_app = self.get_auth_app()
        auth_url = auth_app.get_authorization_request_url(
            scopes=["https://graph.microsoft.com/user.read"],
            redirect_uri=self.app.config.get("REDIRECT_URI")
        )
        return auth_url
    
    def get_token_by_code(self, code: str, redirect_uri: str):
        """Exchange authorization code for access token."""
        auth_app = self.get_auth_app()
        token_response = auth_app.acquire_token_by_authorization_code(
            code=code,
            scopes=["https://graph.microsoft.com/user.read"],
            redirect_uri=redirect_uri
        )
        return token_response


# Initialize (will be used in app factory)
entra_auth = EntraIDAuth()
