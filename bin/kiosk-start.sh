#!/bin/bash

sudo systemctl start photo-kiosk.service
sudo systemctl status photo-kiosk.service --no-pager
