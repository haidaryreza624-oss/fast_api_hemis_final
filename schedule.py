from bs4 import BeautifulSoup

def parse_all_panel_tables(html):
    soup = BeautifulSoup(html, "html.parser")
    
    panel_body = soup.find("div", class_="panel-body")
    if not panel_body:
        return []

    all_tables = []

    # Loop through every table inside the panel-body
    for table in panel_body.find_all("table"):
        table_data = []

        # Grab headers if any
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if cols:
                if headers and len(headers) == len(cols):
                    row_data = {headers[i]: cols[i].get_text(strip=True) for i in range(len(cols))}
                else:
                    # fallback: list of cell values if no headers or mismatch
                    row_data = [col.get_text(strip=True) for col in cols]
                table_data.append(row_data)

        all_tables.append(table_data)

    return all_tables



