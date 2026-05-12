import logging
from itertools import count
from queue import PriorityQueue
from threading import Thread
from traceback import format_exception

from django.tasks.backends.base import BaseTaskBackend
from django.tasks.base import TaskContext, TaskError, TaskResult, TaskResultStatus
from django.tasks.signals import task_enqueued, task_finished, task_started
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.json import normalize_json


logger = logging.getLogger(__name__)


class ThreadQueueBackend(BaseTaskBackend):
    supports_async_task = False
    supports_defer = False
    supports_get_result = False
    supports_priority = True

    def __init__(self, alias, params):
        super().__init__(alias, params)
        self.worker_id = get_random_string(32)
        self._queue = PriorityQueue()
        self._sequence = count()
        self._worker = Thread(
            target=self._worker_loop,
            name=f"task-backend-{alias}",
            daemon=True,
        )
        self._worker.start()

    def enqueue(self, task, args, kwargs):
        self.validate_task(task)

        task_result = TaskResult(
            task=task,
            id=get_random_string(32),
            status=TaskResultStatus.READY,
            enqueued_at=timezone.now(),
            started_at=None,
            last_attempted_at=None,
            finished_at=None,
            args=args,
            kwargs=kwargs,
            backend=self.alias,
            errors=[],
            worker_ids=[],
        )

        task_enqueued.send(type(self), task_result=task_result)

        # Чем больше priority, тем раньше выполняем.
        self._queue.put((-task.priority, next(self._sequence), task_result))
        return task_result

    def _worker_loop(self):
        while True:
            _, _, task_result = self._queue.get()
            try:
                self._execute_task(task_result)
            except BaseException:
                logger.exception("Task worker loop crashed while executing a task")
            finally:
                self._queue.task_done()

    def _execute_task(self, task_result):
        task = task_result.task
        task_start_time = timezone.now()

        object.__setattr__(task_result, "status", TaskResultStatus.RUNNING)
        object.__setattr__(task_result, "started_at", task_start_time)
        object.__setattr__(task_result, "last_attempted_at", task_start_time)
        task_result.worker_ids.append(self.worker_id)

        task_started.send(sender=type(self), task_result=task_result)

        try:
            if task.takes_context:
                raw_return_value = task.call(
                    TaskContext(task_result=task_result),
                    *task_result.args,
                    **task_result.kwargs,
                )
            else:
                raw_return_value = task.call(*task_result.args, **task_result.kwargs)

            object.__setattr__(
                task_result,
                "_return_value",
                normalize_json(raw_return_value),
            )
        except KeyboardInterrupt:
            raise
        except BaseException as e:
            object.__setattr__(task_result, "finished_at", timezone.now())
            exception_type = type(e)
            task_result.errors.append(
                TaskError(
                    exception_class_path=(
                        f"{exception_type.__module__}.{exception_type.__qualname__}"
                    ),
                    traceback="".join(format_exception(e)),
                )
            )
            object.__setattr__(task_result, "status", TaskResultStatus.FAILED)
            task_finished.send(type(self), task_result=task_result)
        else:
            object.__setattr__(task_result, "finished_at", timezone.now())
            object.__setattr__(task_result, "status", TaskResultStatus.SUCCESSFUL)
            task_finished.send(type(self), task_result=task_result)