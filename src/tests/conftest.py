
# On Windows, if needed:
# from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
# set_event_loop_policy(WindowsSelectorEventLoopPolicy())

pytest_plugins = [
    "src.tests.fixtures.db_fixture",
    "src.tests.fixtures.client_fixture",
]
