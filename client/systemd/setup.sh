
BIN=$(dirname $(pwd))/generic_client.py
NAME=vaportrail
echo Please enter your vapor trail server name
read HOST

echo 'enter your systemd dir:'
echo 'gentoo'
echo '/usr/lib/systemd/system'
echo 'debian / ubuntu'
echo '/etc/systemd/system'
read SYSTEMD_DIR


echo '[Unit]' > $SYSTEMD_DIR/$NAME.service
echo 'Description=Vapor Trail client' >> $SYSTEMD_DIR/$NAME.service
echo '' >> $SYSTEMD_DIR/$NAME.service
echo '[Service]' >> $SYSTEMD_DIR/$NAME.service
echo ExecStart=$BIN $HOST >> $SYSTEMD_DIR/$NAME.service
echo '' >> $SYSTEMD_DIR/$NAME.service
echo '[Install]' >> $SYSTEMD_DIR/$NAME.service
echo 'WantedBy=multi-user.target' >> $SYSTEMD_DIR/$NAME.service

systemctl daemon-reload
systemctl enable $SYSTEMD_DIR/$NAME.service
systemctl start $SYSTEMD_DIR/$NAME



