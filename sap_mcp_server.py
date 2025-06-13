import os
from typing import Dict, Any, List
from fastmcp import FastMCP
from dotenv import load_dotenv
import aiohttp
import json
import asyncio

# Load environment variables
load_dotenv()

# Initialize FastMCP
app = FastMCP(name="SAP MCP Server", port=3001)

# SAP OData API configuration
SAP_BASE_URL = "https://ed9.enstrapp.com:8200/sap/opu/odata/sap/ZEMT_PMAPP_SRV"
ENDPOINT = "/DueNotificationSet"

@app.tool("fetch_due_notifications")
async def fetch_due_notifications(
    filter_query: str = "",
    expand: str = "EvMessage,EtNotifHeader,EtNotifHeader/EtNotifHeaderFields,EtNotifHeader/EtNotifHeaderEquipHistory,EtNotifItems,EtNotifItems/EtNotifItemsFields,EtNotifTasks,EtNotifTasks/EtNotifTasksFields,EtNotifActvs,EtNotifActvs/EtNotifActvsFields,EtNotifLongtext,EtNotifStatus,EtImrg,EtDocs",
    format: str = "json",
    sap_language: str = "EN"
) -> Dict[str, Any]:
    """
    Fetch due notifications from SAP OData API with specified filters and expansions.
    
    Args:
        filter_query: OData filter query string
        expand: Comma-separated list of entities to expand
        format: Response format (json)
        sap_language: SAP language code
    
    Returns:
        Dictionary containing the API response
    """
    # Construct the full URL
    url = f"{SAP_BASE_URL}{ENDPOINT}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "IvUser": "ENST1",
        "IvTransmitType": "LOAD",
        "Muser": "ENST1",
        "Deviceid": "546546",
        "Udid": "6564",
        "Operation": "DUNOT"
    }
    
    # Prepare query parameters
    params = {
        "$filter": filter_query,
        "$expand": expand,
        "$format": format,
        "sap-language": sap_language,
        "sap-client": "800"
    }
    
    # Get credentials from environment variables
    username = os.getenv("SAP_USERNAME")
    password = os.getenv("SAP_PASSWORD")
    
    if not username or not password:
        raise ValueError("SAP credentials not found in environment variables")
    
    timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(
                url,
                params=params,
                auth=aiohttp.BasicAuth(username, password),
                headers=headers,
                ssl=False  # Note: In production, you should properly handle SSL
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"SAP API request failed with status {response.status}: {error_text}")
                
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception("Request timed out after 60 seconds")
        except Exception as e:
            raise Exception(f"Error making request to SAP API: {str(e)}")

@app.tool("create_notification")
async def create_notification(
    notification_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new notification in SAP.
    
    Args:
        notification_data: Dictionary containing notification details including:
            - IvUser: User ID
            - Muser: User ID
            - Deviceid: Device ID
            - Udid: Unique device ID
            - ItNotifHeader: List of notification headers
            - ItNotifItems: List of notification items
            - ItNotifActvs: List of notification activities
            - ItNotifTasks: List of notification tasks
    
    Returns:
        Dictionary containing the API response
    """
    # Construct the full URL
    url = f"{SAP_BASE_URL}{ENDPOINT}"
    
    # Get CSRF token and cookies first
    csrf_token, cookies = await get_csrf_token()
    if not csrf_token:
        raise Exception("Failed to get CSRF token")
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-csrf-token": csrf_token,  # Note: Using lowercase as per SAP's requirements
        "IvUser": notification_data.get("IvUser", "ENST1"),
        "Muser": notification_data.get("Muser", "ENST1"),
        "Deviceid": notification_data.get("Deviceid", "546546"),
        "Udid": notification_data.get("Udid", "6564"),
        "Operation": "CRNOT",
        "sap-client": "800"
    }
    
    # Get credentials from environment variables
    username = os.getenv("SAP_USERNAME")
    password = os.getenv("SAP_PASSWORD")
    
    if not username or not password:
        raise ValueError("SAP credentials not found in environment variables")
    
    # Prepare query parameters
    params = {
        "sap-language": "EN",
        "sap-client": "800"
    }
    
    timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
    async with aiohttp.ClientSession(timeout=timeout, cookies=cookies) as session:
        try:
            async with session.post(
                url,
                params=params,
                json=notification_data,
                auth=aiohttp.BasicAuth(username, password),
                headers=headers,
                ssl=False  # Note: In production, you should properly handle SSL
            ) as response:
                if response.status != 201:  # 201 Created
                    error_text = await response.text()
                    raise Exception(f"SAP API request failed with status {response.status}: {error_text}")
                
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception("Request timed out after 60 seconds")
        except Exception as e:
            raise Exception(f"Error making request to SAP API: {str(e)}")

async def get_csrf_token() -> str:
    """Get CSRF token from SAP system."""
    url = f"{SAP_BASE_URL}/"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-csrf-token": "fetch",
        "sap-client": "800"
    }
    
    # Get credentials from environment variables
    username = os.getenv("SAP_USERNAME")
    password = os.getenv("SAP_PASSWORD")
    
    if not username or not password:
        raise ValueError("SAP credentials not found in environment variables")
    
    timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(
                url,
                auth=aiohttp.BasicAuth(username, password),
                headers=headers,
                ssl=False  # Note: In production, you should properly handle SSL
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get CSRF token: {error_text}")
                
                # Get the token from response headers
                token = response.headers.get("x-csrf-token")
                if not token:
                    raise Exception("CSRF token not found in response headers")
                
                # Get cookies for session
                cookies = response.cookies
                
                return token, cookies
        except asyncio.TimeoutError:
            raise Exception("Request for CSRF token timed out after 30 seconds")
        except Exception as e:
            raise Exception(f"Error getting CSRF token: {str(e)}")

@app.tool("get_notification_details")
async def get_notification_details(notification_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific notification.
    
    Args:
        notification_id: The ID of the notification to fetch
    
    Returns:
        Dictionary containing the notification details
    """
    url = f"{SAP_BASE_URL}{ENDPOINT}('{notification_id}')"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "IvUser": "ENST1",
        "IvTransmitType": "LOAD",
        "Muser": "ENST1",
        "Deviceid": "546546",
        "Udid": "6564",
        "Operation": "DUNOT"
    }
    
    # Get credentials from environment variables
    username = os.getenv("SAP_USERNAME")
    password = os.getenv("SAP_PASSWORD")
    
    if not username or not password:
        raise ValueError("SAP credentials not found in environment variables")
    
    timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(
                url,
                auth=aiohttp.BasicAuth(username, password),
                headers=headers,
                ssl=False  # Note: In production, you should properly handle SSL
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"SAP API request failed with status {response.status}: {error_text}")
                
                return await response.json()
        except asyncio.TimeoutError:
            raise Exception("Request timed out after 60 seconds")
        except Exception as e:
            raise Exception(f"Error making request to SAP API: {str(e)}")

if __name__ == "__main__":
    # Run the server
    app.run(transport="sse") 