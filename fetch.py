from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

db_credentials = {
    'username': 'admin',
    'password': 'Jayesh123',
    'host': 'cardstatus.cpee4kui2bz9.eu-north-1.rds.amazonaws.com',
    'port': '3306',
    'database': 'Adi'
}

# Replace 'card' with your actual table name
table_name = 'Card'

# Create a database connection
engine = create_engine(
    f"mysql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        card_number = request.form['card_number']
        contact_number = request.form['contact_number']

        try:
            # Example query based on Card Number and Contact Number, sorted by Last_Update in decreasing order
            query = f"SELECT * FROM {table_name} WHERE `Card_Id` = %s OR `Contact_Number` = %s ORDER BY `Last_Update` DESC"

            # Execute the query with parameters and fetch the results into a DataFrame
            result_df = pd.read_sql_query(query, engine, params=(card_number, contact_number))

            # Check if any results are found
            if not result_df.empty:
                # Pass the results to the HTML template
                return render_template('search.html', result_df=result_df)
            else:
                # Provide a message if no results are found
                no_results_message = "No results found for the provided Card Number or Contact Number."
                return render_template('search.html', result_df=None, no_results_message=no_results_message)

        except Exception as e:
            # Handle the exception, either redirect to an error page or display a message
            error_message = f"An error occurred: {str(e)}"
            return render_template('error.html', error_message=error_message)

    return render_template('search.html', result_df=None)




if __name__ == '__main__':
    app.run(debug=True)
