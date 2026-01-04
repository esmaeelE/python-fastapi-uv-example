"""FastAPI application to get server's public IP address and geolocation information."""

from fastapi import Query
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from typing import Dict, Any


app = FastAPI()


def get_ip_address() -> str:
    """Fetch the public IP address of the server."""

    try:
        # response = requests.get("https://api.ipify.org?format=json")
        response = requests.get("https://ifconfig.co/ip")
        response.raise_for_status()
        ip_data: dict[str, str] = {"ip": response.text.strip()}
        return ip_data.get("ip", "IP address not found")
    except requests.RequestException as e:
        return f"Error occurred: {e}"


@app.get("/ip")
async def get_client_ip(request: Request) -> JSONResponse:
    return JSONResponse(content={"ip": get_ip_address()})


def get_all(ip: str = "") -> Dict[str, Any]:  # Add return type annotation
    """Fetch all data from server the given IP address."""
    try:
        url = f"https://ifconfig.co/json?ip={ip}"
        response = requests.get(url)
        response.raise_for_status()

        key_value: Dict[str, str] = response.json()
        return key_value

    except requests.RequestException as e:
        return {"error": f"Error occurred while fetching data from server: {e}"}


def get_geolocation(ip: str) -> Dict[str, Any]:  # Add return type annotation
    """Fetch geolocation information for the given IP address."""
    try:
        url = f"https://ifconfig.co/json?ip={ip}"
        response = requests.get(url)
        response.raise_for_status()
        geolocation_data = response.json()

        # Extracting geolocation info
        location_info: Dict[str, str] = {
            "ip": geolocation_data.get("ip", ""),
            "city": geolocation_data.get("city", ""),
            "country": geolocation_data.get("country", ""),
            "latitude": geolocation_data.get("latitude", ""),
            "longitude": geolocation_data.get("longitude", ""),
        }
        return location_info

    except requests.RequestException as e:
        return {"error": f"Error occurred while fetching geolocation: {e}"}


@app.get("/geo")
async def get_geolocation_endpoint() -> JSONResponse:
    ip = get_ip_address()
    if "Error" in ip:
        return JSONResponse(status_code=500, content={"error": ip})

    location_info = get_geolocation(ip)
    if "error" in location_info:
        return JSONResponse(status_code=500, content=location_info)

    return JSONResponse(content=location_info)


@app.get("/")
async def read_root() -> JSONResponse:
    return JSONResponse(
        content={
            "message": "Welcome to the IP Address API."
            "see help: /help"
            " endpoints: /ip and /geo"
        }
    )


@app.get("/all")
async def get_all_endpoint(
    ip: str = Query(default="", description="IP address to lookup")
) -> JSONResponse:
    data = get_all(ip)
    return JSONResponse(content=data)


@app.get("/help")
async def read_help() -> JSONResponse:
    help_text = {
        "/": "Welcome message with available endpoints.",
        "/ip": "Get the server's public IP address.",
        "/geo": "Get the geolocation information of the server's public IP address.",
        "/docs": "Interactive API documentation (Swagger UI).",
        "/help": "This help message.",
    }
    return JSONResponse(content=help_text)
