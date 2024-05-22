from flask import Flask, render_template, request
import pandas as pd
import string
import requests
from math import radians, cos, sin, sqrt, atan2
import os
import json
from collections import Counter

app = Flask(__name__)
path = "C:\\Users\\SPYSEL\\Desktop\\hacaton\\flask\\database\\"
pathSave = "C:\\Users\\SPYSEL\\Desktop\\hacaton\\flask\\output\\"
organization_df = pd.read_excel(path+'Карточка мед.организации.xlsx')
normatives_df = pd.read_excel(path+'Нормативы.xlsx')
dataZastroy = pd.read_excel(path+'Данные по застройщикам.xlsx')
organization_staff_df = pd.read_excel(path+'Карточка мед.организации.xlsx', sheet_name='Штатное расписание')

api_key = '3ffe9d66-99e6-4de1-8735-35b76e3c29a7'

def clean_string(input_string):
    allowed_chars = set(string.digits + string.whitespace + string.ascii_letters + 'абinгдеёжзийклмнопрстуфхцчшщъыьэюяАБinГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    cleaned_string = ''.join(char for char in input_string if char in allowed_chars)
    return cleaned_string

def get_coordinates(address):
    address = address.replace(" ", "+")
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': api_key,
        'geocode': address,
        'format': 'json'
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        json_data = response.json()
        pos = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = pos.split()
        return float(lat), float(lon)
    else:
        return None

def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def raschet_new_piople(address, apartments):
    address_coords = get_coordinates(address)
    if not address_coords:
        return None, "Не удалось получить координаты для данного адреса."

    for idx, row in dataZastroy.iterrows():
        if pd.isna(row['Широта']) or pd.isna(row['Долгота']):
            address = row['Адрес строящегося комплекса']
            coordinates = get_coordinates(address)
            if coordinates:
                dataZastroy.at[idx, 'Широта'] = coordinates[0]
                dataZastroy.at[idx, 'Долгота'] = coordinates[1]

    for idx, row in organization_df.iterrows():
        if pd.isna(row['Широта']) or pd.isna(row['Долгота']):
            address = row['Адрес филиала']
            coordinates = get_coordinates(address)
            if coordinates:
                organization_df.at[idx, 'Широта'] = coordinates[0]
                organization_df.at[idx, 'Долгота'] = coordinates[1]

    min_distance = float('inf')
    closest_clinic = None

    for _, crow in organization_df.iterrows():
        clinic_coords = (crow['Широта'], crow['Долгота'])
        distance = haversine(address_coords, clinic_coords)
        if distance < min_distance:
            min_distance = distance
            closest_clinic = crow['Наименование медицинской организации']

    people = int(apartments) * 3  # Расчет людей на основе количества квартир
    return closest_clinic, people, None

def raschet_new_piopleDa():
    for idx, row in dataZastroy.iterrows():
        if pd.isna(row['Широта']) or pd.isna(row['Долгота']):
            address = row['Адрес строящегося комплекса']
            coordinates = get_coordinates(address)
            if coordinates:
                dataZastroy.at[idx, 'Широта'] = coordinates[0]
                dataZastroy.at[idx, 'Долгота'] = coordinates[1]

    for idx, row in organization_df.iterrows():
        if pd.isna(row['Широта']) or pd.isna(row['Долгота']):
            address = row['Адрес филиала']
            coordinates = get_coordinates(address)
            if coordinates:
                organization_df.at[idx, 'Широта'] = coordinates[0]
                organization_df.at[idx, 'Долгота'] = coordinates[1]

    results = []
    for idx, row in dataZastroy.iterrows():
        complex_coords = (row['Широта'], row['Долгота'])
        min_distance = float('inf')
        closest_clinic = None

        for _, crow in organization_df.iterrows():
            clinic_coords = (crow['Широта'], crow['Долгота'])
            distance = haversine(complex_coords, clinic_coords)
            if distance < min_distance:
                min_distance = distance
                closest_clinic = crow['Наименование медицинской организации']

        people = row['Кол-во квартир в доме'] * 3
        results.append((closest_clinic, people))

    clinic_population = {}
    for clinic, people in results:
        if clinic in clinic_population:
            clinic_population[clinic] += people
        else:
            clinic_population[clinic] = people

    return clinic_population



def calculate_all_clinics():
    results = []
    for selected in organization_df['Наименование медицинской организации'].unique():
        selected_df = organization_df[organization_df['Наименование медицинской организации'] == selected]
        selected_staff_df = organization_staff_df[organization_staff_df['Название медицинской организации'] == selected]

        selected_population = selected_df['Общая численность прикрепленного населения'].values[0]

        newPeople = raschet_new_piopleDa()
        selected_population = selected_population + newPeople.get(selected, 0)

        male_population = (selected_population * 0.62) * 0.52
        female_population = (selected_population * 0.62) * 0.48

        for _, row in normatives_df.iterrows():
            unit = row['Единица измерения']
            norm_people = row['Условие']
            recommended_staff = row['Рекомендуемые штатные нормативы (количество должностей)']

            if 'Женщин' in unit:
                relevant_population = female_population
            elif 'Взрослого население' in unit or 'Трудоспособное население' in unit:
                relevant_population = selected_population * 0.62
            elif 'ед.' in unit:
                relevant_population = selected_df['Количество пациенто-мест дневного стационара'].values[0]
            else:
                continue

            required_doctors = (relevant_population / norm_people) * recommended_staff

            position = row['Наименование должностей']
            current_staff = selected_staff_df[selected_staff_df['Наименование должностей'] == position]['Количество штатных единиц'].sum()

            if current_staff != 0:
                load_analysis = relevant_population / current_staff
            else:
                load_analysis = 0

            if load_analysis > 1:
                load_text = f'нагрузка превышена в {load_analysis / norm_people:.2f} раз'
            else:
                load_text = 'нагрузка в норме'

            deficit_or_surplus = current_staff - required_doctors

            if deficit_or_surplus > 0:
                deficit_or_surplus = f"Проффицит в {deficit_or_surplus:.2f} человек"
            else:
                deficit_or_surplus = f"Дифицит в {deficit_or_surplus:.2f} человек"

            results.append({
                'Поликлиника': selected,
                'Должность': position,
                'Необходимое количество врачей': f"{required_doctors:.2f}",
                'Текущее количество штатных единиц': f"{current_staff:.2f}",
                'Дефицит/Профицит': deficit_or_surplus,
                "Текущая нагрузка": load_text
            })

    return results

def calculated(selected, additional_population=0):
    selected_df = organization_df[organization_df['Наименование медицинской организации'] == selected]
    selected_staff_df = organization_staff_df[organization_staff_df['Название медицинской организации'] == selected]

    selected_population = selected_df['Общая численность прикрепленного населения'].values[0]
    selected_population += additional_population  # Учитываем дополнительное население

    male_population = (selected_population * 0.62) * 0.52
    female_population = (selected_population * 0.62) * 0.48

    results = []

    for _, row in normatives_df.iterrows():
        unit = row['Единица измерения']
        norm_people = row['Условие']
        recommended_staff = row['Рекомендуемые штатные нормативы (количество должностей)']

        if 'Женщин' in unit:
            relevant_population = female_population
        elif 'Взрослого население' in unit or 'Трудоспособное население' in unit:
            relevant_population = selected_population * 0.62
        elif 'ед.' in unit:
            relevant_population = selected_df['Количество пациенто-мест дневного стационара'].values[0]
        else:
            continue

        required_doctors = (relevant_population / norm_people) * recommended_staff

        position = row['Наименование должностей']
        current_staff = selected_staff_df[selected_staff_df['Наименование должностей'] == position]['Количество штатных единиц'].sum()

        if current_staff != 0:
            load_analysis = relevant_population / current_staff
        else:
            load_analysis = 0

        if load_analysis > 1:
            load_text = f'нагрузка превышена в {load_analysis / norm_people:.2f} раз'
        else:
            load_text = 'нагрузка в норме'

        deficit_or_surplus = current_staff - required_doctors

        if deficit_or_surplus > 0:
            deficit_or_surplus = f"Проффицит в {deficit_or_surplus:.2f} человек"
        else:
            deficit_or_surplus = f"Дифицит в {deficit_or_surplus:.2f} человек"
        
        results.append({
            'Должность': position,
            'Необходимое количество врачей': f"{required_doctors:.2f}",
            'Текущее количество штатных единиц': f"{current_staff:.2f}",
            'Дефицит/Профицит': deficit_or_surplus,
            "Текущая нагрузка": load_text
        })

    return results

def generate_recommendations(results):
    hire_recommendations = []
    fire_recommendations = []
    for row in results:
        deficit_or_surplus_text = row['Дефицит/Профицит']
        if "Дифицит" in deficit_or_surplus_text:
            deficit_value = float(deficit_or_surplus_text.split(' ')[2])
            hire_recommendations.append((row['Должность'], abs(deficit_value)))
        elif "Проффицит" in deficit_or_surplus_text:
            surplus_value = float(deficit_or_surplus_text.split(' ')[2])
            fire_recommendations.append((row['Должность'], surplus_value))
    return hire_recommendations, fire_recommendations


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/minister')
def minister():
    return render_template('minister_choice.html')

@app.route('/all_clinics')
def all_clinics():
    results = calculate_all_clinics()
    return render_template('all_clinics.html', results=results)

@app.route('/chief_doctor')
def chief_doctor():
    organizations = organization_df['Наименование медицинской организации'].unique()
    return render_template('chief_doctor.html', organizations=organizations)

@app.route('/chief_doctor_calculate', methods=['POST'])
def chief_doctor_calculate():
    selected = request.form['organization']
    results = calculated(selected)
    return render_template('chief_doctor.html', results=results, organizations=organization_df['Наименование медицинской организации'].unique(), selected=selected)

@app.route('/new_house')
def new_house():
    return render_template('new_house.html')

@app.route('/add_new_house', methods=['POST'])
def add_new_house():
    address = request.form['address']
    apartments = request.form['apartments']
    file = request.files['file']

    # Сохраняем загруженный файл, если он есть
    if file:
        file_path = os.path.join(path, file.filename)
        file.save(file_path)

    # Рекомендуемая поликлиника для нового дома и расчет людей
    closest_clinic, people, error = raschet_new_piople(address, apartments)
    if error:
        return render_template('new_house.html', error=error)
    
    message = f"Адрес: {address}, Количество квартир: {apartments}, Рекомендуемая поликлиника: {closest_clinic}, Число людей: {people}"

    # Получаем обновленные результаты для выбранной поликлиники
    results = calculated(closest_clinic, additional_population=people)
    return render_template('new_house.html', message=message, results=results, closest_clinic=closest_clinic)

@app.route('/recommendations', methods=['POST'])
def recommendations():
    results = json.loads(request.form['results'])
    hire_recommendations, fire_recommendations = generate_recommendations(results)
    return render_template('recommendations.html', hire_recommendations=hire_recommendations, fire_recommendations=fire_recommendations)

if __name__ == '__main__':
    app.run(debug=True)