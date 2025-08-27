import requests
import mysql.connector
from tabulate import tabulate

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='roots',
    database='c12'
)
curr = conn.cursor()

# Create the 'Places' table if it doesn't exist
table_statement ='create table if not exists Places (S_No int auto_increment primary key,Location varchar(50),Latitude varchar(20),Longitude varchar(20))'
curr.execute(table_statement)
conn.commit()

# Insert default data only if the table is empty
curr.execute('select count(*) from Places')
if curr.fetchone()[0] == 0:
    default_places = [
        ("Anand", "22.5645", "72.9289"),
        ("Ahmedabad", "23.0225", "72.5714"),
        ("Bangalore", "12.9716", "77.5946")
    ]

    insert_statement = 'insert into Places (Location, Latitude, Longitude) values (%s, %s, %s)'
    curr.execute(default_places)
    curr.execute(insert_statement)
    conn.commit()

# Function to display all saved places
def show_places():
    curr.execute('select * from Places')
    places = curr.fetchall()
    print("\nAvailable places in the database:")
    print(tabulate(places, headers=["S_No", "Location", "Latitude", "Longitude"], tablefmt="pipe"))

# Function to fetch weather data using OpenWeatherMap API
def fetch_weather_data(location):
    curr.execute("select Latitude, Longitude from Places where Location = %s", (location,))
    result = curr.fetchone()
    if result:
        latitude, longitude = result
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=699d5005bb8ec229b0046342fafab63b&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            pressure=weather_data['main']['pressure']

            print("\nWeather in ",location,":")
            print("Temperature: ",temp,"°C")
            print("Humidity: ",humidity,"%")
            print("Description: ",description)
            print("Pressure: ",pressure,'hPa')
        else:
            print("Error fetching weather data. Please check your API key.")
    else:
        print("Location not found in the database.")

# Function to add a new location to the database
def add_location():
    address = input("Enter new location to add: ")
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&limit=1&apiKey=00341ee49f2248fdb62fab4566728a29"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            result = data["features"][0]
            latitude = result["geometry"]["coordinates"][1]
            longitude = result["geometry"]["coordinates"][0]

            # Insert new location into the database
            insert_statement = 'insert into Places (Location, Latitude, Longitude) VALUES (%s, %s, %s)'
            curr.execute(insert_statement, (address, latitude, longitude))
            conn.commit()
            print(f"{address} added successfully!")
        else:
            print("Location not found.")
    else:
        print("Error fetching coordinates. Please check your API key.")

# Main function to drive the program
def main():
    show_places()

    while True:
        print("\nMenu:")
        print("1. View weather of a place")
        print("2. Add a new place")
        print("3. Exit")
        choice = int(input("Choose an option: "))

        if choice == 1:
            location = input("\nEnter the location to view weather: ")
            fetch_weather_data(location)
        elif choice == 2:
            add_location()
        elif choice == 3:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main function
main()
