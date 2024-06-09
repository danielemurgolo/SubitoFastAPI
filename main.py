import re
from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import httpx
from utils import get_coordinates, remove_vetrina_prefix
from geopy.distance import geodesic

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


class VespaListing(BaseModel):
    link: str
    price: str
    location: str
    distance: float


@app.get("/vespa_listings/")
async def get_vespa_listings():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url="https://www.subito.it/annunci-emilia-romagna-vicino/vendita/moto-e-scooter/?q=vespa&bb=000053&pe=2000&me=20&cce=125"
            )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all("div", class_=re.compile(r"item-card"))
        modena_coords = get_coordinates("Modena")
        vespa_listings = []
        for product in products:
            link = product.find("a", class_="SmallCard-module_link__hOkzY")["href"]
            price = product.find("p", class_="index-module_price__N7M2x").text.strip()
            location_span = product.find_all(
                "span", class_="index-module_sbt-text-atom__ed5J9"
            )
            location = remove_vetrina_prefix(
                f"{location_span[0].text.strip()} {location_span[1].text.strip()}"
            )
            coords = get_coordinates(location)
            distance = geodesic(modena_coords, coords).km
            vespa_listings.append(
                VespaListing(
                    link=link, price=price, location=location, distance=distance
                )
            )

        return vespa_listings

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        # Handle other request errors
        raise HTTPException(status_code=500, detail=str(e))

    response = requests.get(
        url="https://www.subito.it/annunci-emilia-romagna-vicino/vendita/moto-e-scooter/?q=vespa&bb=000053&pe=2000&me=20&cce=125"
    )
    soup = BeautifulSoup(response.text, "html.parser")

    products = soup.find_all("div", class_=re.compile(r"item-card"))

    print(products)

    return products
