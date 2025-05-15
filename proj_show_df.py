import pandas as pd

# Path to your CSV file
csv_file = 'trustpilot_reviews.csv'

# Read the CSV into a DataFrame
try:
    df = pd.read_csv(csv_file)

    # Display the first few rows
    print("DataFrame loaded successfully. Here's a preview:")
    print(df.head(-5))  # You can also use df.to_string() to see the full table

except FileNotFoundError:
    print(f"File '{csv_file}' not found.")
except pd.errors.EmptyDataError:
    print(f"The file '{csv_file}' is empty.")
except Exception as e:
    print(f"An error occurred: {e}")
