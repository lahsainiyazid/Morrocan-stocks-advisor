import pandas as pd 
import cloudscraper 
from bs4 import BeautifulSoup 

url = "https://casabourse.ma/screener/"

watchlist = {
  "Addoha": 24.5,
  "AFMA": 16.5,
  "Afric Industries": 14.0,
  "Afriquia Gaz": 18.2,
  "Agma": 15.5,
  "Akdital": 32.0,
  "Alliances": 26.0,
  "Aluminium du Maroc": 14.0,
  "Aradei Capital": 17.0,
  "AtlantaSanad Assurance": 15.0,
  "Attijariwafa bank": 16.0,
  "Auto Hall": 14.0,
  "Auto Nejma": 14.0,
  "Balima": 18.0,
  "Bank Of Africa": 14.0,
  "BCP": 14.5,
  "BMCI": 13.0,
  "CARTIER SAADA": 17.5,
  "Cash Plus": 22.0,
  "CDM": 13.0,
  "CFG Bank": 23.0,
  "CIH Bank": 15.0,
  "Ciments du Maroc": 20.0,
  "CMGP GROUP": 20.0,
  "Colorado": 15.5,
  "Cosumar": 24.0,
  "CTM": 16.0,
  "DARI COUSPATE": 25.0,
  "Delta Holding": 15.5,
  "DIAC SALAF": 12.0,
  "Disty Technologies": 16.0,
  "Disway": 13.0,
  "Ennakl Automobiles": 12.5,
  "Eqdom": 12.5,
  "Fenie Brossette": 14.0,
  "HPS": 25.0,
  "IB MAROC.COM": 18.0,
  "Immorente Invest": 15.0,
  "INVOLYS": 21.0,
  "Jet Contractors": 15.0,
  "Label Vie": 30.0,
  "LafargeHolcim Maroc": 22.0,
  "Lesieur Cristal": 21.0,
  "M2M Group": 18.0,
  "Maghreb Oxygene": 16.5,
  "MAGHREBAIL": 13.5,
  "Managem": 25.5,
  "Maroc Leasing": 13.0,
  "Maroc Telecom": 16.0,
  "Marsa Maroc": 19.0,
  "MED PAPER": 12.0,
  "Microdata": 15.0,
  "Miniere de Touissit": 22.0,
  "Mutandis": 18.5,
  "Oulmes": 26.0,
  "Promopharm": 17.0,
  "REALISATIONS MECANIQUES": 14.0,
  "REBAB COMPANY": 15.0,
  "Résidences Dar Saada": 24.0,
  "Risma": 22.0,
  "S.M MONETIQUE": 16.5,
  "Salafin": 13.0,
  "Sanlam Maroc": 15.0,
  "SGTM": 19.0,
  "SMI": 22.0,
  "SNEP": 15.0,
  "Société des Boissons du Maroc": 20.0,
  "Sonasid": 16.0,
  "Sothema": 23.0,
  "Stokvis Nord Afrique": 12.5,
  "STROC INDUSTRIE": 13.5,
  "T2S": 18.0,
  "Taqa Morocco": 17.0,
  "TGCC": 18.0,
  "Total Energies Maroc": 16.0,
  "Unimer": 13.5,
  "Vicenne": 27.0,
  "Wafa Assurance": 18.5,
  "ZELLIDJA S.A": 16.5
}

# 1. Convert watchlist keys to lowercase once for safe matching and lookup
watchlist_lower = {k.lower(): v for k, v in watchlist.items()}

scraper = cloudscraper.create_scraper()
html = scraper.get(url).text 
soup = BeautifulSoup(html, "html.parser")
rows = soup.find_all("tr")

scraped_data = []

for row in rows:
    name_tag = row.find("a", class_="company-name")
    if not name_tag:
        continue 
    
    name = name_tag.text.strip()
    name_key = name.lower()
    
    # Check if the scraped company is in our lowercase watchlist
    if name_key in watchlist_lower:
        # Initialize default variables to avoid NameErrors if scraping fails
        pe_ratio = float('nan')
        div_yield = 0.0
        price = 0.0
        
        # 2. Try-except for safe P/E ratio parsing
        pe_span = row.select_one('td[data-column-key="pe_ratio"] span')
        if pe_span:
            try:
                pe_ratio = float(pe_span.text.strip().replace(",", "").replace(" ", ""))
            except ValueError:
                pe_ratio = float('nan')
        
        # 3. Try-except for safe dividend yield parsing
        div_span = row.select_one('td[data-column-key="dividend_yield"] span')
        if div_span:
            try:
                div_raw = div_span.text.strip().replace("%", "").replace(" ", "").strip()
                div_yield = float(div_raw) if div_raw else 0.0
            except ValueError:
                div_yield = 0.0
        
        # 4. Try-except for safe current price parsing
        price_span = row.select_one('td[data-column-key="current_price"] span')
        if price_span:
            try:
                price = float(price_span.text.strip().replace(",", "").replace(" ", ""))
            except ValueError:
                price = 0.0
        
        # 5. Extract target_pe as a direct float lookup
        target_pe = watchlist_lower[name_key]
        
        scraped_data.append({
            "Company-name": name,
            "Price": price, 
            "P/E": pe_ratio,
            "Target_PE": target_pe,
            "Yield": div_yield
        })

# Create and process DataFrame
df = pd.DataFrame(scraped_data)
df=df[df["P/E"]!=0]
if not df.empty:
    # Coerce columns to numeric before doing operations to avoid Pandas errors
    df["P/E"] = pd.to_numeric(df["P/E"], errors='coerce')
    df["Target_PE"] = pd.to_numeric(df["Target_PE"], errors='coerce')
    df["Yield"] = pd.to_numeric(df["Yield"], errors='coerce')
    
    # Calculations (Pandas natively ignores/handles NaNs safely now)
    df["PE_Score"] = df["Target_PE"] / df["P/E"]
    df["PE_Score"] = df["PE_Score"].round(2)
    df=df[df["PE_Score"]>1]
    df["Score"] = df["PE_Score"] * (1 + (df["Yield"] / 100))
    df["Score"] = df["Score"].round(2)
    
    # Sort and rank
    df = df.sort_values(by=["Score", "PE_Score"], ascending=False)
    df.index = range(1, len(df) + 1)
    df.index.name = "Rank"
    
    print(df)
else:
    print("Warning: No matching companies from your watchlist were found on the page.")

