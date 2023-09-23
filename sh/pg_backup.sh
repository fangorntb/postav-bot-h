HOST="localhost"
PORT="5432"
USERNAME="your_username"
DATABASE="your_database"
BACKUP_DIR="/home/data/pg-backups/"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="${BACKUP_DIR}/${DATABASE}_${TIMESTAMP}.sql"
pg_dump --host=${HOST} --port=${PORT} --username=${USERNAME} --format=plain --file=${FILENAME} ${DATABASE}
if [ $? -eq 0 ]; then
  echo "Резервная копия успешно создана: ${FILENAME}"
else
  echo "Ошибка при создании резервной копии."
fi
