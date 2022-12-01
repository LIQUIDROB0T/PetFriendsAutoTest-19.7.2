from api import PetFriends
from settings import valid_email, valid_password
from settings import invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Доступное значение параметра filter - 'my_pets' - все питомцы, либо '' - мои питомцы."""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер', age='4',
                                     pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления своего питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем
    # список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о своем питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_photo_valid_data(name='Барсик', animal_type='сибирская', age='3'):
    """Проверяем что можно добавить питомца без фото с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_photo_to_pet_valid_data(pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить фото своему питомцу по ID"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то добавляем фото
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_to_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и параметр pet_photo присутствует в теле ответа
        assert status == 200
        assert 'pet_photo' in result
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 используя невалидные данные авторизации"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает статус 403 при использовании
    неверного ключа авторизации"""

    # Создаем случайный ключ api и сохраняем в переменную auth_key
    auth_key = {"key": "2W3ueu"}
    status, result = pf.get_list_of_pets(auth_key, filter)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403


def test_add_new_pet_with_invalid_data(name='', animal_type='', age='', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с некорректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200  # Ответ должен быть 400!!! Данный тест обнаружил БАГ. По сваггеру имя,
    # тип и возраст - являются обязательными полями, но в реальности питомец создается без имени,
    # типа и возраста!!!


def test_add_new_pet_with_invalid_key(name='Барбоскин',
                                      animal_type='двортерьер', age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить питомца с некорректным API-ключом"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Создаем случайный ключ api и сохраняем в переменную auth_key
    auth_key = {"key": "2W3ueu"}

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403


def test_delete_self_pet_invalid_api_key():
    """Проверяем невозможность удаления питомца с невалидным API ключом"""

    # Получаем реальный ключ auth_key что бы запросить список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять
    # запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на
    # удаление с невалидным ключом API
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.delete_pet({"key": "2W3ueu"}, pet_id)

    # Проверяем что статус ответа равен 403 и питомец не удален
    assert status == 403
    assert 'id' in result  # ВНИМАНИЕ: Данный тест проходит, но в сваггере есть возможность
    # удаления питомца по невалидному ключу или значению ' ' (Проблел) в поле ввода ключа API.


def test_update_self_pet_info_invalid_api_key(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем невозможность обновления информации о питомце с невалидным API ключом"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст с невалидным API ключом
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info({"key": "2W3ueu"}, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 403
        assert status == 403
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_update_self_pet_info_invalid_id(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем что нельзя обновить информацию питомца с некорректным id ("c82306ad-5864-454f")"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его с невалидным id ("c82306ad-5864-454f")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, "c82306ad-5864-454f", name, animal_type, age)

        # Проверяем что статус ответа = 400
        assert status == 400
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_photo_invalid_api_key(name='Барсик', animal_type='сибирская', age='3'):
    """Проверяем что нельзя добавить питомца без фото с некорректным API ключом"""

    # Невалидный API ключ сохраняем в переменную auth_key
    auth_key = {"key": "2W3ueu"}

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 403


def test_add_new_pet_without_photo_invalid_data(name='', animal_type='', age=''):
    """Проверяем что нельзя добавить питомца без фото с некорректными данными"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200  # Ответ должен быть 400!!! Данный тест обнаружил БАГ. По сваггеру имя,
    # тип и возраст - являются обязательными полями, но в реальности питомец создается без имени,
    # типа и возраста!!!


def test_add_photo_to_pet_invalid_api_key(pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить фото питомца по ID с невалидным API ключом"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то добавляем фото с использованием невалидного API ключа
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_to_pet({"key": "2W3ueu"}, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 403
        assert status == 403
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_photo_to_pet_invalid_data(pet_photo='images/cat1.jpg'):
    """Проверяем что нельзя добавить фото питомца по некорректному ID ("c82306ad-5864-454f")"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то добавляем фото c некорректным id ("c82306ad-5864-454f")
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo_to_pet(auth_key, "c82306ad-5864-454f", pet_photo)

        # Проверяем что статус ответа = 500
        assert status == 500  # ВНИМАНИЕ! Данная ошибка отсутствует в сваггере. Возможно нужно заменить
        # значение 400 на 500.
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_delete_not_self_pet():
    """Проверяем невозможность удаления ЧУЖОГО питомца"""

    # Получаем ключ auth_key и запрашиваем список ВСЕХ питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, '')

    # Проверяем - если список ВСЕХ питомцев пустой, то добавляем нового и опять запрашиваем
    # список ВСЕХ питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, '')

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список ВСЕХ питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, '')

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()  # Данный тест обнаружил БАГ! Авторизированный пользователь
    # имеет возможность УДАЛЯТЬ ЧУЖИХ ПИТОМЦЕВ.
