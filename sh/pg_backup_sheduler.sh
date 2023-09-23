BACKUP_SCRIPT="/path/to/your/script.sh"

(crontab -l 2>/dev/null; echo "0 2 * * * ${BACKUP_SCRIPT}") | crontab -

echo "Задача резервного копирования запланирована."
