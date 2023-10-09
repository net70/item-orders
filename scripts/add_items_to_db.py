import uuid
import random
import pymongo

# MongoDB connection settings
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["transactions"]["items"]

# Random Items to add to DB (generated with chatGPT)
items = {
    "Sparkling Water": "Refreshing carbonated water for instant hydration.",
    "Bluetooth Earbuds": "Wireless earphones for music and calls on the go.",
    "Laptop Backpack": "Stylish and spacious backpack for your laptop and essentials.",
    "Coffee Maker": "Brew your favorite coffee at home effortlessly.",
    "Yoga Mat": "Non-slip yoga mat for a comfortable workout.",
    "Wireless Mouse": "Ergonomic wireless mouse for smooth navigation.",
    "LED Desk Lamp": "Adjustable LED lamp for productive work or reading.",
    "Portable Charger": "Charge your devices anytime, anywhere.",
    "Running Shoes": "High-performance running shoes for active lifestyles.",
    "Stainless Steel Water Bottle": "Durable, eco-friendly water bottle to stay hydrated.",
    "Wireless Keyboard": "Compact wireless keyboard for efficient typing.",
    "Fitness Tracker": "Track your health and fitness goals with this smart device.",
    "Noise-Canceling Headphones": "Enjoy immersive audio without distractions.",
    "Blender": "Blend smoothies and shakes with this powerful appliance.",
    "Camping Tent": "Spacious tent for outdoor adventures and camping trips.",
    "Digital Camera": "Capture memories with high-quality digital photography.",
    "Electric Toothbrush": "Achieve a fresh, clean smile with an electric toothbrush.",
    "Garden Hose": "Durable garden hose for watering plants and lawns.",
    "Wireless Speaker": "Portable wireless speaker for music on the move.",
    "Cooking Pan Set": "Non-stick cooking pans for delicious meals.",
    "E-book Reader": "Access your favorite books and novels in digital format.",
    "Hiking Backpack": "Comfortable backpack for long hikes and treks.",
    "Smartwatch": "Stay connected and track your fitness with a smartwatch.",
    "Resistance Bands": "Versatile resistance bands for effective workouts.",
    "Drone": "Capture stunning aerial photos and videos with this drone.",
    "Bluetooth Speaker": "High-quality Bluetooth speaker for enhanced audio.",
    "Espresso Machine": "Brew delicious espresso at home like a barista.",
    "Gaming Mouse": "Precision gaming mouse for competitive gaming.",
    "Projector": "Enjoy movies and presentations on a big screen.",
    "Gaming Chair": "Ergonomic gaming chair for extended gaming sessions."
}


# Function to generate a random item
def generate_random_item(name, description):
    return {
        "item_id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "price": round(random.uniform(10.0, 1_000.0), 2),
        "num_in_stock": random.randint(1_000, 10_000),
    }

# Number of unique items to add
num_items_to_add = len(items)

# Create and insert unique items into the db
for name, description in items.items():
    unique_item = generate_random_item(name, description)
    # Ensure uniqueness of the item by using the "id" field
    if not db.find_one({"name": unique_item["name"]}):
        db.insert_one(unique_item)
        print(f"Added item: {unique_item['name']}")

print("Items added successfully.")

# Close the MongoDB client connection
mongo_client.close()
