# -*- coding: utf-8 -*-
import os
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

bind='0.0.0.0:8080'

# multiple processing
workers= multiprocessing.cpu_count() * 2 + 1
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

# x_forwarded
x_forwarded_for_header = 'X-FORWARDED-FOR'

# other config
backlog=2048
debug=True
proc_name='gunicorn.pid'
pidfile='/home/thdice/log/gunicorn.pid'
logfile='/home/thdice/log/debug.log'
loglevel='debug'
