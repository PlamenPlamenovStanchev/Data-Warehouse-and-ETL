import logging
import pandas as pd
import requests

from bs4 import BeautifulSoup

def extract_weather_data_from_sinoptik(city: str = "Pleven") -> pd.DataFrame:
    """
    Extracts weather data from the Sinoptik website for a given city.

    Args:
        city (str): The name of the city to extract weather data for.
    """
    url = f"https://www.sinoptik.bg/pleven-bulgaria-10072820"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    }

    logging.info(f"Extracting weather data for {city} from Sinoptik API...")

    try:
        response = requests.get(url, headers=header)
    except Exception as e:
        logging.error(f"Error occurred while making the request: {e}")
        
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        temp_node = soup.find("span", class_="wfCurrentTemp")
        feel_node = soup.find("span", class_="wfCurrentFeelTemp")
        temperature = temp_node.text.strip() if temp_node else None
        feels_like = feel_node.text.strip() if feel_node else None

        if temperature is None or feels_like is None:
            raise ValueError("Could not find temperature or feels like data in the response.")
        
    except Exception as e:
        logging.error(f"Error occurred while parsing the response: {e}")
       
    df = pd.DataFrame({
        "city": [city],
        "temperature": [temperature],
        "feels_like": [feels_like]
    })

    logging.info(f"Weather data for {city} extracted successfully.")
    return df