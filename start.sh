#!/usr/bin/env bash
if [ -d "backend" ]; then
  cd backend
fi
exec gunicorn config.wsgi:application
