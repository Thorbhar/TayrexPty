from flask import Flask, request, render_template, send_file, session
import pandas as pd
import csv
import json
import math

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'your_secret_key'


@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Read CSV files
    session['download_allowed'] = True
    file = request.files['file']
    file2 = request.files['file2']

    file.save('/tmp/tayrex.csv')
    file2.save('/tmp/anz.csv')

    df1 = pd.read_csv('/tmp/tayrex.csv')

    df1.rename(columns={'TRANSACTION ID': 'transref'}, inplace=True)
    df1.rename(columns={'REMITTER': 'user'}, inplace=True)
    df1.rename(columns={'SENDING AMOUNT': 'amount'}, inplace=True)

    df1.to_csv('/tmp/tayrex.csv')

    df1['amount'] = df1['amount'].apply(math.floor)

    df1['user'] = df1['user'].str.upper()
    df1['user'] = df1['user'] + ' ' + df1['transref']

    with open('/tmp/anz.csv', mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)
    # Insert a new row at the top
    header_row = ['Date', 'amount', 'user']  # Replace with your header values
    rows.insert(0, header_row)

    # Write the modified rows back to the CSV file
    with open('/tmp/anz.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    df2 = pd.read_csv('/tmp/anz.csv')
    df2['user'] = df2['user'].str.upper()
    df2['amount'] = df2['amount'].apply(math.floor)


    # Define function to check if two names intersect
    def check_names_intersect(name1, name2):
        count = 0
        for n1 in name1.split(' '):
            for n2 in name2.split(' '):
                if n1 == n2:
                    count += 1
                    if count >= 2:
                        return True
        return False

    # create a hash table for df1  with amount as key and the value should be a tuple of (name, index)

    def create_hash_table(df):
        hash_table = {}
        for index, row in df.iterrows():
            if row['amount'] in hash_table:
                hash_table[row['amount']].append((row['user'], index))
            else:
                hash_table[row['amount']] = [(row['user'], index)]
        return hash_table

    df1_amount_hash_table = create_hash_table(df1)

    # iterate over df2 and check if the amount is present in the hash table
    # if present, check if the names intersect
    # if names intersect, print the name and amount and drop the row from both the dataframes

    for index2, row in df2.iterrows():
        if row['amount'] in df1_amount_hash_table:
            for i, (name, index1) in enumerate(df1_amount_hash_table[row['amount']]):
                if check_names_intersect(name, row['user']):
                    print(name, row['amount'])
                    try:
                        df1 = df1.drop(index1)
                        df2 = df2.drop(index2)
                        del df1_amount_hash_table[row['amount']][i]
                        if len(df1_amount_hash_table[row['amount']]) == 0:
                            del df1_amount_hash_table[row['amount']]
                    except KeyError:
                        print("Key not found")
                    break

    # Write result to CSV
    df1.to_csv('/tmp/result.csv', index=False)
    print(df1)

    return render_template('index2.html')


@app.route('/download', methods=['POST'])
def download_file():
    if 'download_allowed' not in session or not session['download_allowed']:
        return "Access denied: No File available for download"  # return an error message if download not allowed
    else:
        path = '/tmp/result.csv'  # Replace with the path to your file
        session['download_allowed'] = False  # reset session variable to disallow further downloads
        return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run()
