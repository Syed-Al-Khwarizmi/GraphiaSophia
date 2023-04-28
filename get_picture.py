import requests
from bs4 import BeautifulSoup
from pyvis.network import Network

# Open the HTML file in a BeautifulSoup object.
soup = BeautifulSoup(open("experiment.html", "r"), "html.parser")

# Get the network graph from the HTML file.
network = soup.find("visNetwork")

# Use the vis.Network.export() method to export the network graph to a PNG image.
png_image = network.export("png")

# Save the PNG image to a file.
with open("experiment.png", "wb") as f:
    f.write(png_image)