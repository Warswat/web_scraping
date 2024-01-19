import fake_headers
import requests
from bs4 import BeautifulSoup
import json


def gen_headers():
    headers_gen = fake_headers.Headers(os="win", browser="chrome")
    return headers_gen.generate()


def get_vacancies_tags(pages):
    main_response = requests.get(f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={pages}",
                                 headers=gen_headers())
    main_html_data = main_response.text
    main_soup = BeautifulSoup(main_html_data, "lxml")
    vacancies_list_tag = main_soup.find("main", class_="vacancy-serp-content")
    return vacancies_list_tag


if __name__ == "__main__":
    parsed_data = []

    for page in range(0,2):
        for vacancies_tag in get_vacancies_tags(page).find_all("div", class_="serp-item"):
            vacancy_link = vacancies_tag.find("a", class_="bloko-link")["href"]
            vacancies_response = requests.get(vacancy_link, headers=gen_headers())
            vacancies_html_data = vacancies_response.text
            vacancies_soup = BeautifulSoup(vacancies_html_data, "lxml")

            if vacancies_soup.find("div", class_="vacancy-description") and "flask" and "django" in vacancies_soup.find(
                    "div", class_="vacancy-description").text.lower():

                if vacancies_soup.find("div", attrs={"data-qa":"vacancy-salary"}):
                    salary = vacancies_soup.find("div", attrs={"data-qa":"vacancy-salary"}).text
                else:
                    salary = "Вилка ЗП не указана"

                if vacancies_soup.find("a", attrs={"data-qa":"vacancy-company-name"}):
                    company = vacancies_soup.find("a", attrs={"data-qa":"vacancy-company-name"}).text
                else: company = "Название компании не указано"

                if vacancies_soup.find("p", attrs={"data-qa":"vacancy-view-location"}):
                    location = vacancies_soup.find("p", attrs={"data-qa":"vacancy-view-location"}).text
                else: location = "Город не указан"

                parsed_data.append({
                    "link": vacancy_link,
                    "salary": salary,
                    "company": company,
                    "location": location,
                })
    with open('hh_data','w', encoding="utf-8", ) as f:
        json.dump(parsed_data,f,ensure_ascii=False)