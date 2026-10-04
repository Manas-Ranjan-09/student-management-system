#!/usr/bin/env bash
exec gunicorn config.wsgi:application
