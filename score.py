from bs4 import BeautifulSoup

def parse_scores(html):
    soup = BeautifulSoup(html, "html.parser")
    semesters = []

    # Find all tables grouped by semester
    tables = soup.find_all("table", class_="table")
    for table in tables:
        # Find semester number from the group-by row
        group_row = table.find("tr", class_="group-by")
        if not group_row:
            continue
        semester_text = group_row.get_text(strip=True)
        # Extract the number after "سمستر : "
        semester_number = int(semester_text.split(":")[-1].strip())

        subjects = []
        # All rows after header
        rows = table.find_all("tr")[2:]  # skip group-by and header
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 15:
                continue  # skip malformed rows

            def parse_float(cell):
                try:
                    return float(cell.get_text(strip=True))
                except:
                    return None

            subject = {
                "number": int(cells[0].get_text(strip=True)),
                "name": cells[1].get_text(strip=True),
                "credits": parse_float(cells[2]),
                "attendance": parse_float(cells[3]),
                "absent": parse_float(cells[4]),
                "homework_10": parse_float(cells[5]),
                "activity_10": parse_float(cells[6]),
                "midterm_20": parse_float(cells[7]),
                "final_60": parse_float(cells[8]),
                "total_100": parse_float(cells[9]),
                "second_chance": parse_float(cells[10]),
                "third_chance": parse_float(cells[11]),
                "fourth_chance": parse_float(cells[12]),
                "status": cells[13].get_text(strip=True),
                "final_approval": cells[14].get_text(strip=True)
            }
            subjects.append(subject)

        semesters.append({
            "semester_number": semester_number,
            "subjects": subjects
        })

    return {"semesters": semesters}