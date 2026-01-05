from typing import Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import cast
import requests
import logging


# Initialize the FastAPI app and logging
app = FastAPI()

logging.basicConfig(level=logging.INFO)


class IPResponse(BaseModel):
    ip: str


class GeolocationResponse(BaseModel):
    ip: str
    city: str
    country: str
    latitude: str
    longitude: str


class ErrorResponse(BaseModel):
    error: str


def fetch_data_from_url(url: str) -> Dict[str, Any]:
    """Helper function to fetch data from a URL with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad HTTP status

        # Cast the response to Dict[str, Any]
        # Tells mypy the result is of the expected type
        return cast(Dict[str, Any], response.json())

    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        # Return error response as a dictionary
        return {"error": str(e)}  # Ensuring error message is of type str


def get_ip_address() -> str:
    """Fetch the public IP address of the server."""
    ip_data = fetch_data_from_url("https://ifconfig.co/ip")

    # Return the IP if available, or default message if not
    return str(ip_data.get("ip", "IP address not found"))


def get_geolocation(ip: str) -> Dict[str, Any]:
    """Fetch geolocation information for the given IP address."""
    url = f"https://ifconfig.co/json?ip={ip}"
    geo_data = fetch_data_from_url(url)

    if "error" in geo_data:
        return geo_data  # Return error as part of dict

    return {
        "ip": geo_data.get("ip", ""),
        "city": geo_data.get("city", ""),
        "country": geo_data.get("country", ""),
        "latitude": geo_data.get("latitude", ""),
        "longitude": geo_data.get("longitude", ""),
    }


@app.get("/ip", response_model=IPResponse)
async def get_client_ip() -> IPResponse:
    """Endpoint to get the server's public IP address."""
    ip = get_ip_address()
    if "Error" in ip:
        raise HTTPException(status_code=500, detail=ip)
    return IPResponse(ip=ip)


@app.get("/geo", response_model=GeolocationResponse)
async def get_geolocation_endpoint() -> JSONResponse:
    """Endpoint to get geolocation info of the server's public IP address."""
    ip = get_ip_address()
    if "Error" in ip:
        raise HTTPException(status_code=500, detail=ip)

    location_info = get_geolocation(ip)
    if "error" in location_info:
        raise HTTPException(status_code=500, detail=location_info["error"])

    return JSONResponse(content=location_info)


@app.get("/", response_model=Dict[str, str])
async def read_root() -> Dict[str, str]:
    """Welcome message and available endpoints."""
    return {
        "message": "Welcome to the IP Address API. See help: /help.",
        "endpoints": "/ip and /geo",
    }


@app.get("/all", response_model=Dict[str, Any])
async def get_all_endpoint(
    ip: str = Query(default="", description="IP address to lookup"),
) -> JSONResponse:
    """Get all available data for the provided IP address."""
    url = f"https://ifconfig.co/json?ip={ip}"
    data = fetch_data_from_url(url)
    return JSONResponse(content=data)


@app.get("/help", response_model=Dict[str, str])
async def read_help() -> Dict[str, str]:
    """Endpoint for help documentation."""
    help_text = {
        "/": "Welcome message with available endpoints.",
        "/ip": "Get the client's public IP address.",
        "/geo": "Get the geolocation information of the server's public IP address.",
        "/docs": "Interactive API documentation (Swagger UI).",
        "/redoc": "Alternative API documentation (ReDoc).",
        "/help": "Show this help message.",
    }
    return help_text
