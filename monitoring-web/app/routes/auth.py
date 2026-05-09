"""Authentication routes - Login, Logout, Callback."""
import logging
import requests
from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify
from app.auth import entra_auth

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET"])
def login():
    """Initiate login with Entra ID (Proftask tenant)."""
    if not current_app.config.get("AUTH_ENABLED"):
        return redirect(url_for("main.index"))
    
    try:
        auth_url = entra_auth.get_authorization_url()
        logger.info(f"Redirecting to Entra ID login: {auth_url[:50]}...")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed", "details": str(e)}), 500


@auth_bp.route("/callback", methods=["GET"])
def callback():
    """Handle OAuth callback from Entra ID (Proftask)."""
    if not current_app.config.get("AUTH_ENABLED"):
        return redirect(url_for("main.index"))
    
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        logger.error(f"OAuth error: {error}")
        return jsonify({"error": f"Authentication error: {error}"}), 400
    
    if not code:
        logger.error("No authorization code received")
        return jsonify({"error": "No authorization code"}), 400
    
    try:
        # Exchange code for token
        token_response = entra_auth.get_token_by_code(
            code,
            current_app.config["REDIRECT_URI"]
        )
        
        if "error" in token_response:
            logger.error(f"Token error: {token_response}")
            return jsonify({"error": f"Token error: {token_response.get('error_description')}"}), 500
        
        # Get user info from Microsoft Graph
        access_token = token_response["access_token"]
        user_response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        
        if user_response.status_code != 200:
            logger.error(f"Failed to get user info: {user_response.status_code}")
            return jsonify({"error": "Failed to get user information"}), 500
        
        user_info = user_response.json()
        
        # Store user info in session
        session["user_id"] = user_info.get("id")
        session["user_name"] = user_info.get("displayName")
        session["user_email"] = user_info.get("mail")
        session["access_token"] = access_token
        session.permanent = True
        
        logger.info(f"User logged in: {session.get('user_email')} (ID: {session.get('user_id')})")
        return redirect(url_for("main.index"))
        
    except requests.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return jsonify({"error": "Failed to communicate with identity provider"}), 500
    except Exception as e:
        logger.error(f"Callback error: {e}")
        return jsonify({"error": "Authentication failed", "details": str(e)}), 500


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Logout user and clear session."""
    user_email = session.get("user_email")
    session.clear()
    logger.info(f"User logged out: {user_email}")
    return redirect(url_for("main.index"))


@auth_bp.route("/user", methods=["GET"])
def get_user():
    """Get current user info (JSON API)."""
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401
    
    return jsonify({
        "authenticated": True,
        "user_id": session.get("user_id"),
        "user_name": session.get("user_name"),
        "user_email": session.get("user_email")
    })
