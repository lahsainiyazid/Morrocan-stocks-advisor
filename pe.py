import pandas as pd 
import cloudscraper 
from bs4 import BeautifulSoup 
url="https://casabourse.ma/screener/"
watchlist = {
    "maroc telecom": {"Nom": "Maroc Telecom", "Profil": "Mûre, dividendes élevés", "Target_PE": 14},
    "attijariwafa bank": {"Nom": "Attijariwafa Bank", "Profil": "Grande banque panafricaine", "Target_PE": 16},
    "bank of africa": {"Nom": "Bank of Africa", "Profil": "Forte croissance africaine", "Target_PE": 15},
    "bcp": {"Nom": "BCP", "Profil": "Banque solide, croissance modérée", "Target_PE": 14},
    "lafargeholcim maroc": {"Nom": "LafargeHolcim Maroc", "Profil": "Ciment, secteur cyclique", "Target_PE": 13},
    "managem": {"Nom": "Managem", "Profil": "Mines, forte croissance", "Target_PE": 18},
    "tgcc": {"Nom": "TGCC", "Profil": "Construction, croissance élevée", "Target_PE": 17},
     "addoha": {"Nom": "Addoha", "Profil": "Logement social & export Afrique de l'Ouest", "Target_PE": 10}
}
scraper=cloudscraper.create_scraper()
html=scraper.get(url).text 
soup=BeautifulSoup(html,"html.parser")
rows=soup.find_all("tr")
scraped_data=[]
for row in rows:
    name_tag=row.find("a",class_="company-name")
    if not name_tag :
        continue 
    name=name_tag.text.strip()
    if name.lower() in watchlist:
        pe_span=row.select_one('td[data-column-key="pe_ratio"] span')
        if pe_span:
            pe_ratio=float(pe_span.text.strip())
        else:
            pe_ratio="N/A"
        div_span=row.select_one('td[data-column-key="dividend_yield"] span')
        if div_span:
            try:
                div_raw=div_span.text.strip().replace("%","").replace(" ","").strip()
                div_yield=float(div_raw) if div_raw else 0.0
            except ValueError:
                div_yield=0.0
        price_span=row.select_one('td[data-column-key="current_price"] span')
        if price_span:
            price=float(price_span.text.strip().replace(",",""))
        target_pe=watchlist[name.lower()]["Target_PE"]
        scraped_data.append({"Company-name":name,
                             "Price":price, 
                             "P/E":pe_ratio,
                             "Target_PE":target_pe,"Yield":div_yield})
df=pd.DataFrame(scraped_data)
df["PE_Score"]=df["Target_PE"]/df["P/E"]
df["PE_Score"]=df["PE_Score"].round(2)
df["Score"]=df["PE_Score"]*(1+(df["Yield"]/100))
df["Score"]=df["Score"].round(2)
df=df.sort_values(by=["Score","PE_Score"],ascending=False)
df.index=range(1,len(df)+1)
df.index.name="Rank"
print(df)

