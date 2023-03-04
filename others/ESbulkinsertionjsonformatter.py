import json

# Load the JSON file
with open('restaurants-data.json', 'r') as file:
    data = json.load(file)

# Convert the data to NDJSON format
ndjson = ''
for item in data:
    ndjson += json.dumps({"index": {}}) + '\n' + json.dumps(item) + '\n'

# Save the NDJSON data to a file
with open('restaurants-data.ndjson', 'w') as file:
    file.write(ndjson)