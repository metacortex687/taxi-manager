# Архитектура Taxi-manager

Этот каталог содержит C4-модель проекта в нотации Structurizr DSL. Основные архитектурные уровни — диаграмма контекста системы C1 и диаграммы контейнеров C2; динамические представления поясняют ключевые сценарии, а deployment views — варианты физического развёртывания по мере роста нагрузки.

## Структура

- `workspace.dsl` — точка входа Structurizr;
- `model/taxi-manager.dsl` — элементы и связи работающего приложения;
- `model/notifications.dsl` и `views/notifications.dsl` — подключаемая система уведомлений менеджеров, её C1, C2 и сценарий формирования уведомления;
- `model/observability.dsl` и `views/observability.dsl` — платформа наблюдаемости и её представления;
- `model/ci-cd.dsl` и `views/ci-cd.dsl` — Jenkins-конвейер, его представления и сценарий выполнения;
- `model/deployment.dsl` и `views/deployment.dsl` — варианты физического развёртывания;
- `views/taxi-manager.dsl` — C1, C2 и ключевые сценарии основной системы;
- `views/styles.dsl` — общие стили диаграмм.

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
make architecture-restart # перезапуск после внесения изменения в DSL файлы C4
make architecture-export-png # обновляет картинки в docs/images/c4

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
