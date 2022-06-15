# Imports
## Standard libraries
import csv
import re
## Other libraries
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

# Base URL
BASE_URL = "https://www.cos.ufrj.br"

# Get `courses` page
## Get `courses` page HTML soup
COURSES_URL = "/index.php/pt-BR/pos-graduacao/disciplinas-3"

courses_soup = bs(
    requests.get(BASE_URL + COURSES_URL).text,
    "html.parser"
)

## Extract a list of `(semester, semester_soup)` tuples
semesters_list = [
    (
        x.find("a").text,
        bs(
            requests.get(BASE_URL + x.find("a").get("href")).text,
            "html.parser"
        )
    )
    for x in courses_soup.find_all("td", class_="list-title")
]

# Get `semester` pages
## Definition of helper functions
def column_renamer(column_name: str) -> str:
    """Column mapper for renaming DataFrames

    Args:
        column_name (str): Name of a column

    Returns:
        str: Mapped name for the column
    """
    if column_name == "COD.": return "codigo"
    if column_name == "Códigos": return "codigo"
    if column_name == "CRED": return "creditos"
    if column_name == "Céditos": return "creditos"
    if column_name == "Créditos": return "creditos"
    if column_name == "TURMA": return "turma"
    if column_name == "Turmas": return "turma"
    if column_name == "DISCIPLINA": return "disciplina"
    if column_name == "Disciplinas": return "disciplina"
    if column_name == "HORÁRIO": return "horario"
    if column_name == "Horários": return "horario"
    if column_name == "SALA": return "sala"
    if column_name == "Sala": return "sala"
    if column_name == "Salas": return "sala"
    if column_name == "MOODLE": return "sala"
    if column_name == "Pres/Híbrid": return "tipo"
    if column_name == "PROFESSOR": return "docentes"
    if column_name == "Docentes": return "docentes"
    if column_name == "Graduação?": return "graduacao"
    if column_name == "Grad.": return "graduacao"
    if column_name == "GRADUAÇÃO": return "graduacao"
    raise KeyError(f"New column name ({column_name}): Please update `column_renamer` function.")

## Initialize DataFrame
df = pd.DataFrame()

## Loop through `semesters_list` extracting page data
for semester, soup in semesters_list:
    table_html = str(soup.find(
        "table"
    ))

    table_df = pd.read_html(
        table_html,
        header=0,
        decimal=",",
        thousands="."
    )[0].rename(columns=column_renamer)

    table_df["semestre"] = re.sub(
        "\n|\r|\t",
        "",
        semester
    )
    
    df = pd.concat(
        [df, table_df]
    )

## Data treatment
### 1) `-----` to `NaN`
df = df.replace(re.compile(r"-+"), float("NaN"))

### 2) Fix typo and convert dtype for `creditos` column
df["creditos"] = df["creditos"].replace("vc 3,0", 3.0).astype(float)

# Export DataFrame
df.to_excel(
    "./courses.xlsx",
    index=False
)
df.to_csv(
    "./courses.zip",
    sep=";",
    index=False,
    compression={
        "method": "zip",
        "archive_name": "courses.csv"
    },
    quoting=csv.QUOTE_ALL
)
