"""

  Environment handler for file serializer

  Used to de-reference settings that contain environment variables

"""
import ast
import os
import re
from configparser import ConfigParser
from os.path import realpath, isdir, join, isfile

from nio.properties.base import ENVIRONMENT_VAR


class NIOEnvironment(object):

    _root = os.getcwd()
    _conf_file = ''
    _env_file = ''
    _env_vars = {}

    @classmethod
    def set_environment(cls, root, env_file=''):
        """ Sets environment

        Args:
            root (str): working directory
            env_file (str): path to file containing envrironment variables
        """
        if not isfile(root):
            root = realpath(root)
        if env_file and not isfile(env_file):
            # They specified a environment file and it's not already a file
            env_file = join(root, env_file)

        cls._root = root
        # making project's root directory the working/current directory
        if not os.path.isdir(root):
            os.makedirs(root)
        os.chdir(root)

        cls._env_file = env_file
        if env_file:
            cls._load_env_vars()

    @classmethod
    def replace_setting(cls, value, attempt_conversion=True):

        # A replace function to pass to the regex substitution
        def repl(m):
            return str(cls.get_variable(m.group(1)))

        if isinstance(value, str):
            # Find out if the entire string is a single environment variable,
            match = ENVIRONMENT_VAR.fullmatch(value)
            if match is not None:
                # if so, then try to convert it or eval it
                var_name = match.group(1)
                value = cls.get_variable(var_name)
                if attempt_conversion:
                    value = cls._attempt_conversion(value)
            else:
                # otherwise, just replace the environment variable expression
                # with the environment variable value
                value = re.sub(ENVIRONMENT_VAR, repl, value)
        return value

    @staticmethod
    def _attempt_conversion(value):
        try:
            value = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # if literal_eval fails, return value as is
            pass
        return value

    @classmethod
    def _load_env_vars(cls):

        # set strict flag to false in ConfigParser to avoid having duplicate
        # keys crash the read. duplicate keys are discouraged but behavior
        # is well defined: the second value (top to bottom) is used.
        config = ConfigParser(strict=False)
        config.read(cls._env_file)
        try:
            cls._env_vars = config['vars']
        except KeyError:
            pass

    @classmethod
    def get_variable(cls, name):
        """Returns environment variables
        Arg:
            name: Name of the variable to get

        Returns: mixed
        """

        # Strip name
        name = name.strip()

        # Get from config
        value = cls._env_vars.get(name, "[[{}]]".format(name))

        # if asking for PROJECT_ROOT and it does not contain
        # a valid value then provide it from environment
        if name == "PROJECT_ROOT" and not isdir(value):
            value = cls.get_root()

        # Allow actual environment variables to over-write values
        return os.getenv(name, value)

    @classmethod
    def get_root(cls):
        """ Returns the project root path.

        This is typically the path where the nio.conf file exists. Or the path
        specified by the -r option on the executable.
        """
        return cls._root
