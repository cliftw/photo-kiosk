#!/bin/bash

echo
echo "Restarting Photo Kiosk..."
echo

sudo systemctl restart photo-kiosk.service

sleep 1

sudo systemctl status photo-kiosk.service --no-pager

echo
echo "Done."
echo
