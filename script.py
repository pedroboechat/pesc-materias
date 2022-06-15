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
    try:
        mapper = {
            "COD.": "codigo",
            "Códigos": "codigo",
            "CRED": "creditos",
            "Céditos": "creditos",
            "Créditos": "creditos",
            "TURMA": "turma",
            "Turmas": "turma",
            "DISCIPLINA": "disciplina",
            "Disciplinas": "disciplina",
            "HORÁRIO": "horario",
            "Horários": "horario",
            "SALA": "sala",
            "Sala": "sala",
            "Salas": "sala",
            "MOODLE": "sala",
            "Pres/Híbrid": "tipo",
            "PROFESSOR": "docentes",
            "Docentes": "docentes",
            "Graduação?": "graduacao",
            "Grad.": "graduacao",
            "GRADUAÇÃO": "graduacao"
        }
        return mapper[column_name]
    except KeyError as error:
        raise KeyError(
            f"New column name ({column_name}): Please update `column_renamer` function."
        ) from error

## Initialize DataFrame
df = pd.DataFrame()

## Loop through `semesters_list` extracting page data
for semester, soup in semesters_list:
    TABLE_HTML = str(soup.find(
        "table"
    ))

    table_df = pd.read_html(
        TABLE_HTML,
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
