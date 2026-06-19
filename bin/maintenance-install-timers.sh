#!/bin/bash

echo
echo "Installing Photo Kiosk maintenance timers..."
echo

sudo systemctl daemon-reload

sudo systemctl enable --now photo-kiosk-roster-refresh.timer
sudo systemctl enable --now photo-kiosk-gdrive-cleanup.timer
sudo systemctl enable --now photo-kiosk-local-cleanup.timer

echo
echo "Installed timers:"
echo

systemctl list-timers | grep photo-kiosk

echo
echo "Done."
echo
