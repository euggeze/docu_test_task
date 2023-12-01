import datetime


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def get_json_data(tasks: list, columns: list) -> str | dict | list:
    if len(tasks) == 0:
        return 'Task not found'
    if len(tasks) == 1:
        return {column: value for column, value in zip(columns, tasks[0])}
    result_list = []
    for task in tasks:
        result_list.append({column: value for column, value in zip(columns, task)})
    return result_list