

Create the service file
sudo emacs /etc/systemd/system/photo-kiosk.service

Contents:

[Unit]
Description=Hilhi Engineering Photo Kiosk
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=cliftw
WorkingDirectory=/home/cliftw/photo-kiosk

ExecStart=/home/cliftw/photo-kiosk/.venv/bin/python \
          /home/cliftw/photo-kiosk/test_workflow_kiosk.py

Restart=always
RestartSec=5

StandardOutput=append:/home/cliftw/photo-kiosk/logs/systemd-output.log
StandardError=append:/home/cliftw/photo-kiosk/logs/systemd-error.log

[Install]
WantedBy=multi-user.target
Activate it
sudo systemctl daemon-reload
sudo systemctl enable photo-kiosk.service
sudo systemctl start photo-kiosk.service
Useful commands

Status:

sudo systemctl status photo-kiosk.service

Restart:

sudo systemctl restart photo-kiosk.service

Stop:

sudo systemctl stop photo-kiosk.service

Start:

sudo systemctl start photo-kiosk.service

Disable autostart:

sudo systemctl disable photo-kiosk.service
