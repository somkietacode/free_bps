# Backend Protection System (BPS)
![URL based backend protection system](https://github.com/user-attachments/assets/21c45067-d764-4652-9e8f-ad7881c076ee)

The **Backend Protection System (BPS)** acts as a reverse proxy, forwarding client requests to your backend while ensuring the security and integrity of your API. It validates API keys, manages role-based permissions, handles authentication via backend response, and protects against brute-force attacks.

## Features

1. **Authentication Handling**:  
   Forwards the `/auth` request to the backend. If the backend responds with `{"success": "Any_text_you"}`, an API key is generated and returned.

2. **API Key Validation**:  
   Validates the API key (`KEY` parameter in the query string) for every non-auth request and forwards it to the backend without the `KEY` parameter.

3. **Role-Based Access Control (RBAC)**:  
   Restricts access to endpoints based on roles, as defined in the `permission.conf` configuration file.

4. **HTTP Method Permissions**:  
   Manages permissions for specific HTTP methods (e.g., `GET`, `POST`) per endpoint, providing fine-grained access control.

5. **Brute Force Protection**:  
   Tracks invalid requests and blocks IPs that make more than 5 failed attempts in 5 seconds.

6. **Dynamic Configuration**:  
   The backend URL and role-based permissions are dynamically loaded from configuration files (`bps.conf` and `permission.conf`).

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

[user_role]
atribute_name = role
```

Replace `http://your-backend-server.com` with the actual URL of your backend.

### 4. Create the `permission.conf` configuration file:
![mep](https://github.com/user-attachments/assets/d27a1beb-d446-43f7-aec9-d78918f79a45)

In the same directory, create a `permission.conf` file to define role-based access control:

```ini
[some_endpoint]
GET = admin,user
POST = admin

[another_endpoint]
GET = admin
```

Each section (`[endpoint_name]`) specifies the roles allowed for specific HTTP methods (`GET`, `POST`, etc.).

### 5. Run the FastAPI application:

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
    { "API_KEY": API_KEY }
    ```
  - If authentication fails, returns an error:  
    ```json
    { "error": "Invalid credentials" }
    ```

### `/{endpoint}` (All HTTP Methods)

- **Description**:  
   Forwards requests to the backend, validating the `KEY` query parameter and the user role. The method and permissions are checked against the `permission.conf` configuration.

- **Query Parameter**:
  - `KEY`: The API key returned by the `/auth` endpoint.

- **Permissions**:
  - The `permission.conf` file defines the roles and HTTP methods allowed for each endpoint.

- **Response**:  
  - If the key and role are valid, forwards the request to the backend and returns its response.
  - If the key is invalid or the user lacks permission, returns an error:  
    ```json
    { "error": "Not allowed" }
    ```

### Brute Force Protection

- The BPS system tracks invalid requests (requests with an incorrect API key) and blocks IPs after 5 invalid attempts in 5 seconds. Blocked IPs are prevented from making requests for 24 hours.

## Configuration

### `bps.conf` File:
Defines the backend URL and the user role attribute:

```ini
[backend]
url = http://your-backend-server.com

[user_role]
atribute_name = role
```

### `permission.conf` File:
Manages role-based access control per endpoint and HTTP method:

```ini
[some_endpoint]
GET = admin,user
POST = admin

[another_endpoint]
GET = admin
```

## Cleaning Up Expired Sessions

Sessions with expired API keys are cleaned up every 60 seconds, ensuring that expired sessions do not persist indefinitely.

## Troubleshooting

- **Error 502 (Bad Gateway)**: Indicates an issue forwarding the request to the backend. Check the backend URL in `bps.conf` for correctness.
- **Error 403 (Forbidden)**: The user’s role does not have permission to access the endpoint or method.
- **Error 401 (Unauthorized)**: The provided API key is either invalid or expired.
- **Error 400 (Bad Request)**: Indicates a missing or improperly formatted `KEY` query parameter.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
