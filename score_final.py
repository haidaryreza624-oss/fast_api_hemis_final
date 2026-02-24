from bs4 import BeautifulSoup
import json

def safe_float(value):
    """Convert to float safely, return None if empty or invalid"""
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None

def safe_int(value):
    """Convert to int safely, return None if empty or invalid"""
    try:
        return int(float(value.replace(",", "").strip()))
    except (ValueError, AttributeError):
        return None

def extract_all_scores(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    
    result = {
        "semesters": [],
        "final_result": {}
    }
    
    semesters = soup.find_all("div", class_="semester-scores")
    for sem in semesters:
        sem_info = {}
        
        # Semester number
        group_row = sem.find("tr", class_="group-by")
        if group_row:
            sem_number_text = group_row.find("td").text.strip()
            try:
                sem_info["semester_number"] = int(sem_number_text.split(":")[-1].strip())
            except ValueError:
                sem_info["semester_number"] = None
        
        # Subjects
        sem_info["subjects"] = []
        subject_table = sem.find("table", class_="stripe")
        if subject_table:
            rows = subject_table.find_all("tr")[2:]  # skip headers
            for row in rows:
                cells = [c.text.strip() for c in row.find_all("td")]
                if len(cells) < 11:
                    continue
                subject = {
                    "number": safe_int(cells[0]),
                    "name": cells[1] if cells[1] else None,
                    "year": cells[2] if cells[2] else None,
                    "first_chance": safe_float(cells[3]),
                    "second_chance": safe_float(cells[4]),
                    "third_chance": safe_float(cells[5]),
                    "fourth_chance": safe_float(cells[6]),
                    "credits": safe_float(cells[7]),
                    "pass_score": safe_float(cells[8]),
                    "pass_chance": safe_int(cells[9]),
                    "weighted_score": safe_float(cells[10])
                }
                sem_info["subjects"].append(subject)
        
        # Semester results
        result_table = sem.find("table", class_="results")
        sem_info["semester_result"] = None
        if result_table:
            data_row = result_table.find("tr", class_="passed-semester")
            if data_row:
                cells = [c.text.strip() for c in data_row.find_all("td")]
                if len(cells) == 8:
                    sem_info["semester_result"] = {
                        "year": cells[0] if cells[0] else None,
                        "semester": safe_int(cells[1]),
                        "result_metric": safe_float(cells[2]),
                        "grade": cells[3] if cells[3] else None,
                        "passed": cells[4] if cells[4] else None,
                        "semester_promotion": cells[5] if cells[5] else None,
                        "semester_credits": safe_float(cells[6]),
                        "passed_credits": safe_float(cells[7])
                    }
        
        result["semesters"].append(sem_info)
    
    # Final results
    final_div = soup.find("div", class_="row total-results")
    result["final_result"] = None
    if final_div:
        final_table = final_div.find("table")
        if final_table:
            final_row = final_table.find_all("tr")[1]
            cells = [c.text.strip() for c in final_row.find_all("td")]
            if len(cells) == 5:
                result["final_result"] = {
                    "subjects_count": safe_int(cells[0]),
                    "total_credits": safe_float(cells[1]),
                    "total_score": safe_float(cells[2]),
                    "average_score": safe_float(cells[3]),
                    "passed_semesters": safe_int(cells[4])
                }
    
    return result