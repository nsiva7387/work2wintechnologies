#!/usr/bin/env python
"""Django management entry point for the Work2Win student portal."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "work2win.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
