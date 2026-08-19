# Архитектура Taxi-manager

Этот каталог содержит небольшую C4-модель проекта в нотации Structurizr DSL.

## Структура

- `workspace.dsl` — точка входа Structurizr;
- `model/taxi-manager.dsl` — элементы и связи работающего приложения;
- `views/taxi-manager.dsl` — C1, C2 и сценарий геокодирования;
- `model/observability.dsl` и `views/observability.dsl` — заготовки для наблюдаемости;
- `model/ci-cd.dsl` и `views/ci-cd.dsl` — заготовки для CI/CD;
- `views/styles.dsl` — общие стили диаграмм.

Наблюдаемость и CI/CD подключены как пустые фрагменты. Пока они не заполнены, они не добавляют элементы и диаграммы в текущую модель.

## Запуск

Добавьте в основной `Makefile` строку:

```makefile
include Makefile.structurizr
```

После этого доступны команды:

```bash
make architecture
make architecture-status
make architecture-down
```

Откройте <http://127.0.0.1:8085>.

Без подключения файла к основному `Makefile` запуск возможен так:

```bash
make -f Makefile.structurizr architecture
```

Порт можно изменить без редактирования Compose-файла:

```bash
STRUCTURIZR_PORT=8090 make architecture
```
