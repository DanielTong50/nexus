
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def test_google_sheets():
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    
    print("=== Google Sheets Connection Test ===\n")
    
    # 1. Check env vars
    if not creds_json:
        print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not set")
        return
    else:
        print("✅ GOOGLE_SERVICE_ACCOUNT_JSON is set")
        try:
            creds_data = json.loads(creds_json)
            print(f"   → Service Account: {creds_data.get('client_email', 'unknown')}")
        except json.JSONDecodeError:
            print("❌ GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON")
            return
    
    if not spreadsheet_id:
        print("❌ GOOGLE_SHEETS_SPREADSHEET_ID not set")
        return
    else:
        print(f"✅ GOOGLE_SHEETS_SPREADSHEET_ID: {spreadsheet_id}")
    
    # 2. Try to connect
    print("\n2. Testing API Connection...")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=credentials)
        print("✅ Google Sheets API client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        return
    
    # 3. Try to read data
    print("\n3. Testing Read Access...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Boothing Companies!A1:G5"
        ).execute()
        values = result.get("values", [])
        print(f"✅ Read {len(values)} rows from 'Boothing Companies'")
        if values:
            print(f"   → Headers: {values[0]}")
    except Exception as e:
        print(f"❌ Read failed: {e}")
        return
    
    # 4. Try to append data (test row)
    print("\n4. Testing Write Access (append test row)...")
    try:
        test_row = [["TEST_COMPANY", "Test Contact", "test@example.com", "Test", "Pending", "Booth", "DELETE THIS ROW"]]
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Boothing Companies!A:G",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": test_row}
        ).execute()
        updated = result.get("updates", {}).get("updatedCells", 0)
        print(f"✅ Appended test row! Updated {updated} cells.")
        print("   → Please check the sheet and delete the TEST_COMPANY row.")
    except Exception as e:
        print(f"❌ Write failed: {e}")
        if "PERMISSION_DENIED" in str(e):
            print("   → Service account may not have write access to the sheet!")
            print("   → Share the sheet with the service account email with Editor permissions.")

if __name__ == "__main__":
    test_google_sheets()
