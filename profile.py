from bs4 import BeautifulSoup

def parse_student_profile(html):
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "profile_picture": None,
        "personal_info": {},
        "education_info": {},
        "contact_info": {},
        "address_info": {},
        "family_info": {},
        "other_info": {}
    }

    # -------------------------
    # Profile picture
    # -------------------------
    pic_div = soup.find("div", class_="profile-userpic")
    if pic_div and pic_div.find("img"):
        result["profile_picture"] = pic_div.find("img").get("src")

    app_div = soup.find("div", id="app")
    if not app_div:
        return result

    def clean(text):
        return " ".join(text.split())

    # -------------------------
    # Generic label-value parser
    # -------------------------
    for group in app_div.find_all("div", class_="form-group"):
        label = group.find("label")
        value_div = group.find("div", class_=lambda x: x and "col-" in x)

        if not label or not value_div:
            continue

        key = clean(label.get_text())
        value = clean(value_div.get_text())

        if not value:
            continue

        # -------------------------
        # Categorization
        # -------------------------
        if key in ["نام", "نام پدر", "نام پدرکلان", "نام فامیلی", "ملیت", "زبان مادری", "جنسیت"]:
            result["personal_info"][key] = value

        elif key in ["درجه", "پوهنتون", "دیپارتمنت", "سمستر", "سال کانکور", "نمره کانکور", "ID کانکور"]:
            result["education_info"][key] = value

        elif "تماس" in key or "phone" in key.lower():
            result["contact_info"][key] = value

        elif key in ["ادرس", "اصلی", "فعلی"]:
            result["address_info"][key] = value

        else:
            result["other_info"][key] = value

    # -------------------------
    # Family / emergency contact section
    # -------------------------
    family_rows = app_div.find_all("div", class_="row")
    for row in family_rows:
        cols = row.find_all("div", class_="col-md-3")
        if len(cols) == 4:
            relation = clean(cols[0].get_text())
            name = clean(cols[1].get_text())
            job = clean(cols[2].get_text())
            phone = clean(cols[3].get_text())

            if relation and name:
                result["family_info"] = {
                    "relation": relation,
                    "name": name,
                    "job": job,
                    "phone": phone
                }

    return result