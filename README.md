[![Build Status](https://travis-ci.org/anegramotnov/firebird_test_framework.svg?branch=master)](https://travis-ci.org/anegramotnov/firebird_test_framework)

# Прототип тестового фреймворка для хранимых процедур Firebird

Позволяет изолированно протестировать хранимую процедуру, подменяя 
другие используемые ей процедуры заглушками (mock), которые возвращают
заранее определенные значения.

В планах:

* Реализовать mock таблиц
* Упростить API
* Добавить примеры использования (работающие примеры содержали конфиденциальную
информацию и в публичный репозиторий не вошли)

### Запуск тестовых примеров

В данный момент, отсутствуют:
```
python -m pytest examples

```

### Тесты:
```
python -m pytest tests
```

### Pylint
```
pylint ../firebird_test_framework
```

### Flake8
```
flake8 .
```
