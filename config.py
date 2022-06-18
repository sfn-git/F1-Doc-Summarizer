# Python program to read
# json file
  
  
import json
  
# Opening JSON file
f = open('config.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Closing file
f.close()