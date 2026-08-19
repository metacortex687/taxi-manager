systemContext taxiManager "TaxiManagerSystemContext" {
    title "C1 — Контекст системы Taxi-manager"
    description "Показывает пользователей Taxi-manager и внешние программные системы. Тип клиента телеметрии пока не определён."
    include *
    autoLayout lr
}

container taxiManager "TaxiManagerContainers" {
    title "C2 — Контейнеры работающего приложения Taxi-manager"
    description "Логическое представление приложений и хранилища. Наблюдаемость, CI/CD и детали развёртывания показываются в отдельных представлениях."
    include *
    autoLayout tb 300 250
}

dynamic taxiManager "TaxiManagerGeocodingFlow" {
    title "Геокодирование адреса через фоновое задание"
    description "LocationIQ взаимодействует только с фоновым обработчиком заданий и не имеет прямого доступа к PostgreSQL."
    1: taxiManager.djangoWsgi -> taxiManager.database "Сохраняет задание геокодирования в очереди"
    2: taxiManager.taskWorker -> taxiManager.database "Получает задание из очереди"
    3: taxiManager.taskWorker -> locationIq "Отправляет запрос и получает результат геокодирования"
    4: taxiManager.taskWorker -> taxiManager.database "Сохраняет результат геокодирования"
    autoLayout lr
}

