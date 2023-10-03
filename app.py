from flask import Flask, jsonify, request
# from pymongo import MongoClient
# from flask_cors import CORS
import csv
import random

# cors = CORS()

def create_app():
	app = Flask(__name__)
	# cors.init_app(app)
	return app


# client = MongoClient('localhost', 27017)
# db = client.test
# insurance_members = db.insurance_members

app = create_app()
FILE_PATH = './sample-rates.csv'

@app.route("/")
def init():
      return 'Server Running'

@app.route("/get-loading-params")
def getOnLoad():
      client_type = [
            { 'label': 'Adult', 'min': 0, 'max': 2, 'value': 'adult' },
            { 'label': 'Child', 'min': 0, 'max': 4, 'value': 'child' }
            ]
      city_type = [
            { 'label': 'Tier 1', 'value': 'tier-1' }
      ]
      tenure_type = [
            { 'label': "500000", 'value': 500000 },
            { 'label': "700000", 'value': 700000 },
            { 'label': "1000000", 'value': 1000000 },
            { 'label': "1500000", 'value': 1500000 },
            { 'label': "2000000", 'value': 2000000 },
            { 'label': "2500000", 'value': 2500000 },
            { 'label': "3000000", 'value': 3000000 },
            { 'label': "4000000", 'value': 4000000 },
            { 'label': "5000000", 'value': 5000000 },
            { 'label': "6000000", 'value': 6000000 },
            { 'label': "7500000", 'value': 7500000 },
      ]
      age_category = []
      for age in range(18, 100):
            age_category.append({ 'value': age, 'label': str(age) })
      year_category = []
      for year in range(1,3):
            year_category.append({ 'label': str(year)+'yr', 'value': year })
      return jsonify({ 'year_category': year_category, 'client_type': client_type, 'city_type': city_type, 'tenure_type': tenure_type, 'age_category': age_category })

def ageRangeMatcher(range, age):
      [lower, upper] = range.split('-')
      if int(lower) <= int(age) and int(age) <= int(upper):
            return True
      return False
def findDiscount(member_csv, maximum_member, client):
      if member_csv == '1a':
            return 0
      if maximum_member['label'] == client['label']:
            return 0
      return 50

@app.route("/get-plan", methods=['POST'])
def getPlans():
      content_type = request.headers.get('Content-Type')
      if (content_type == 'application/json'):
            json = request.get_json()
      else:
            return 'invalid request'
      tier = request.get_json().get('city')
      tenure = request.get_json().get('tenure')
      year = request.get_json().get('year')
      year = int(year)
      adult_count = 0
      child_count = 0
      clients = request.get_json().get('clients')
      for client in clients:
            if client['type'] == 'adult':
                  adult_count += 1
            elif client['type'] == 'child':
                  child_count += 1
      if not adult_count:
            return 'no valid plan exists.'
      
      member_csv = str(adult_count)+'a'
      if child_count:
            member_csv += ',' + str(child_count) + 'c'

      plan_details = []
      with open(FILE_PATH) as file:
            csv_file = csv.reader(file)
            member_csv_index = 0
            age_range_index = 0
            tier_index = 0
            tenure_index = 0
            for row in csv_file:
                  for colIndex in range(len(row)):
                        col = row[colIndex]
                        if col == 'member_csv':
                              member_csv_index = colIndex
                        elif col == 'age_range':
                              age_range_index = colIndex
                        elif col == 'tier':
                              tier_index = colIndex
                        elif col == tenure:
                              tenure_index = colIndex
                  break
            maximum_member = clients[0]
            maxim = 0
            for client in clients:
                  if int(client['age']) > maxim:
                        maxim = client['age']
                        maximum_member = client

            for client in clients:
                  client = client
                  for row in csv_file:
                        if not len(row):
                              break
                        if row[member_csv_index] == member_csv and row[tier_index] == tier and ageRangeMatcher(row[age_range_index], client['age']):
                              floated_discount = findDiscount(member_csv, maximum_member, client)
                              discounted_percentage = 1
                              base_rate = round(float(row[tenure_index])/year, 2)
                              if floated_discount:
                                    discounted_percentage = int(floated_discount or 1)*0.01
                              discounted_percentage = round(discounted_percentage*float(row[tenure_index])/int(year), 2)
                              plan_details.append({
                                    'age_range': row[age_range_index], 'age': client['age'], 'label': client['label'],
                                    'base-rate': base_rate, 'floater-discount': floated_discount,
                                    'value': client['type'],
                                    'discounted-rate': discounted_percentage,
                              })
                              file.seek(0)
                              break
      return plan_details

# @app.route("/checkout", methods=['POST'])
# def saveToDB():
#       content_type = request.headers.get('Content-Type')
#       if (content_type == 'application/json'):
#             json = request.get_json()
#       else:
#             return 'invalid request'
#       tier = request.get_json().get('city')
#       tenure_amount = request.get_json().get('tenure_amount')
#       year = request.get_json().get('year')
#       clients = request.get_json().get('clients')
#       policy_number = 'POL' + str(random.randrange(10000, 500000))
#       for i in range(len(clients)):
#             client = clients[i]
#             client['member_number'] = 'MEMB' + str(policy_number) + str(i+1)
#       record = insurance_members.insert_one({ 'tier': tier, 'tenure_amount': tenure_amount, 'year': year, 'clients': clients, 'policy_number': policy_number })


      return { 'tier': tier, 'tenure_amount': tenure_amount, 'year': year, 'clients': clients, 'policy_number': policy_number }



if __name__ == "__main__":
    app.run(debug=True)