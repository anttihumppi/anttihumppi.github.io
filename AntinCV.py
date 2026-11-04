# -*- coding: utf-8 -*-
import base64
import os
import pandas as pd
import plotly.express as px
import pyodbc

# ==========================================
# 1. ASETUKSET JA TIETOKANTAYHTEYS
# ==========================================
SERVER = "Antsa\Antsan"  # Muuta tarvittaessa
DATABASE = "TEST"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# ==========================================
# 2. DATAN HAKU SSMS-TIETOKANNASTA
# ==========================================
print("Haetaan dataa tietokannasta...")

query = """
SELECT TOP (1000) 
      [Job_ID]
      ,[Employer]
      ,[Role]
      ,[Work start]
      ,[Work end]
      ,[Supervisor]
      ,[Role_Desc]
      ,[Sijainti]
  FROM [TEST].[dbo].[Career]
  ORDER BY Job_ID ASC
"""

try:
  with pyodbc.connect(conn_str) as conn:
    df = pd.read_sql(query, conn)
  print(f"Data haettu onnistuneesti! Rivejä yhteensä: {len(df)}")
except Exception as e:
  print(f"Virhe tietokantayhteydessä: {e}")
  exit()

# Muunnetaan päivämäärät oikeaan muotoon
df["Work start"] = pd.to_datetime(df["Work start"])
df["Work end"] = pd.to_datetime(df["Work end"])

df["Start_Str"] = df["Work start"].dt.strftime("%d.%m.%Y")
df["End_Str"] = df["Work end"].dt.strftime("%d.%m.%Y")

df["Role_Desc_HTML"] = (
    df["Role_Desc"]
    .astype(str)
    .str.replace("\r\n", "<br>")
    .str.replace("\n", "<br>")
)
df["Y_Label"] = (
    df["Job_ID"].astype(str) + ": " + df["Employer"] + " (" + df["Role"] + ")"
)
df["TaskLabel"] = df["Employer"] + " - " + df["Role"]

# ==========================================
# 3. PLOTLY GANTT -KAAVION RAKENTAMINEN
# ==========================================
print("Luodaan Gantt-kaaviota...")

fig = px.timeline(
    df,
    x_start="Work start",
    x_end="Work end",
    y="Y_Label",
    color="Employer",
    hover_name="TaskLabel",
    custom_data=[
        "Start_Str",
        "End_Str",
        "Role_Desc_HTML",
        "Sijainti",
        "Supervisor",
    ],
)

fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>"
    + "📅 Aika: %{customdata[0]} – %{customdata[1]}<br>"
    + "📍 Sijainti: %{customdata[3]}<br>"
    + "👤 Esihenkilö: %{customdata[4]}<br><br>"
    + "<b>Tehtävät ja saavutukset:</b><br>%{customdata[2]}<extra></extra>"
)

sorted_y_labels = df.sort_values("Job_ID", ascending=True)[
    "Y_Label"
].tolist()

fig.update_yaxes(
    categoryorder="array", categoryarray=sorted_y_labels, title="Työhistoria"
)
fig.update_xaxes(title="Aikajana")

fig.update_layout(
    font_family="Arial",
    title_text="Antti Humppi - Työhistoria",
    title_font_size=22,
    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial"),
    height=750,
    margin=dict(l=50, r=50, t=80, b=50),
    legend_title="Työnantajat",
)

# ==========================================
# 4. PROFIILIKUVAN MUUNNUS BASE64-MUOTOON
# ==========================================
# Kirjoita tähän kuvatiedostosi tarkka nimi (esim. 'antti.jpg' tai 'kuva.png')
image_filename = "AnttiHumppi2.jpg"

img_tag = '<img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/icons/person-circle.svg" alt="Antti Humppi" class="profile-img">'

if os.path.exists(image_filename):
  with open(image_filename, "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
    ext = image_filename.split(".")[-1].lower()
    mime_type = "image/png" if ext == "png" else "image/jpeg"
    img_tag = f'<img src="data:{mime_type};base64,{encoded_string}" alt="Antti Humppi" class="profile-img">'
  print("Profiilikuva upotettu onnistuneesti tiedostoon!")
else:
  print(
      f"Huom: Kuvatiedostoa '{image_filename}' ei löytynyt samasta kansiosta."
      " Käytetään oletuskuvaketta."
  )

# ==========================================
# 5. ITSEMÄINEN HTML-SIVUN LUOMINEN
# ==========================================
plotly_div = fig.to_html(full_html=False, include_plotlyjs="cdn")

html_content = rf"""
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <title>Antti Humppi - CV Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .header-container {{
            max-width: 1200px;
            margin: 0 auto 20px auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .profile-img {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #0077b5;
        }}
        .header-info h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
            color: #111;
        }}
        .header-info p {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .linkedin-btn {{
            display: inline-block;
            background-color: #0077b5;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
            transition: background 0.2s;
        }}
        .linkedin-btn:hover {{
            background-color: #004182;
        }}
        .card {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>

    <div class="header-container">
        {img_tag}
        <div class="header-info">
            <h1>Antti Humppi</h1>
            <p>Interaktiivinen työhistoria & Gantt-profiili</p>
            <a href="https://www.linkedin.com/in/anttihumppi/" target="_blank" class="linkedin-btn">🔗 LinkedIn-profiili</a>
        </div>
    </div>

    <div class="card">
        {plotly_div}
    </div>

</body>
</html>
"""

output_filename = "Antti_Humppi_CV.html"
with open(output_filename, "w", encoding="utf-8") as f:
  f.write(html_content)

print(f"Valmis! Itsenäinen CV luotu nimellä: {output_filename}")
