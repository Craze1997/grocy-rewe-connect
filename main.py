#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py
"""Grocy Connector für REWE eBons
Dieser Code ermöglicht es, REWE eBons zu importieren und die gekauften Produkte in Grocy zu übertragen.
Erforderliche Module:
- requests: Für HTTP-Anfragen
- colorTerminal: Für farbige Konsolenausgaben
- config: Für Konfigurationseinstellungen
- grocyConnector: Für die Interaktion mit Grocy"""

# Importierte Module
import requests
from colorTerminal import OK, WARN, ERROR
from config import BON_HISTORY
from grocy_connector import add_product_to_stock

# CONFIGURATION
RECEIPT_URL = "https://shop.rewe.de/api/receipts/"

def prequisites():
    """
    Überprüft, ob die Konfigurationsdateien vorhanden sind und erstellt sie bei Bedarf."""
    # Check if ignore.txt exists
    try:
        with open("ignore.txt", "r", encoding='utf-8') as f:
            f.read().splitlines()
    except FileNotFoundError:
        print(f"{ERROR} ignore.txt nicht gefunden. Datei wird erstellt..")
        with open("ignore.txt", "w", encoding='utf-8') as f:
            f.write("")

# FETCH LATEST REWE eBons
def fetch_rewe_bon(rtsp: str):
    """
    Ruft den neuesten REWE-eBon ab und gibt die Liste der gekauften Artikel zurück.

    Parameters:
    - RTSP (str): Der RTSP-Token für die Authentifizierung.

    Returns:
    - list or None: Eine Liste der gekauften Artikel, wenn der Abruf erfolgreich ist, andernfalls None.

    Example:
    rewe_bon = fetch_rewe_bon("your_RTSP_token")
    if rewe_bon:
        processrewe_bon(rewe_bon)
    """
    receipt_list = requests.get(RECEIPT_URL, cookies={"rstp": rtsp}, timeout=10).json()
    print(f"{OK} Empfange eBon-Liste der letzten Einkäufe..")

    option_receipts = receipt_list['items']
    for x in range(0, BON_HISTORY, 1):
        print(f"ID: {x}; Vom: {option_receipts[x]['receiptTimestamp']}; Summe: {option_receipts[x]['receiptTotalPrice']/100}€")

    while True:
        option = int(input("Welchen Bon möchtest du an Grocy senden? (ID): "))
        if 0 <= option < BON_HISTORY:
            break
        else:
            print(f"{ERROR} Bitte wähle einen Bon zwischen 0 und {BON_HISTORY-1} aus.")


    rewe_bon = requests.get(RECEIPT_URL + option_receipts[option]['receiptId'], cookies={"rstp": rtsp}, timeout=10)

    if rewe_bon.status_code == 200:
        print(f"{OK} Rewe-Bon mit der UUID {option_receipts[option]['receiptId']} wurde erfolgreich abgerufen")
        return rewe_bon.json()["articles"]
    else:
        print(f"{ERROR} Fehler beim Abrufen des Rewe-Bons. Statuscode: {rewe_bon.status_code}")
        return None

# Iterate selected eBon
def processrewe_bon(rewe_bon):
    """
    Verarbeitet einen REWE-Kassenbon.

    Parameters:
    - rewe_bon (list): Eine Liste von Produkten auf dem REWE-Bon.

    Prints:
    - Informationen zu jedem Produkt auf dem Bon.
    - Fügt jedes Produkt dem Lagerbestand mit der entsprechenden Menge hinzu.

    Returns:
    - None

    Example:
    processrewe_bon([
        {'quantity': '2', 'productName': 'Milch', 'nan': '123456789', 'unitPrice': 150, 'totalPrice': 300},
        {'quantity': '1', 'productName': '', 'nan': '987654321', 'unitPrice': 120, 'totalPrice': 120}
    ])
    """
    for product in rewe_bon:
        if 'productName' in product:
            print(f"{OK} {int(product['quantity'])}x {product['productName']}, EAN: {product['nan']}, Stückpreis: {product['unitPrice']/100}€")
            add_product_to_stock(product['nan'], int(product['quantity']), product['unitPrice']/100)
        else:
            print(f"{WARN} Produkt mit EAN {product['nan']} ({int(product['quantity'])}x {product['totalPrice']}) hat keinen Produktnamen, es handelt sich dabei wahrscheinlich um Pfand, Saison- oder Thekenware.")

# MAIN EXECUTION
def main():
    """
    Hauptfunktion des Rewe2Grocy Connectors.

    - Fordert den RTSP-Token an und verarbeitet den REWE-Einkauf.
    - Benutzer wird aufgefordert, sich auf shop.rewe.de einzuloggen und den RTSP-Token aus den Entwicklertools zu kopieren.
    - Ruft die Funktion fetch_rewe_bon auf, um den REWE-Bon abzurufen.
    - Wenn der Bon vorhanden ist, ruft die Funktion processrewe_bon auf, um den Bon zu verarbeiten.

    Parameters:
    - None

    Returns:
    - None

    Example:
    main()
    """
    # REQUEST RTSP COOKIE
    print("Willkommen im Rewe2Grocy Connector! Bevor wir den Einkauf übertragen können, benötigen wir den RTSP Token.\nLogge dich dazu auf shop.rewe.de ein und kopiere den Cookie aus den Entwicklertools deines Browsers.")
    rtsp = input("RTSP Token: ")

    rewe_bon = fetch_rewe_bon(rtsp)

    if rewe_bon:
        processrewe_bon(rewe_bon)

if __name__ == "__main__":
    main()
