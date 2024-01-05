from django.db import connection
from django.db import reset_queries
from functools import wraps

# Decorator used for database optimalization purposes
def database_debug(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        results = func(*args, **kwargs)
        query_info = connection.queries
        print("function_name: {}".format(func.__name__))
        print("query_count: {}".format(len(query_info)))
        queries = ["{}\n".format(query["sql"]) for query in query_info]
        print("queries: \n{}".format("".join(queries)))
        return results

    return inner_func
