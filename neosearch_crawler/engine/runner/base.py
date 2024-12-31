import ray
from datetime import datetime
from uuid import uuid4
from threading import Thread
from typing import Callable


class DAGBuilder():
    """
    A class to manage DAG creation and execution for methods within a class.
    """
    def __init__(self, dag_id = None, start_date=None, schedule_interval=None):
        if dag_id is None:
            dag_id = str(uuid4())
        self.dag_id = dag_id
        self.start_date = start_date or datetime.now()
        self.schedule_interval = schedule_interval
        self.steps: dict[int, list] = {}
        self.dag = None


    def register_step(self, step_func, index):
        """Register a step function with a specific index."""
        if index not in self.steps:
            self.steps[index] = []
        self.steps[index].append(step_func)


    def build_dag(self) -> list[list[Callable]]:
        """Build the DAG based on the registered steps."""

        if self.start_date is None:
            self.start_date = datetime.now()

        task_lists = []
        task_map = {}

        # Set dependencies
        for i in range(len(sorted(self.steps.keys())) - 1):
            current_steps = self.steps[sorted(self.steps.keys())[i]]
            next_steps = self.steps[sorted(self.steps.keys())[i + 1]]

            task_list = []
            for current_step in current_steps:
                for next_step in next_steps:
                    # does not support circular dependencies
                    if next_step in task_map:
                        raise ValueError("Circular dependencies are not supported.")

                if current_step not in task_map:
                    task_map[current_step] = []
                    task_list.append(current_step)
                task_map[current_step].append(next_step)
            task_lists.append(task_list)

        return task_lists


    def _create_ray_task(self, step_func):
        """Wrap a step function to execute within a Ray worker."""
        @ray.remote
        def ray_task(*args, **kwargs):
            return step_func(*args, **kwargs)

        def task(*args, **kwargs):
            return ray.get(ray_task.remote(*args, **kwargs))

        return task



class BaseRunner(DAGBuilder):
    """Base runner class for creating DAGs with @step decorators."""

    def __init__(self, dag_id=None, start_date=datetime.now(), schedule_interval='@once'):
        super().__init__(dag_id, start_date, schedule_interval)

    def __init_subclass__(cls, **kwargs):
        """Automatically register methods with @step decorators."""
        # super().__init_subclass__(**kwargs)
        for name, method in cls.__dict__.items():
            if hasattr(method, '_step_index'):
                cls._register_method(method, name)


    def run_dag(self):
        task_lists = self.build_dag()

        # create threads for each task list
        for task_list in task_lists:
            threads = [ Thread(target=task) for task in task_list ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()


    def run_dag_ray(self):
        task_lists = self.build_dag()

        # create ray tasks for each task list
        for task_list in task_lists:
            ray_tasks = [ self._create_ray_task(task) for task in task_list ]
            ray.get([ task.remote() for task in ray_tasks ])


    @classmethod
    def _register_method(cls, method, name):
        index = getattr(method, '_step_index', None)
        if index is not None:
            instance = cls()
            instance.register_step(getattr(instance, method.__name__), index)


    @classmethod
    def _init_ray(cls):
        # Initialize Ray
        ray.init(ignore_reinit_error=True)
