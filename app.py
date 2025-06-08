import streamlit as st
import requests
from datetime import date, timedelta

# Clé API RapidAPI
RAPIDAPI_KEY = "14d7b11f53msh7545ec16c257ac1p112f4djsn21b340dfc003"
RAPIDAPI_HOST = "tripadvisor16.p.rapidapi.com"

st.title("🌍 Recherche d'hôtels (TripAdvisor API)")

query = st.text_input("Tapez une ville...")

col1, col2 = st.columns(2)
with col1:
    check_in = st.date_input("Date d'arrivée (check-in)", value=date.today() + timedelta(days=1), min_value=date.today())
with col2:
    check_out = st.date_input("Date de départ (check-out)", value=date.today() + timedelta(days=2), min_value=date.today() + timedelta(days=1))

if check_in >= check_out:
    st.warning("⚠️ La date de départ doit être après la date d'arrivée.")
else:
    if query:
        url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
        params = {"query": query}
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data.get("data", [])

            if not results:
                st.info("Aucune ville correspondante trouvée.")
            else:
                first_city = results[0]
                city_name = first_city.get("title", "Ville inconnue")
                geo_id = first_city.get("geoId")

                st.success(f"Recherche d'hôtels ...")

                hotel_url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
                hotel_params = {
                    "geoId": geo_id,
                    "checkIn": check_in.strftime('%Y-%m-%d'),
                    "checkOut": check_out.strftime('%Y-%m-%d'),
                    "pageNumber": "1",
                    "currencyCode": "CAD"
                }

                hotel_response = requests.get(hotel_url, headers=headers, params=hotel_params)

                if hotel_response.status_code == 200:
                    hotel_data = hotel_response.json()
                    hotels = hotel_data.get("data", {}).get("data", [])

                    if not hotels:
                        st.info("Aucun hôtel trouvé pour ces dates.")
                    else:
                        st.markdown("## Résultats d'hôtels 🔍")
                        rows = [hotels[i:i+4] for i in range(0, len(hotels), 4)]

                        for row in rows:
                            cols = st.columns(4)
                            for idx, hotel in enumerate(row):
                                with cols[idx]:
                                    if "cardPhotos" in hotel and hotel["cardPhotos"]:
                                        image_url = hotel["cardPhotos"][0]["sizes"]["urlTemplate"].replace("{width}", "300").replace("{height}", "200")
                                        st.image(image_url, use_container_width=True)
                                    else:
                                        st.text("Image non disponible")

                                    st.markdown(f"### {hotel.get('title', 'Nom indisponible')}", unsafe_allow_html=True)

                                    if "bubbleRating" in hotel:
                                        st.markdown(f"⭐ **{hotel['bubbleRating'].get('rating', 'N/A')}**")

                                    if "priceForDisplay" in hotel:
                                        st.markdown(f"💵 {hotel['priceForDisplay']}")

                                    url = "https://www.tripadvisor.ca/"
                                    if "commerceInfo" in hotel:
                                        for info in hotel["commerceInfo"]:
                                            if "clickTrackingUrl" in info:
                                                url = info["clickTrackingUrl"]
                                                break

                                    if url:
                                        # Bouton sous forme de lien HTML qui ouvre dans un nouvel onglet
                                        st.markdown(
                                            f'<a href="{url}" target="_blank" style="text-decoration:none;">'
                                            f'<button style="background-color:#008CBA;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">Réserver</button>'
                                            f'</a>',
                                            unsafe_allow_html=True
                                        )
                else:
                    st.error("Erreur lors de la récupération des hôtels.")
                    st.text(hotel_response.text)
        else:
            st.error("Erreur lors de la récupération de la ville.")
            st.text(response.text)
