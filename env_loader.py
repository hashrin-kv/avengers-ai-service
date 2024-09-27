from dotenv import dotenv_values, find_dotenv
import os


def get_environment_variable(key: str, default: str = "", value_type: type = str) -> any:
    """
    Get the environment variable value for the specified key.
    :param key: The key of the environment variable.
    :param default: The default value to return if the environment variable is not set.
    :param value_type: The type to cast the environment variable value to.
    :return: The casted value of the environment variable.
    """
    try:
        dotenv_path = find_dotenv()
        env_vars = dotenv_values(dotenv_path)

        os.environ.update(env_vars)

        env_value = os.getenv(key, default)

        if env_value is None or env_value == "":
            return default

        return value_type(env_value)
    except (ValueError, TypeError, Exception):
        return default
