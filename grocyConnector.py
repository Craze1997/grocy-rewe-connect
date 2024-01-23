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

def addProductToStock(itemEAN: int, amount: int, price, locationID: int):
    """Add a Product to GROCY INSTANCE via EAN"""

    with open(IGNORE_FILE, 'r') as data:
        for EAN in data:
            try:
                if itemEAN == int(EAN.strip()):
                    return 0
            except:
                print(f"{ERROR} Konnte aktuelle EAN nicht mit der Ignore-Liste vergleichen")
                
    print(f"Suche nach '{itemEAN}' in der Datenbank..")
    try:
        productByBarcode = requests.get(ENDPOINT_GET_BYBARCODE + str(itemEAN), headers=GROCY_HEADER, timeout=10, verify=False).json()
        print(f"{OK} Artikel gefunden: {productByBarcode['product']['name']}")
        product = {
            "amount": amount,
            "transaction_type": "purchase",
            "price": price
        }
        addToStock = requests.post(ENDPOINT_GET_BYBARCODE + str(itemEAN) + "/add", json=product, headers=GROCY_HEADER, timeout=10, verify=False)
        if addToStock.status_code == 200:
            print(f"{OK} {amount}x {productByBarcode['product']['name']} wurde dem Bestand hinzugefügt. Stückpreis: {price}€")
        else:
            print(f"{ERROR} {itemEAN} konnte nicht hinzugefügt werden... :( Bitte prüfe den Bestand in Grocy zu diesem Produkt.")
    except:
        print(f"{WARN} Es wurde kein Produkt mit der EAN {itemEAN} gefunden. Möchtest du ein Produkt anlegen oder die EAN einem Produkt zuweisen?")
        naProduct = None
        while naProduct is None:
            try:
                print("(1) Neues Produkt erstellen\n(2) EAN einem bestehenden Produkt hinzufügen\n(8) Einmal überspringen\n(9) Immer überspringen\n(0) Beenden")
                naProduct = int(input())
            except:
                print(f"{ERROR} Bitte nutze eine der angegebenen Optionen, tippe dafür einfach die Zahl.")
        if naProduct == 0:
            exit(0)
        if naProduct == 8:
            return 0
        elif naProduct == 1:
            print("Starte Dialog für: PRODUKT ANLEGEN\n\n\n")
            print("Name des Produkts: ")
            productName = input()
            print("\nMengeneinheiten: (2) Stück, (3) Packung, (4) Flasche\nMengeneinheit: ")
            productQU = input()
            productInfo = {
                "name": productName,
                "shopping_location_id": locationID,
                "location_id": "2",
                "qu_id_purchase": productQU,
                "qu_id_stock": productQU
            }
            try:
                print(productInfo)
                createProduct = requests.post(ENDPOINT_ADD_PRODUCT, headers=GROCY_HEADER, timeout=10, json=productInfo, verify=False)
                print(f"{createProduct}\n{createProduct.content}")
                productID = createProduct.json()
                productID = productID['created_object_id']
                print(productID)
                if createProduct.status_code == 200:
                    print(f"{OK} Produkt {productName} wurde angelegt. ID des Produkts: {productID}\nFüge EAN hinzu...")
                    newEAN = {
                        "barcode": itemEAN,
                        "amount": 1,
                        "shopping_location_id": locationID
                    }
                    postReq = requests.post(ENDPOINT_ADD_BARCODE_BY_ID, headers=GROCY_HEADER, json=newEAN, timeout=10, verify=False)
                    if postReq.status_code == 200:
                        print(f"{OK} EAN wurde dem Produkt hinzugefügt. Dialog wird neugestartet.")
                    else:
                        print(f"{ERROR} EAN konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                else:
                    print(f"{ERROR} Antwort von Grocy war != 200, bitte prüfen. Dialog wird Pausiert, ENTER zum fortfahren...")
                    input()
            except:
                print(f"{ERROR} Fehler beim Anlegen des Produktes. Dialog wird neugestartet.")
            addProductToStock(itemEAN, amount, price, locationID)
        elif naProduct == 2:
            productID = None
            print("Bitte schaue in GROCY nach dem gewünschten Produkt und kopiere die ID aus der URL und gebe sie hier ein: ")
            while productID is None:
                try:
                    productID = int(input())
                    try:
                        findProductByID = requests.get(ENDPOINT_GET_BYID + str(productID), headers=GROCY_HEADER, timeout=10, verify=False).json()
                        findProductByID_data = findProductByID[0]
                        print(f"{OK} Produkt gefunden: {findProductByID_data['name']} ... EAN wird hinterlegt..")
                        try:
                            newEAN = {
                                "barcode": itemEAN,
                                "product_id": findProductByID_data['id'],
                                "amount": 1,
                                "shopping_location_id": locationID
                            }
                            postReq = requests.post(ENDPOINT_ADD_BARCODE_BY_ID, headers=GROCY_HEADER, json=newEAN, timeout=10, verify=False)
                            if postReq.status_code == 200:
                                print(f"{OK} EAN wurde dem Produkt hinzugefügt. Dialog wird neugestartet.")
                            else:
                                print(f"{ERROR} EAN konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                        except:
                            print(f"{ERROR} EAN konnte dem Produkt nicht hinzugefügt werden. Dialog wird neugestartet.")
                        addProductToStock(itemEAN, amount, price, locationID)
                    except:
                        productID = None
                        raise Exception from Exception
                except:
                    print(f"{ERROR} Produkt nicht gefunden, versuche es noch einmal.")
        elif naProduct == 9:
            with open(IGNORE_FILE, 'a') as data:
                print(f"{OK} {itemEAN} wird zukünftig ignoriert.")
                data.write(str(itemEAN) + '\n')