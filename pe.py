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
    "tgcc": {"Nom": "TGCC", "Profil": "Construction, croissance élevée", "Target_PE": 17}
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
        target_pe=watchlist[name.lower()]["Target_PE"]
        scraped_data.append({"Company-name":name,"P/E":pe_ratio,
                             "Target_PE":target_pe})
df=pd.DataFrame(scraped_data)
df["PE_Score"]=df["Target_PE"]/df["P/E"]
df["PE_Score"]=df["PE_Score"].round(2)
df=df.sort_values(by="PE_Score",ascending=False)
print(df)

