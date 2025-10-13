import requests


def fetch_weather(city):
    api_key = "your_api_key_here"  # Replace with your actual API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Weather in {city}:")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Condition: {data['weather'][0]['description']}")
    else:
        print("Failed to fetch weather data. Please check the city name or API key.")


if __name__ == "__main__":
    city = input("Enter the name of a city: ")
    fetch_weather(city)
