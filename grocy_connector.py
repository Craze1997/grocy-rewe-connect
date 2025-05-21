"""Grocy Connector for Grocy API
This code allows you to add products to your Grocy instance via ean codes.
It includes functions to add products to stock, create new products, and assign ean codes to existing products.
It also handles user input for creating new products or assigning ean codes."""
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore pylint: disable=E0401
from colorTerminal import OK, WARN, ERROR
from config import GROCY_API_URL, GROCY_API_KEY                           # pylint: disable=E0611

requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # type: ignore pylint: disable=E1101

IGNORE_FILE = "ignore.txt"
GROCY_BASE_URL = GROCY_API_URL + "/api"
GROCY_HEADER = {"GROCY-API-KEY": GROCY_API_KEY, "accept": "application/json", "Content-Type": "application/json"}
ENDPOINT_SYSINFO = GROCY_BASE_URL + "/system/info"
ENDPOINT_GET_BYBARCODE = GROCY_BASE_URL + "/stock/products/by-barcode/"
ENDPOINT_ADD_BARCODE_BY_ID = GROCY_BASE_URL + "/objects/product_barcodes"
ENDPOINT_ADD_PRODUCT = GROCY_BASE_URL + "/objects/products"
ENDPOINT_GET_BYID = GROCY_BASE_URL + "/objects/products?query%5B%5D=id%3D"

def add_product_to_stock(itemean: int, amount: int, price):
    """Add a Product to GROCY INSTANCE via ean"""

    with open(IGNORE_FILE, 'r', encoding='utf-8') as data:
        for ean in data:
            try:
                if itemean == int(ean.strip()):
                    return 0
            except ValueError:
                print(f"{ERROR} Konnte aktuelle ean nicht mit der Ignore-Liste vergleichen")

    print(f"Suche nach '{itemean}' in der Datenbank..")
    try:
        product_by_barcode = requests.get(ENDPOINT_GET_BYBARCODE + str(itemean), headers=GROCY_HEADER, timeout=10, verify=False).json()
        print(f"{OK} Artikel gefunden: {product_by_barcode['product']['name']}")
        product = {
            "amount": amount,
            "transaction_type": "purchase",
            "price": price
        }
        add_to_stock = requests.post(ENDPOINT_GET_BYBARCODE + str(itemean) + "/add", json=product, headers=GROCY_HEADER, timeout=10, verify=False)
        if add_to_stock.status_code == 200:
            print(f"{OK} {amount}x {product_by_barcode['product']['name']} wurde dem Bestand hinzugefügt. Stückpreis: {price}€")
        else:
            print(f"{ERROR} {itemean} konnte nicht hinzugefügt werden... :( Bitte prüfe den Bestand in Grocy zu diesem Produkt.")
    except requests.exceptions.RequestException:
        print(f"{WARN} Es wurde kein Produkt mit der ean {itemean} gefunden. Möchtest du ein Produkt anlegen oder die ean einem Produkt zuweisen?")
        na_product = None
        while na_product is None:
            try:
                print("(1) Neues Produkt erstellen\n(2) ean einem bestehenden Produkt hinzufügen\n(8) Einmal überspringen\n(9) Immer überspringen\n(0) Beenden")
                na_product = int(input())
            except ValueError:
                print(f"{ERROR} Bitte nutze eine der angegebenen Optionen, tippe dafür einfach die Zahl.")
        if na_product == 0:
            exit(0)
        if na_product == 8:
            return 0
        elif na_product == 1:
            print("Starte Dialog für: PRODUKT ANLEGEN\n\n\n")
            print("Name des Produkts: ")
            product_name = input()
            print("\nMengeneinheiten: (2) Stück, (3) Packung, (4) Flasche\nMengeneinheit: ")
            product_qu = input()
            product_info = {
                "name": product_name,
                "qu_id_purchase": product_qu,
                "qu_id_stock": product_qu
            }
            try:
                print(product_info)
                create_product = requests.post(ENDPOINT_ADD_PRODUCT, headers=GROCY_HEADER, timeout=10, json=product_info, verify=False)
                print(f"{create_product}\n{create_product.content}")
                product_id = create_product.json()
                product_id = product_id['created_object_id']
                print(product_id)
                if create_product.status_code == 200:
                    print(f"{OK} Produkt {product_name} wurde angelegt. ID des Produkts: {product_id}\nFüge ean hinzu...")
                    newean = {
                        "barcode": itemean,
                        "product_id": product_id,
                        "amount": 1
                    }
                    postreq = requests.post(ENDPOINT_ADD_BARCODE_BY_ID, headers=GROCY_HEADER, json=newean, timeout=10, verify=False)
                    if postreq.status_code == 200:
                        print(f"{OK} ean wurde dem Produkt hinzugefügt. Dialog wird neugestartet.")
                    else:
                        print(f"{ERROR} ean konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                else:
                    print(f"{ERROR} Antwort von Grocy war != 200, bitte prüfen. Dialog wird Pausiert, ENTER zum fortfahren...")
                    input()
            except requests.exceptions.RequestException:
                print(f"{ERROR} Fehler beim Anlegen des Produktes. Dialog wird neugestartet.")
            add_product_to_stock(itemean, amount, price)
        elif na_product == 2:
            product_id = None
            print("Bitte schaue in GROCY nach dem gewünschten Produkt und kopiere die ID aus der URL und gebe sie hier ein: ")
            while product_id is None:
                try:
                    product_id = int(input())
                    try:
                        find_product_by_id = requests.get(ENDPOINT_GET_BYID + str(product_id), headers=GROCY_HEADER, timeout=10, verify=False).json()
                        find_product_by_id_data = find_product_by_id[0]
                        print(f"{OK} Produkt gefunden: {find_product_by_id_data['name']} ... ean wird hinterlegt..")
                        try:
                            newean = {
                                "barcode": itemean,
                                "product_id": find_product_by_id_data['id'],
                                "amount": 1
                            }
                            postreq = requests.post(ENDPOINT_ADD_BARCODE_BY_ID, headers=GROCY_HEADER, json=newean, timeout=10, verify=False)
                            if postreq.status_code == 200:
                                print(f"{OK} ean wurde dem Produkt hinzugefügt. Dialog wird neugestartet.")
                            else:
                                print(f"{ERROR} ean konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                        except requests.exceptions.RequestException:
                            print(f"{ERROR} ean konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                        add_product_to_stock(itemean, amount, price)
                    except requests.exceptions.RequestException as exc:
                        product_id = None
                        raise RuntimeError("Failed to find product by ID") from exc
                except ValueError:
                    print(f"{ERROR} Produkt nicht gefunden, versuche es noch einmal.")
        elif na_product == 9:
            with open(IGNORE_FILE, 'a', encoding='utf-8') as data:
                print(f"{OK} {itemean} wird zukünftig ignoriert.")
                data.write(str(itemean) + '\n')
