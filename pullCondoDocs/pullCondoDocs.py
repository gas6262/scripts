#!/usr/bin/env python3
"""
Document downloader script for BuildingLink files.
Reads document IDs from docs.yaml and downloads files using the provided URL pattern.
"""

import yaml
import requests
import os
from pathlib import Path
import time
from urllib.parse import unquote
import re
from datetime import datetime
import zipfile

# Configuration
BASE_URL = "https://venetiaresidents.buildinglink.com/V2/Tenant/Library/getFile.aspx"
DOCS_FILE = "docs.yaml"
DOWNLOAD_DIR = Path(__file__).parent / "downloads"

# Set your cookie value here - replace with your actual cookie
COOKIE_VALUE = "HostGUID=555243ac-5e68-41db-8dda-e9b690f36ccc; UserHasLoggedIn=True; UserLoggedInDate=2025-03-12T03:35:41; GTMFacId=10559; _ga=GA1.2.999437332.1741808149; _hjSessionUser_2825293=eyJpZCI6IjczYmY2YThmLWY3NzktNTdjNy1hMjZlLTUzOWJkOGYwZjAzNSIsImNyZWF0ZWQiOjE3NDE4MDgxNDkzMzksImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_2825293=eyJpZCI6IjczYmY2YThmLWY3NzktNTdjNy1hMjZlLTUzOWJkOGYwZjAzNSIsImNyZWF0ZWQiOjE3NDE4MDgxNDkzMzksImV4aXN0aW5nIjp0cnVlfQ==; __cflb=02DiuDXvJ1dKekvY3osgZyhzd7gY2ApvA9itqc1aB8bBa; bl.auth.cookie.oidc=chunks:2; betaflags=76|79|81|83|86|87|88|89|95|103|107|109|110|114|115|116|118|121|1069|1073|1079|119|113|1083|1084|1022|1056|106|1009|1010|1021|1013|1023|1025|1032|1030|1039|1040|1041|1064; ASP.NET_SessionId=h0zaldxoahjvajtxpapsfskq; BuildingSession=h0zaldxoahjvajtxpapsfskq10559; UserSelectedCulture=en-us; _gid=GA1.2.1755320789.1755251933; _ga_GZ6JZLD50L=GS2.2.s1755290852$o23$g1$t1755291146$j60$l0$h0; _ga_1PVTZ2M882=GS2.2.s1755290852$o23$g1$t1755291146$j60$l0$h0; bl.auth.cookie.oidcC1=UCOzlBrQTegiJ3uQSYgxrRrjiTlJj1WJ6mY1rj1cklTUBGNcGVku3gYihdu20h-l1tq9ILJydEHQ01CVha5x7jsUf-df8hTMtKcDw0oU9preHDL95JbNP9TSYi7p1NnRoUga8UkpApQRdlq6ALmZAa9HJogFgtf16i9xZBSVc2YrAbjgUtNmp7pcX652-Mok3qhxGEl9bvi6c10_MFMVQAJTJkZ9G-x3w-amBl0I-iYCK7nvokuwRdDhcQ7Auh38WOPd-HKSexZr_TYFDzBTb6UUa_D_bFx22n78oxssuolJtWaTk04pMfl_B34xfwG0qEMFfuUY_jZXsS7wbRjwHBFyCDKnch7AC9Z9resorD00FFN-GOM_fL9jD6uaBBYh1UHcpg00HvLA3xo1X_Bxy216pg7HII2PSZRGriMEBqAI46SAygmrIk-6Tuk4hawG5SmAxS09irZ9MT_w5ArkPKl1qH_VT10vQu0_XmwUYeQccooFVqUQ5mkgkDdNjckXpQ_KDR4h-VmtcFRK-CazeibI8sXrGr9IENC2rBcvc67njiAdN-la9aoZEb1SBe1ozvCkmmj-y7TTcFa9ESkmn9-VksCJ_Vz6W7dKqfNR-OrkRzWVKFyb6BgRuyK9ZL8FpLUoiyNdvgdm_5x8-HuHzA81kXGAKC73jVuo36AxEMQFhNpPTP236TkFN9R4r6C5Vlz2b57Uk4spjldTdRui_p5YCtuWMB2wjg2cn34Q99gBpoi_P8I4qRYjUahJMtyLFOTYpjU94XH3cIax94SnFWXvXluWYFYFkHNUEFSFdkTGbDh3JrdIEaQ0XhEAbU8BDtSbCOj4U_H5hfxrCvB-OmQLsiidB-cJKYPQyJdy7ZqeHR6UVEqh5rXQ10kONVRA50m-eh-qh-kumqUg75-3bVD_x8hBfcJkX1yCgWX3VVrzYmgcd_WC_syBauXo8bwELq9E150rX6fRustfh3hc4oWCfa2trr_n8L_YIv6UdJDDKe8DG7gCwjNhIgJYnSZqoODqCco7dX9YUmDdVBjpAMvnVQs5mB3PNhXS8548bZpPcZo-mh88KRiFrYuGepe6Cj5L6f25ny_mLcz25kmh7xRrCxIWt2R9V6EVB4yG6zl_94d1VIvleI722phGRwLXphXs04I-z2qE5xNOfcLy1g69VyHMwPtSeeaD99uHxwKHOG3mUr5AEoEGG0OP4PnfFtUuptKNTduprmR7kvYrUniAe5uz3S1Bmp9R-azogrK6R7KzmlhA5TjtqUjzBJzViKP64DF7oMfDc4VrHuKxszG1RSSq7KL5IZvJgjZn9IYHeFwxqnjUN50-o43bT7pawc9SmilrM0oQTD13dTeKE43XsP4iSDH7Fl6mLVfw1G-2Yk17bS8GMx94cjjoagvWO_IldA2GdICnrd9VpzjfzTcqo3ANpCfaWWIy7_F4hWwoL7yyjktv--1n8BQORrUZ6YCJUrTOUBk70KH49uo-3A2vJvIzF1NjIgoCHobT_u_wXndDUfg3HRYAt64hM6A_36oEz98QNSBXoM9_WQFiTmmP1OkaP9F3BTLaW0xepOfXpaGTiFVSBtB4CU2ULLnJzHJBtAzFT4TPJBynan-3wj1NHlvmn0jwGm6k29KPPxSScWq27VSPafK_60uWuFVizF5GP-2IZfKDr_6HELK_LLtb1-Xq2otwt9dvPK3feAYo8YVxY8Ois85792Xl5u9mJgDZbkHhxFL5u-aPGX8DDMbQJyiablvf_SgBEo3Nj1Tvh2rtcObhI5-jPySq8HO-zw92NYNr1pGG8PxLjI6QNcbYYZs0m5HcmUkziKONTKZaZojtuf_jL5JGtxtgiwGWXwEG4jMlSejuJhYH7rI2OPN071XdTJrzw6wpGqn5ekJxKBvjh9qteLKa9UngSrXXb43YJNTzF10DDtf0WaG0dzdkRHm-dCR48CZWn6py6DgEpqlo-OdxfW7vghQhcpqJqtCaX1fPCJ-dH1YV5S-y-x-ba56MYLVr1KU-1CuuKKNMD2QD1wEhLJE1cgKqIf2urE26rr0AytdbUtk7TqIdjLmDS9H6uHXW4VEO23IGHWe_wTFpxlS26ks2LY47l-TDrYJGxbfc2LhyeSNFOFxbhBoFc6cX1dsw7waOI9_rnNxqz8NT--KcbYXRneKImYFdTU4HKCjOdVBsmfcug2RcSjrgsR-1y7P6ZAf8akn_xU0JiqvDZ479RUGVH-uO3KKz8fpAKMMhErO4AkzpP7PucOGUyyL_kkYp7r36J3kHXjEyrfwMdpVQXME9nKC7awmnL3z4aoWf5LEDXqVH1p5xfur1Qx--OHO2Yo_HoJRaZ7nlV-7sH7uTHr_Xkz7auqmn7YjzvVKCD95oTz-dEqkN8EiwICedMEnhu5BSrHgFMpqD50NHYzuSBKqrdtr_NZOggPFgQQv4auEb3_9BZGECZHgBo3EvgD6JCjcVZkbaPhpG5WrQxjeNtvZrJM4494exZAhWQZgUMfuW1s7Zpv3gO-27wrFPDMxtzXP0C0M5jDF3m2e9peLy6WWlpsSwxlJP_lqmHchzlLgx54i4B52kCJHrSrpURKFyEqOnUxR0bJdaf_S2Iteg9h36X4XyUFecBuPlMX0ucDpaUA1109Lam1cYvyNfPVT-yxKVchEfS3IiX7dZ7L04vccr6vpDD0I02dWi5djd1FinBhyva6hXt0NcM6a0Kk7q50XQcNfQYCzT7ogqoeHtn5U0ZNppeZ0ih34btFD2h3eD4wRu5zpB6QH-46_Xdy9C2aUN6SEp9LWb84wo5OxkqCsl4kLEV1vJEPvV7CQENgBD3-ple6a15wkliFUmIzIWraHhits0ELZVzB-fvP0CwzQ3uGZSTNvqpFRrNyOOxZ6biTPDA1riNb0hr6dYPw4nbiM621nKzE8DtNFaOQcGh__5tehKRNtvteBv7RKVmekg-DRkugNUB_VsGNn3AxH2MHjjc1T-wHH8hbRXKIPsJwhfBDM5z_d5jDLfeMo7E2Da1Tg-ETxKr8j2-jfEzl2fTpenYEsm9udn9E0U6lX4QkN3wB9aUU8DKafhv64g021L-Kcwi0GyvhzgX2eO9PMj9RaLVL94EhQrWyrwxOdBw4bI6XNbr1hqTFO7r6UkCLoDIzsNZBVGmIOm_NBV7ok-qmWpy86eJ6JQRnoWASRSrt-vSKeJa97pzS_8e__zPa8JqTaIgOGL7ANu5T2SyZVwe3LziL4N2_bASWnWm78RSjix3keiLFCne8pVL2XYsVwmHjg2Qh45Uf-RtnSpZA45sV75q1Zn86ux6HsnzJDU-ZsH2ddXOuhP0VAIeZt2AAxC5Gt2-VvRCylIs5AfYMX8LAYk4zq-ceDKjXbJXgjhjS2C-pfkVh53mcAF0OkuzHP6UgL3VtkRsXvpGOF5_gEJ4HStQhBCJmU5ANLqo6FxA7pa0Yb5Ysz5cWjICaypEu_lFkQ8OCOq-UdAR0dlg3iARyPYwi4YQQO2X-JejMbUL5ylSaSZjBYSeWAVOlFSlXYc_Fjq3yzKessxg1ORc_B1gchUDkIb_9l6ukY4eJafSEwQVEPuuSjurvkZdpukSeHYZ8NLzyvqBp-P-Hd-8mbuGr63f6Fkhyvu517biVgIEr45kKZh1kZSwx0EIWZ03TsEB2X2MCquDfewRZS50sO-gPdkt5GlQwi70jrLKaybIM1Xo4qbygs3TdueD42Qe8GUJhRzQPk_7BGAOkOUhRXXtidnnM0ErTobo6oFQs5F6DSpeu7OqYg3BeeFYIbVb7BdWwRvqD4BGRqQDuc_MVMCGBxCuHisYYxxhYVlfwb68rg-umlCbWlMvMsR9VJIayzal9OAhofca4jvvT43K1OVQ4pP0nblyIlIYhzG3i6q5d5oUlqP5R7hDL5Vs9scVrLkfxW9jGrRaZIeYpgHHGAl8XBDfT6WwIyaB3OkXY1ge4p4je2pM9Dg-T-cKB05-CmlEAo_JtKrNectv66p9bQMfTdFIDGWxx6yGtt07JHWxmZmVUrCvTGAX8gPXbeCyTx2ccE_w; bl.auth.cookie.oidcC2=Z7BHKIfgA3SWVGttnWi89sc6jymWZ6ZCqxKoEGFSaGiOQBdufYJTIONeM9hm5IPFJ85XZZXBlw5T7aiVdMfvDrftfCdGZooS3oID_cASxYjvE9GoCNYTzfoRoJTIqgtZNtQykeiQZzn6v2cmhbWk-Sc9Z81nVnSdOXJLla_XcS2SIEPDPgNcAZNnrP-XzJ3ZrU5GkOYA9G02It6-HAhDOhRu44n5aKCbhBRBvfJeKZiPVaFjqewQYwLI17rtt8aL-zpZHqrjwzj-q6xU7qNwk2eA2LKEwgUM1gw2hctVjkUc9zZH6s_SdyI9j4WddWqM-ULKlQmjgljeZ5o79wOFtH7o_7tH9fXLMerMH4nzpUjdj9fM9qPRIRh9NjIy84WgajYBWbmiibAvuJbofHvW9qH456Kq9nOH3QARdSNkMv31WKGRxLM0jEHmlmD8cYbFIF5MK5KbeGYQA7dAnFpabOTh0TZUVoUkUOo-Vm9KvMCTaTpXQhSycgbsy1mWZTMa6hBDHRdwobx4ETnH89VDdU-Kigb085Mtdm95A_pNKGQULOuhUkwu7c7CtgXRe5NPa4ITjx7_1r1jmMt1IVMkK2-puHHxf7Zbls_JI0rmbJjx0lbaF0E7Ah_KK0yJuNTaF2oD5UeuMlR_z_Z2ef5fN3x1rzH9catg4GEB6nkGO_XyxWzikrknmdKQBBrfpwUFTqGSym_RYjY5I4wJuLWKVbY1ovx1wPhDCrmt0DYcHsE-XOVZdykdS8754AA_2EGYlDz6l1kPGt1vNEczT_nCFQYviZ48sso3mpjKj9AyB9asLi6G-3QeC7kgAQWncaaAYe1iSthZj_dB9xJFnyPgxdZsUKP6LSEd5QPqIwZdd2dHmItsYtpi5IrGkDTU8IYC6Wx3Qj14u_RHre0UN_-zbI-CJeCWt17jHnslRplukPfVU1CAvEmKbc5KELc12_tdYvo_u2dm9pVMu8mkbuO_4buq-63agc-MDHWQ0dScpbx6-QKq_Duo5wjcetsiMKMoEIeQAQz9gqKeiRB7W8MwgP_bG4d-in9SN8LRmCn5TaXcxoovk_Ziuz4pT2gFd2lAyqnrEeKLws86d82GOlaxjrBhQAZQV6qka7oAZFO-eVoiD0QgGcHj7ZBaWtYcezyEiNUg66PCRk9GHdMKGvzbl7qrfKTy5PfyQLGh5j1fv7i544WHzUF1ziuXgC0vYDbvst2qU7JfUPmOwWId3uChj-ksssnvvKjfH7IcgALwKuQWkMHweQb1qw0ss6mmLrqHOVNp_VhgcOc8RiW7TeBQ2i5MsxcI7y6pdTP0AFKCP9dS3ldjWqiKs0wvumQ_aeXuiKR2GIdAY1sX7iR37MfRArIHZPfz1vEpb2Lpa1yWiIQvev8OCrIUXwhIqNNTHxKQQtSrNJINJ0iAvrcB-m3zCDvm0H-EfDZ7e1IiB5Qh0kPt7JNsqK9WuQLGHEeJ1Z_ydQisnfGFTk5CK-7R4CJXGc9PLM; __cf_bm=QkrlQ5iXOpSkuP_VHL6HbcHzy6wZX9RG4JuRH0_3CUU-1755329580-1.0.1.1-6FzZsNMG8Lr4Wofe1XVw4TTNUXBfcVF0DOWVJ81ZfUYG0LTj7lGO1RtQPvtoe6vNzw7V3kaDmNYkU0K3O8HllWF1Yay1Pou8yFDQlCCBnh4; .ASPXROLES=bK3qBjKasw27w1c3bN8KaBG1_TF_0wtKve82P6kdo-LhUPoNMZ3NYf-A9L6qnZhDyCA4dkVJz-8MeLMpE5EH0_qEFhh9gVnw9md5cN33gNFEAdYjHkXiMbS8WkDzz5QZf3ru2deYT8B9tY_86zEuAS_f8N12RrJdAJQXYE1sVuCZfQ1M7j4YxDTn0k6xkk3FBRR1XCUN_R4lxfMt4jaiRBATNjRXaHWBp94N-crSEQ0f1RLhfxXMaKwNZaxpf80LzxdgL2x8nQIT4lnVJlOJYAZADdBqO1uBBvcUNqQlL-pDcppHjfi1iJ8PtIDVyBIeM1zQlfWGdk4rjKQd6CemtOwduuiQkYNzkjHJqXok0bm0mNZOOKOvn5HtfPsZZS3hC7YbotVW5NJHu7x3_0938yJ75sr0qYB6GIa0MDQcuVI0d3jqvd6TdCQNV-EWG666XrHOcqPzDc0b0dLs5mWqI4iLAz6VkOtc9YecCbvYoLt-ynqpDlCFI6BLLRrMY9rg0"

# Headers to mimic browser request
HEADERS = {
    'Cookie': COOKIE_VALUE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def load_document_ids():
    """Load document IDs and dates from YAML file."""
    try:
        with open(DOCS_FILE, 'r') as file:
            data = yaml.safe_load(file)
        
        # Handle different YAML structures
        if isinstance(data, list):
            # If it's a simple list of IDs, return them with no dates
            return [(doc_id, None) for doc_id in data]
        elif isinstance(data, dict):
            # If it's a dict, try to find document IDs
            if 'docs' in data:
                docs = data['docs']
                if isinstance(docs, list):
                    # Check if docs is a list of dictionaries with id and date
                    if docs and isinstance(docs[0], dict) and 'id' in docs[0]:
                        return [(doc['id'], doc.get('date')) for doc in docs]
                    else:
                        # Simple list of IDs
                        return [(doc_id, None) for doc_id in docs]
                else:
                    return [(docs, None)]
            elif 'documents' in data:
                return [(doc_id, None) for doc_id in data['documents']]
            elif 'ids' in data:
                return [(doc_id, None) for doc_id in data['ids']]
            else:
                # Assume all values are document IDs
                return [(doc_id, None) for doc_id in data.values()]
        else:
            raise ValueError("Unsupported YAML format")
    
    except FileNotFoundError:
        print(f"Error: {DOCS_FILE} not found in current directory.")
        print("Please create a docs.yaml file with your document IDs.")
        print("Example format:")
        print("docs:")
        print("  - id: 1224994")
        print("    date: \"8/8/25\"")
        print("  - id: 1224995") 
        print("    date: \"8/9/25\"")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def get_filename_from_headers(response):
    """Extract filename from Content-Disposition header."""
    content_disposition = response.headers.get('content-disposition', '')
    
    # Try to extract filename from Content-Disposition header
    if 'filename=' in content_disposition:
        filename_match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disposition)
        if filename_match:
            filename = filename_match.group(1).strip('\'"')
            return unquote(filename)
    
    return None

def parse_date_to_yyyy_mm_dd(date_str):
    """Parse date string from YAML and convert to YYYY_MM_DD format."""
    if not date_str:
        return datetime.now().strftime('%Y_%m_%d')
    
    try:
        # Handle format like "8/8/25" or "8/8/2025"
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                # Convert 2-digit year to 4-digit year (assuming 20xx)
                if len(year) == 2:
                    year = '20' + year
                
                # Create datetime object and format
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y_%m_%d')
        
        # Handle other common date formats
        date_formats = [
            '%m/%d/%Y',   # 8/8/2025
            '%m/%d/%y',   # 8/8/25
            '%Y-%m-%d',   # 2025-08-08
            '%m-%d-%Y',   # 08-08-2025
            '%m-%d-%y',   # 08-08-25
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y_%m_%d')
            except ValueError:
                continue
                
    except (ValueError, TypeError):
        pass
    
    # Fallback to current date if parsing fails
    print(f"Warning: Could not parse date '{date_str}', using current date")
    return datetime.now().strftime('%Y_%m_%d')

def download_file(doc_id, doc_date, session):
    """Download a single file given its document ID and date."""
    url = f"{BASE_URL}?id={doc_id}&open=inline"
    
    try:
        print(f"Downloading document ID: {doc_id}")
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get filename from headers
        filename = get_filename_from_headers(response)
        
        # Get file date from YAML data
        file_date = parse_date_to_yyyy_mm_dd(doc_date)
        
        if not filename:
            # Fallback to generic filename with extension based on content-type
            content_type = response.headers.get('content-type', '')
            if 'pdf' in content_type:
                ext = '.pdf'
            elif 'image' in content_type:
                ext = '.jpg'  # Default image extension
            elif 'text' in content_type:
                ext = '.txt'
            else:
                ext = '.bin'  # Binary file
            
            filename = f"document_{doc_id}{ext}"
        
        # Prepend date to filename
        name_parts = filename.rsplit('.', 1)  # Split filename and extension
        if len(name_parts) == 2:
            name, ext = name_parts
            filename = f"{file_date}_{name}.{ext}"
        else:
            # No extension found
            filename = f"{file_date}_{filename}"
        
        # Create downloads directory if it doesn't exist
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        
        # Full file path
        file_path = DOWNLOAD_DIR / filename
        
        # Check if file already exists
        if file_path.exists():
            file_size = file_path.stat().st_size
            print(f"⚠ Skipping: {filename} (already exists, {file_size:,} bytes)")
            return True
        
        # Handle duplicate filenames (in case of naming conflicts)
        counter = 1
        original_path = file_path
        while file_path.exists():
            name = original_path.stem
            ext = original_path.suffix
            file_path = DOWNLOAD_DIR / f"{name}_{counter}{ext}"
            counter += 1
        
        # Download and save file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = file_path.stat().st_size
        print(f"✓ Downloaded: {filename} ({file_size:,} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading document ID {doc_id}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error downloading document ID {doc_id}: {e}")
        return False

def create_zip_archive():
    """Create a zip file containing all downloaded documents."""
    zip_path = Path(__file__).parent / "condo_docs.zip"
    
    # Check if downloads directory exists and has files
    if not DOWNLOAD_DIR.exists() or not any(DOWNLOAD_DIR.iterdir()):
        print("No files to zip - downloads directory is empty")
        return False
    
    try:
        print(f"\nCreating zip archive: {zip_path.name}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            total_size = 0
            
            # Add all files from downloads directory to zip
            for file_path in DOWNLOAD_DIR.iterdir():
                if file_path.is_file():
                    # Add file to zip with just the filename (not the full path)
                    zipf.write(file_path, file_path.name)
                    file_count += 1
                    total_size += file_path.stat().st_size
                    print(f"  Added: {file_path.name}")
        
        zip_size = zip_path.stat().st_size
        compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
        
        print(f"✓ Zip archive created successfully!")
        print(f"  Files: {file_count}")
        print(f"  Original size: {total_size:,} bytes")
        print(f"  Compressed size: {zip_size:,} bytes")
        print(f"  Compression: {compression_ratio:.1f}%")
        print(f"  Location: {zip_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating zip archive: {e}")
        return False

def main():
    """Main function to orchestrate the download process."""
    print("BuildingLink Document Downloader")
    print("=" * 40)
    
    # Check if cookie is set
    if COOKIE_VALUE == "your_cookie_value_here":
        print("Error: Please set your cookie value in the COOKIE_VALUE variable.")
        print("You can find this in your browser's developer tools under Network tab.")
        return
    
    # Load document IDs and dates
    doc_data = load_document_ids()
    if not doc_data:
        return
    
    print(f"Found {len(doc_data)} documents to download")
    
    # Create a session to reuse connections
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Download files
    successful = 0
    failed = 0
    skipped = 0
    
    for i, (doc_id, doc_date) in enumerate(doc_data, 1):
        print(f"\n[{i}/{len(doc_data)}] ", end="")
        
        result = download_file(doc_id, doc_date, session)
        if result is True:
            # Check if it was skipped by looking at the last print message
            # This is a simple way - in a more complex system you'd return different status codes
            successful += 1
        else:
            failed += 1
        
        # Small delay to be respectful to the server
        time.sleep(0.5)
    
    # Summary
    print(f"\n" + "=" * 40)
    print(f"Download complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Files saved to: {DOWNLOAD_DIR.absolute()}")
    
    # Create zip archive if we downloaded any files
    if successful > 0:
        create_zip_archive()
    else:
        print("No files were downloaded, skipping zip creation")

if __name__ == "__main__":
    main()