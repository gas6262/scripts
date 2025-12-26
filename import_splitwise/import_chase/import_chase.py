from splitwise.expense import Expense
from splitwise.user import ExpenseUser
from splitwise import Splitwise
import os
import json
import optparse
import requests
import os
import glob
import csv
from typing import List, Dict
from datetime import datetime
import json

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DATE_TIME_COLS = ["transaction_date", "post_date"]
AMOUNT_COLS = ["amount", "balance"]

def parse_date(date_str: str) -> datetime:
    """
    Try to parse a date string using common formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If date cannot be parsed with any known format
    """
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_str}")

def normalize_row(row: Dict[str, str], filename: str) -> Dict[str, any]:
    """
    Normalize a CSV row: lowercase column names, replace spaces with underscores,
    convert date columns to datetime objects, and add source file info.
    
    Args:
        row: Raw CSV row from DictReader
        filename: Name of the source CSV file
        
    Returns:
        Normalized row dictionary
    """
    # Normalize column names: lowercase and replace spaces with underscores
    normalized_row = {
        key.strip().replace(" ", "_").lower(): value
        for key, value in row.items()
    }
    normalized_row["_source_file"] = filename
    
    # Convert date/time columns to datetime
    for col in DATE_TIME_COLS:
        if col in normalized_row and normalized_row[col]:
            try:
                normalized_row[col] = parse_date(normalized_row[col])
            except ValueError:
                pass  # Keep original value if conversion fails

    for col in AMOUNT_COLS:
        if col in normalized_row and normalized_row[col]:
            try:
                normalized_row[col] = - float(normalized_row[col].replace(',', '').replace('$', ''))
            except ValueError:
                pass  # Keep original value if conversion fails
    
    return normalized_row

def read_expenses(folder: str) -> List[Dict[str, str]]:
    """
    Iterate through all CSV files in the given folder and return a list of rows.
    The `folder` parameter may be an absolute path or a path relative to this script.
    Each row is returned as a dict (csv.DictReader). A special key '_source_file'
    is added containing the CSV filename where the row came from.

    Raises FileNotFoundError if the folder does not exist.
    """
    # Expand ~ and environment vars
    folder = os.path.expanduser(os.path.expandvars(folder))

    # If path is not absolute, interpret it as relative to this script's directory
    if not os.path.isabs(folder):
        folder = os.path.join(THIS_FILE_DIR, folder)

    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    pattern_csv = os.path.join(folder, "*.csv")
    pattern_CSV = os.path.join(folder, "*.CSV")
    
    files = sorted(glob.glob(pattern_csv) + glob.glob(pattern_CSV))
    expenses: List[Dict[str, str]] = []

    for file_path in files:
        # Open with utf-8 and fallback to latin-1 if needed
        try_encodings = ("utf-8", "latin-1")
        for enc in try_encodings:
            try:
                with open(file_path, newline="", encoding=enc) as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        normalized_row = normalize_row(row, os.path.basename(file_path))
                        expenses.append(normalized_row)
                break
            except UnicodeDecodeError:
                # try next encoding
                print(f"Warning: Could not decode {file_path} with {enc}, trying next encoding.")
                continue

    return expenses

def get_bearer_token() -> str:
    """
    Obtain a bearer token using the OAuth2 authorization-code flow.
    This is a placeholder function and should be implemented as needed.
    
    Returns:
        Bearer token string
    """
    token_path = os.path.join(THIS_FILE_DIR, "token.json")
    
    if not os.path.isfile(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}")
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    return token_data.get("access_token")


def send_expenses(expenses, group = 88149298, users = [6284544, 41626223]) -> None:
    """
    Send the given expense to Splitwise using the Splitwise API.
    
    Args:
        expense: Expense object to send
    """
    
    with open(os.path.join(THIS_FILE_DIR, 'consumer_oauth.json'), 'r') as f:
        conf = json.load(f)

    with open(os.path.join(THIS_FILE_DIR, 'token.json'), 'r') as f:
        token_json = json.load(f)

    sObj = Splitwise(conf["consumer_key"],conf["consumer_secret"])

    sObj.setOAuth2AccessToken(token_json)

    for exp in expenses:
        expense = Expense()
        expense.setGroupId(f"{group}")
        expense.setCost(exp['amount'])
        expense.setDescription(exp['description'] + " " + exp['transaction_date'].strftime('%m/%d'))
        expense.setCurrencyCode('USD')
        expense.setSplitEqually(True)

        expense_users = []
        val = exp['amount']
        for i, user in enumerate(users):
            user2 = ExpenseUser()
            user2.setId(user)
            user2.setOwedShare(val if i == 0 else '0.00')
            expense_users.append(user2)

        # expense.setUsers(expense_users)

        expense, errors = sObj.createExpense(expense)

        if errors:
            print("Errors occurred while creating expense:")
            print(errors)


def main(folder) -> None:
    """
    Main function to process expenses from CSV files.
    
    Args:
        folder: Path to folder containing CSV files (default: "in_12_24")
    """
    expenses = read_expenses(folder)

    if not expenses:
        print("No expenses found.")
        return
    
    send_expenses(expenses)


if __name__ == "__main__":
    
    usage = "import_chase.py -f [folder]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f", "--folder", default="in_12_24", dest="folder", help="Folder containing CSV files (default: in_12_24)" )
    
    options, args = parser.parse_args()
    
    # Use positional arg if provided, otherwise use option/default
    folder = args[0] if args else options.folder
    main(folder)