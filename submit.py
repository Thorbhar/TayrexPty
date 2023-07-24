from flask import Flask, request, render_template, send_file, session
import pandas as pd
import csv
import json
import math

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'your_secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    session['download_allowed'] = True
    file = request.files['file']
    file2 = request.files['file2']
    file3 = request.files['file3']
    file.save('/Users/toba/Desktop/TayrexPty/uploads/Child.csv')
    file2.save('/Users/toba/Desktop/TayrexPty/uploads/ANZ.csv')
    file3.save('/Users/toba/Desktop/TayrexPty/uploads/poli.csv')

    df = pd.read_csv('/Users/toba/Desktop/TayrexPty/uploads/Child.csv')

    df3 = pd.read_csv('/Users/toba/Desktop/TayrexPty/uploads/poli.csv')

    df.rename(columns={'TRANSACTION ID': 'Trans ref'}, inplace=True)
    df.rename(columns={'REMITTER': 'User'}, inplace=True)
    df.rename(columns={'SENDING AMOUNT': 'Amount'}, inplace=True)
    df3.rename(columns={'Merchant Reference': 'User'}, inplace=True)

    df.to_csv('/Users/toba/Desktop/TayrexPty/uploads/Child.csv')
    df3.to_csv('/Users/toba/Desktop/TayrexPty/uploads/poli.csv')

    with open('/Users/toba/Desktop/TayrexPty/uploads/ANZ.csv', mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Insert a new row at the top
    header_row = ['Date', 'Amount', 'User']  # Replace with your header values
    rows.insert(0, header_row)

    # Write the modified rows back to the CSV file
    with open('/Users/toba/Desktop/TayrexPty/uploads/ANZ.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    child_transactions = []
    with open('/Users/toba/Desktop/TayrexPty/uploads/ANZ.csv', mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            child_transactions.append(row)

    print(len(child_transactions))

    parent_transactions = []
    with open('/Users/toba/Desktop/TayrexPty/uploads/Child.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            parent_transactions.append(row)

    print(len(parent_transactions))

    transform_child = {}
    transformed_child_keys = []

    for ind, transaction in enumerate(child_transactions):
        transform_child[f"{transaction['User']} {ind}"] = math.floor(float(transaction['Amount']))

    transformed_child_keys = list(transform_child.keys())

    # print(transformed_child_keys)

    not_present = []

    for transaction in parent_transactions:
        user_name = transaction['User']
        substr_array = user_name.split(' ')
        filtered_child = []
        for substr in substr_array:
            sub_item_array = [key for key in transformed_child_keys if substr.lower() in key.lower()]
            filtered_child.extend(sub_item_array)
        unique_filtered_child = list(set(filtered_child))
        if len(unique_filtered_child) == 0:
            not_present.append(transaction)
        else:
            has_transaction = False
            for child in unique_filtered_child:
                if transform_child[child] == math.floor(float(transaction['Amount'])):
                    has_transaction = True
            if not has_transaction:
                not_present.append(transaction)

    print(len(not_present))

    with open('/Users/toba/Desktop/TayrexPty/output/not-present.json', 'w') as output_file:
        json.dump(not_present, output_file)
        print("Successfully wrote file")

    df = pd.read_json('/Users/toba/Desktop/TayrexPty/output/not-present.json')
    df.to_csv('/Users/toba/Desktop/TayrexPty/output/not-present.csv')

    # Read child transaction CSV file
    with open('/Users/toba/Desktop/TayrexPty/uploads/poli.csv', "r") as f:
        childTransactions = [row for row in csv.DictReader(f)]
    childSet = set(item["User"] for item in childTransactions)

    # Read parent transaction CSV file
    with open('/Users/toba/Desktop/TayrexPty/output/not-present.csv', "r") as f:
        parentTransactions = [row for row in csv.DictReader(f)]
    notPresent = []

    for element in parentTransactions:
        if element["Trans ref"] not in childSet:
            notPresent.append(element)

    print(len(notPresent))

    # Write not present transactions to JSON file
    with open('/Users/toba/Desktop/TayrexPty/output/.not-present.json', "w") as f:
        json.dump(notPresent, f)

    df = pd.read_json('/Users/toba/Desktop/TayrexPty/output/.not-present.json')
    df.to_csv('/Users/toba/Desktop/TayrexPty/output/Not_present.csv')

    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_file():
    if 'download_allowed' not in session or not session['download_allowed']:
        return "Access denied"  # return an error message if download not allowed
    else:
        path = '/Users/toba/Desktop/TayrexPty/output/Not_present.csv'  # Replace with the path to your file
        session['download_allowed'] = False  # reset session variable to disallow further downloads
        return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run()
