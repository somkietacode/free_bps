# Backend Protection System (BPS)
![URL based backend protection system](https://github.com/user-attachments/assets/21c45067-d764-4652-9e8f-ad7881c076ee)

The **Backend Protection System (BPS)** acts as a reverse proxy, forwarding client requests to your backend while ensuring the security and integrity of your API. It validates API keys, handles authentication via backend response, and protects against brute-force attacks.

## Features

1. **Authentication Handling**:  
   Forwards the `/auth` request to the backend. If the backend responds with `{"success": "Any_text_you"}`, an API key is generated and returned.

2. **API Key Validation**:  
   Validates the API key (`KEY` parameter in the query string) for every non-auth request and forwards it to the backend without the `KEY` parameter.

3. **Brute Force Protection**:  
   Tracks invalid requests and blocks IPs that make more than 5 failed attempts in 5 seconds.

4. **Configuration**:  
   The backend URL is dynamically loaded from a `bps.conf` configuration file.

## Prerequisites

Before using this system, make sure you have the following installed:

- Python 3.8+  
- FastAPI  
- HTTPX (for asynchronous HTTP requests)
- Uvicorn (for serving the FastAPI app)

## Installation

### 1. Clone the repository or create a directory for your project:

```bash
git clone https://github.com/somkietacode/free_bps
cd free_bps
```

### 2. Install the required dependencies:

```bash
pip install fastapi httpx uvicorn
```

### 3. Create the `bps.conf` configuration file:

In the same directory as the script, create a `bps.conf` file with the following format:

```ini
[backend]
url = http://your-backend-server.com
```

Replace `http://your-backend-server.com` with the actual URL of your backend.

### 4. Run the FastAPI application:

```bash
python bps.py
```

The application will start running on `http://localhost:8000`.

## Endpoints

### `/auth` (POST)

- **Description**:  
   Forwards the `/auth` request to the backend and processes the response. If the backend returns `{"success": "Any_text_you"}`, an API key is returned.
  
- **Request Body**:  
  Sends the original body from the client to the backend for authentication.

- **Response**:  
  - If successful, returns an API key:  
    ```json
    { "API_KEY": "API_KEY_1" }
    ```
  - If authentication fails, returns an error:  
    ```json
    { "error": "Invalid credentials" }
    ```

### `/{endpoint}` (GET)

- **Description**:  
   Forwards requests to the backend, validating the `KEY` query parameter. If the key is valid, the request is forwarded to the backend without the `KEY`.

- **Query Parameter**:
  - `KEY`: The API key returned by the `/auth` endpoint.

- **Response**:  
  - If the key is valid, returns the response from the backend.
  - If the key is invalid or not provided, returns an error:  
    ```json
    { "error": "Invalid key" }
    ```

### `/auth` Behavior

- The BPS system forwards the authentication request to the backend. If the response is successful (contains `"success": "Any_text_you"`), an API key is generated and returned.
- Otherwise, an error message is returned.

### Brute Force Protection

- The BPS system tracks invalid requests (requests with an incorrect API key) and blocks IPs after 5 invalid attempts in 5 seconds. Blocked IPs are prevented from making requests for 24 hours.

## Configuration

The `bps.conf` file contains the backend URL:

```ini
[backend]
url = http://your-backend-server.com
```

Make sure this file is located in the same directory as your FastAPI application.

## Cleaning Up Expired Sessions

Sessions with expired API keys are cleaned up every 60 seconds, ensuring that expired sessions do not persist indefinitely.

## Troubleshooting

- **Error 502 (Bad Gateway)**: This indicates that there is an issue forwarding the request to the backend. Check the backend URL in `bps.conf` for correctness.
- **Error 403 (Forbidden)**: This means the IP has been blocked due to excessive invalid requests.
- **Error 401 (Unauthorized)**: This means the provided API key is either invalid or expired.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
