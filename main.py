# main.py
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore pylint: disable=E0401
from colorTerminal import OK, WARN, ERROR
from config import GROCY_LOCATION_ID
from grocyConnector import addProductToStock

# CONFIGURATION
RECEIPT_URL = "https://shop.rewe.de/api/receipts/"

# FETCH LATEST REWE eBons
def fetchReweBon(RTSP):
    receiptList = requests.get(RECEIPT_URL, cookies={"rstp": RTSP}, timeout=10).json()
    print(f"{OK} Empfange eBon-Liste der letzten Einkäufe..")

    optionReceipts = receiptList['items']
    for x in range(0, 5, 1):
        print(f"ID: {x}; Vom: {optionReceipts[x]['receiptTimestamp']}; Summe: {optionReceipts[x]['receiptTotalPrice']/100}€")

    option = int(input("Welchen Bon möchtest du an Grocy senden? (ID): "))
    reweBon = requests.get(RECEIPT_URL + optionReceipts[option]['receiptId'], cookies={"rstp": RTSP}, timeout=10)
    
    if reweBon.status_code == 200:
        print(f"{OK} Rewe-Bon mit der UUID {optionReceipts[option]['receiptId']} wurde erfolgreich abgerufen")
        return reweBon.json()["articles"]
    else:
        print(f"{ERROR} Fehler beim Abrufen des Rewe-Bons. Statuscode: {reweBon.status_code}")
        return None

# Iterate selected eBon
def processReweBon(reweBon):
    for product in reweBon:
        try:
            print(f"{OK} {int(product['quantity'])}x {product['productName']}, EAN: {product['nan']}, Stückpreis: {product['unitPrice']/100}€")
            addProductToStock(product['nan'], int(product['quantity']), 1, product['unitPrice']/100, GROCY_LOCATION_ID)
        except:
            print(f"{WARN} Produkt mit EAN {product['nan']} ({int(product['quantity'])}x {product['totalPrice']}) hat keinen Produktnamen, es handelt sich dabei wahrscheinlich um Pfand, Saison- oder Thekenware.")

# MAIN EXECUTION
def main():
    # REQUEST RTSP COOKIE
    print("Willkommen im Rewe2Grocy Connector! Bevor wir den Einkauf übertragen können, benötigen wir den RTSP Token.\nLogge dich dazu auf shop.rewe.de ein und kopiere den Cookie aus den Entwicklertools deines Browsers.")
    RTSP = input("RTSP Token: ")

    reweBon = fetchReweBon(RTSP)
    
    if reweBon:
        processReweBon(reweBon)

if __name__ == "__main__":
    main()
