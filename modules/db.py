from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
my_email = "nicdelhi2024@gmail.com"
code = "zuff vkvx pamt kdor"
uri = "mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client['HMS']
patients_collection = db['patients']
doctors_collection = db['doctors']
users_collection = db['users']
admin_collection = db['admin']
appointment_collection = db['appointment']
contact_collection = db['contact']
superadmin_collection = db['Superadmin']
hospital_data_collection = db['hospital_data']
hospital_discharge_collection = db['discharged']
inventory_collection = db['inventory']
stock_collection = db['stock']

today_date = datetime.today().strftime('%Y-%m-%d')
# Query to find documents where the date is less than today
query = {'appointment_date': {'$lt': today_date}}

# Delete the matching documents
result = appointment_collection.delete_many(query)

print(f"Deleted {result.deleted_count} appointments.")