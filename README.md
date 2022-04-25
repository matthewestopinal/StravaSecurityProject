# Strava Data Tools

Data tools created to investigate how much information is gleanable from Strava. Investigating results from our [survey](https://docs.google.com/forms/d/e/1FAIpQLSeGa4oRXdG83JrqNwLlDvE6D1b9JQJP_lmYOSlNpiCFFuiWWw/viewform?usp=sf_link) on sentiment and understanding of Privacy in social media spaces related to fitness.

Contains functions to manipulate, visualize, and analyze GPS Data from a Strava Data Dump.

Requires plotly, fitparse, numpy, and pandas.

Note: As [MapBox](https://www.mapbox.com/) is required for certain visualizations, a mapbox token will be required for these functions.

Note: A [Google Maps](https://github.com/googlemaps/google-maps-services-python) API token is also required to analyze privacy zones. Strava stores Privacy Zones using text addresses, so we send those to Google Maps to receive coordinates.
