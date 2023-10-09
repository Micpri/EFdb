#!/bin/python
# Generate test data for mongodb
from mongoCRUDservice import MongoCRUD
from helpFunctions import *



#### Initialise client
MCRUD = MongoCRUD()
#### TEST CREATE DATABASE
print("#### TEST CREATE DATABASE")
MCRUD.DeleteDatabase("EFdb")
database = MCRUD.CreateDatabase("EFdb")
print(" ")


# TEST CREATE COLLECTIONS
MCRUD.CreateCollection(database, "Mode_of_Transport.Road.PC")
MCRUD.CreateCollection(database, "Mode_of_Transport.Road.Motorcycle")
MCRUD.CreateCollection(database, "Mode_of_Transport.Road.HDV")
MCRUD.CreateCollection(database, "Mode_of_Transport.Road.Bus")
MCRUD.CreateCollection(database, "Mode_of_Transport.Road.Pipeline")
MCRUD.CreateCollection(database, "Mode_of_Transport.Rail")
MCRUD.CreateCollection(database, "Mode_of_Transport.Sea")
MCRUD.CreateCollection(database, "Mode_of_Transport.Air")
MCRUD.CreateCollection(database, "Energy_Carriers")
MCRUD.CreateCollection(database, "Logisitc_Service")
MCRUD.CreateCollection(database, "Travel_Service")


# TEST READ COLLECTION
print(database.list_collection_names())
print(MCRUD.Read(database, "Mode_of_Transport.Road.Pipeline"))
print(" ")


# TEST CREATE ENTRY
print("#### TEST CREATE ENTRY")
entry =  {
#        "Fordonskategori": "Heavy goods vehicle",
        "Subkategori" : "Tung lastbil utan släp",
        "HBEFA namn": "RT <=7.5t Euro-VI D-E",
#        "IVL namn (med maximala bruttovikter)" : "Lastbil utan släp <=7.5t",
        "Bränsle" : "Diesel",
 #       "Emissionsstandard": "Euro VI D-E",
#        "Trafiksituation" : "Rural (excl. motorway)",
#        "Load % " : 0,
        "Representativt för år": 2021,
#        "Bränsleförbrukning (MJ/km)" : 4.552099705,
#        "BC (exhaust) (g/km)" : 0.000185188,
#        "CH4 (g/km)" : 0.000272984,
#        "CO (g/km)" : 0.05329882,
#        "HC (g/km)" : 0.011374321,
#        "N2O (g/km)" : 0.016412197,
#        "NH3 (g/km)" : 0.007252378,
#        "NMHC (g/km)" : 0.011101337,
        "NO2 (g/km)" : 0.01,
        "NOx (g/km)	" : 0.02,
        "PM2.5 (exhaust) (g/km)": 0.03,
        "PN (exhaust) (g/km)" : 0.004
#        "IVL Processed?" : "Extracted (Klimatrapportering 2022)",
#        "Sources" : "HBEFA 4.2",
#        "FileName" : "",
#        "Pointer" : "",
#        "Comment" :	"Emissionsfaktorer som användes vid beräkningarna till klimatrapporteringen sommaren 2022 (submission 2023)."
}

MCRUD.CreateEntry(database.Mode_of_Transport.Road.Pipeline, entry)
ans = MCRUD.Read(database, "Mode_of_Transport.Road.Pipeline")
id = ans[0]["_id"]
print(id, type(id))


# TEST READ ENTRY
print("#### TEST READ ENTRY")
ans2 = MCRUD.Read(database, "Mode_of_Transport.Road.Pipeline", {"_id" : id})
pprint(ans2)


# TEST UPDATE ENTRY
print("#### TEST UPDATE ENTRY")
msg_UpdateEntry = MCRUD.UpdateEntry(
    database.Mode_of_Transport.Road.Pipeline, 
    {"_id":id}, 
    updates = {
            "FileName" : "THIS IS THE NEW FILE NAME",
            "NEW FIELD" : "THIS IS A NEW FIELD"
        }
)
print(msg_UpdateEntry)
pprint(MCRUD.Read(database, "Mode_of_Transport.Road.Pipeline"))



# TEST CREATE ENTRIES - same as create/insert many
print("#### TEST CREATE ENTRIES")
n_entries = 100

def genr():
    jp_cars = ["Toyota", "Nissan", "Honda", "Suzuki", "Mazda", "Daihatsu", "Subaru", "Mitsubishi"]
    files = ["test_txt.txt", "test_txt2.txt","test_pdf.pdf", "", "test_pptx.pptx","test_xlsx.xlsx","test_doc.docx","ivl_logo.svg", ["test_pptx.pptx","test_xlsx.xlsx"], ["test_txt.txt", "test_txt2.txt"]]
    links = ["https://bbc.com", "https://www.svt.se", "https://ivl.se", ["https://bbc.com","https://svt.se"]]
    years = np.arange(1989, 2045, 3)

    returner = [{
        "Name": str(random.choice(jp_cars)),
        "Record1": str(random.random()),
        "Record2": str(random.randint(0,1e3)),
        "Document" : str(random.choice(files)),
        "Valid Until" : str(random.choice(years)),
    }, {
        "Name": str(random.choice(jp_cars)),
        "Record1": str(random.random()),
        "Link" : str(random.choice(links)),
        "Document" : str(random.choice(files)),
        "Valid Until" : str(random.choice(years))
    }]

    # choose random of two configs (one without Record2)
    ans = 1#random.randrange(2)
    return returner[ans]


pprint(MCRUD.Read(database, "Mode_of_Transport.Road.Motorcycle"))
MCRUD.CreateEntries(database.Mode_of_Transport.Road.Bus, [genr() for entry in range(3)])
MCRUD.CreateEntries(database.Mode_of_Transport.Road.HDV, [genr() for entry in range(n_entries)])
MCRUD.CreateEntries(database.Mode_of_Transport.Road.Motorcycle, [genr() for entry in range(n_entries)])
MCRUD.CreateEntries(database.Mode_of_Transport.Road.PC, [genr() for entry in range(n_entries)])
pprint(MCRUD.Read(database, "Mode_of_Transport.Road.Bus"))