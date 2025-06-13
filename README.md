# SAP MCP SSE Server

This is a Model Context Protocol (MCP) Server-Sent Events (SSE) server that provides access to SAP OData API endpoints for fetching due notifications and related data.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your SAP credentials:
```
SAP_USERNAME=your_username
SAP_PASSWORD=your_password
```

## Running the Server

Start the server with:
```bash
python sap_mcp_server.py
```

The server will start on `http://localhost:8000`.

## Available Tools

### 1. fetch_due_notifications
Fetches due notifications from the SAP OData API with specified filters and expansions.

Parameters:
- `filter_query` (optional): OData filter query string
- `expand` (optional): Comma-separated list of entities to expand
- `format` (optional): Response format (default: "json")
- `sap_language` (optional): SAP language code (default: "EN")

### 2. get_notification_details
Gets detailed information for a specific notification.

Parameters:
- `notification_id`: The ID of the notification to fetch

## Security Notes

1. The server currently disables SSL verification for development purposes. In production, you should properly handle SSL certificates.
2. Make sure to keep your `.env` file secure and never commit it to version control.
3. Consider implementing additional security measures like API key validation or IP whitelisting for production use.

## Error Handling

The server includes basic error handling for:
- Missing credentials
- API request failures
- Invalid responses

All errors are returned with appropriate error messages and status codes. 