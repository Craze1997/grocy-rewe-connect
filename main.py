# main.py
import requests
from colorTerminal import OK, WARN, ERROR
from config import GROCY_LOCATION_ID, BON_HISTORY
from grocyConnector import addProductToStock

# CONFIGURATION
RECEIPT_URL = "https://shop.rewe.de/api/receipts/"

# FETCH LATEST REWE eBons
def fetchReweBon(RTSP):
    """
    Ruft den neuesten REWE-eBon ab und gibt die Liste der gekauften Artikel zurück.

    Parameters:
    - RTSP (str): Der RTSP-Token für die Authentifizierung.

    Returns:
    - list or None: Eine Liste der gekauften Artikel, wenn der Abruf erfolgreich ist, andernfalls None.

    Example:
    reweBon = fetchReweBon("your_RTSP_token")
    if reweBon:
        processReweBon(reweBon)
    """
    receiptList = requests.get(RECEIPT_URL, cookies={"rstp": RTSP}, timeout=10).json()
    print(f"{OK} Empfange eBon-Liste der letzten Einkäufe..")

    bonHistory = 10

    optionReceipts = receiptList['items']
    for x in range(0, BON_HISTORY, 1):
        print(f"ID: {x}; Vom: {optionReceipts[x]['receiptTimestamp']}; Summe: {optionReceipts[x]['receiptTotalPrice']/100}€")

    while True:
        option = int(input("Welchen Bon möchtest du an Grocy senden? (ID): "))
        if 0 <= option < BON_HISTORY:
            break
        else:
            print(f"{ERROR} Bitte wähle einen Bon zwischen 0 und {BON_HISTORY-1} aus.")


    reweBon = requests.get(RECEIPT_URL + optionReceipts[option]['receiptId'], cookies={"rstp": RTSP}, timeout=10)

    if reweBon.status_code == 200:
        print(f"{OK} Rewe-Bon mit der UUID {optionReceipts[option]['receiptId']} wurde erfolgreich abgerufen")
        return reweBon.json()["articles"]
    else:
        print(f"{ERROR} Fehler beim Abrufen des Rewe-Bons. Statuscode: {reweBon.status_code}")
        return None

# Iterate selected eBon
def processReweBon(reweBon):
    """
    Verarbeitet einen REWE-Kassenbon.

    Parameters:
    - reweBon (list): Eine Liste von Produkten auf dem REWE-Bon.

    Prints:
    - Informationen zu jedem Produkt auf dem Bon.
    - Fügt jedes Produkt dem Lagerbestand mit der entsprechenden Menge hinzu.

    Returns:
    - None

    Example:
    processReweBon([
        {'quantity': '2', 'productName': 'Milch', 'nan': '123456789', 'unitPrice': 150, 'totalPrice': 300},
        {'quantity': '1', 'productName': '', 'nan': '987654321', 'unitPrice': 120, 'totalPrice': 120}
    ])
    """
    for product in reweBon:
        try:
            print(f"{OK} {int(product['quantity'])}x {product['productName']}, EAN: {product['nan']}, Stückpreis: {product['unitPrice']/100}€")
            addProductToStock(product['nan'], int(product['quantity']), product['unitPrice']/100, GROCY_LOCATION_ID)
        except:
            print(f"{WARN} Produkt mit EAN {product['nan']} ({int(product['quantity'])}x {product['totalPrice']}) hat keinen Produktnamen, es handelt sich dabei wahrscheinlich um Pfand, Saison- oder Thekenware.")

# MAIN EXECUTION
def main():
    """
    Hauptfunktion des Rewe2Grocy Connectors.

    - Fordert den RTSP-Token an und verarbeitet den REWE-Einkauf.
    - Benutzer wird aufgefordert, sich auf shop.rewe.de einzuloggen und den RTSP-Token aus den Entwicklertools zu kopieren.
    - Ruft die Funktion fetchReweBon auf, um den REWE-Bon abzurufen.
    - Wenn der Bon vorhanden ist, ruft die Funktion processReweBon auf, um den Bon zu verarbeiten.

    Parameters:
    - None

    Returns:
    - None

    Example:
    main()
    """
    # REQUEST RTSP COOKIE
    print("Willkommen im Rewe2Grocy Connector! Bevor wir den Einkauf übertragen können, benötigen wir den RTSP Token.\nLogge dich dazu auf shop.rewe.de ein und kopiere den Cookie aus den Entwicklertools deines Browsers.")
    RTSP = input("RTSP Token: ")

    reweBon = fetchReweBon(RTSP)

    if reweBon:
        processReweBon(reweBon)

if __name__ == "__main__":
    main()
