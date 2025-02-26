    import requests
    from bs4 import BeautifulSoup

    url = "https://www.example.com/safety-ratings"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.prettify())  # View structure of the page
    else:
        print("Failed to fetch data")

    safety_data = []
    for row in soup.find_all("div", class_="crime-data"):  # Change selector as needed
        area = row.find("h2").text
        crime_rate = row.find("span", class_="crime-rate").text
        safety_data.append({"area": area, "crime_rate": crime_rate})
    import pandas as pd

    df = pd.DataFrame(safety_data)
    df.to_csv("safety_data.csv", index=False)
    print(df.head())
    def classify_safety(crime_rate):
        return "Unsafe" if int(crime_rate) > 50 else "Safe"

    df["safety_status"] = df["crime_rate"].apply(classify_safety)
    print(df)
