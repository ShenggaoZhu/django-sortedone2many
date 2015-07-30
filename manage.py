#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    Base_Dir = os.path.dirname(os.path.abspath(__file__))

    # test modified django:
    # sys.path.insert(0, os.path.join(os.path.dirname(Base_Dir), 'django'))

    sys.path.insert(0, Base_Dir)
    os.environ["DJANGO_SETTINGS_MODULE"] = "test_project.settings"
#     sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
