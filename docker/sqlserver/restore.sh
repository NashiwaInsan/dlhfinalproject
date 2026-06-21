#!/bin/bash
# =====================================================================
# Dijalankan oleh container sqlserver_init.
# 1) Tunggu SQL Server siap menerima koneksi
# 2) Jika database belum ada -> restore <NAMA_DATABASE>.bak
# 3) Buat tabel dbo.OnlineOrderStream untuk faker penjualan online
# =====================================================================
set -e

SQLCMD="/opt/mssql-tools/bin/sqlcmd"
SERVER="sqlserver"
PASS="$MSSQL_PASSWORD"
DB="$MSSQL_DATABASE"
BAK="/var/opt/mssql/backup/${MSSQL_DATABASE}.bak"

# Nama LOGICAL file di dalam backup AdventureWorks (tanpa angka tahun).
# Diverifikasi dari output RESTORE FILELISTONLY: 'AdventureWorks' & 'AdventureWorks_log'.
LOGICAL_DATA="AdventureWorks"
LOGICAL_LOG="AdventureWorks_log"

echo ">> Menunggu SQL Server siap..."
for i in $(seq 1 60); do
  if $SQLCMD -S "$SERVER" -U sa -P "$PASS" -Q "SELECT 1" >/dev/null 2>&1; then
    echo ">> SQL Server SIAP."
    break
  fi
  echo "   ...belum siap ($i/60)"; sleep 3
done

# Cek apakah database sudah ada (biar restore tidak diulang tiap restart)
EXISTS=$($SQLCMD -S "$SERVER" -U sa -P "$PASS" -h -1 -W \
  -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM sys.databases WHERE name='$DB'")

if [ "$EXISTS" = "1" ]; then
  echo ">> Database $DB sudah ada. Lewati restore."
else
  echo ">> Logical file names di dalam backup (untuk verifikasi):"
  $SQLCMD -S "$SERVER" -U sa -P "$PASS" -Q "RESTORE FILELISTONLY FROM DISK='$BAK'"

  echo ">> Restore database $DB ..."
  $SQLCMD -S "$SERVER" -U sa -P "$PASS" -Q "
    RESTORE DATABASE [$DB] FROM DISK='$BAK'
    WITH MOVE '$LOGICAL_DATA' TO '/var/opt/mssql/data/$DB.mdf',
         MOVE '$LOGICAL_LOG'  TO '/var/opt/mssql/data/${DB}_log.ldf',
         REPLACE, RECOVERY;"
  echo ">> Restore selesai."
fi

echo ">> Membuat tabel stream untuk faker online sales..."
$SQLCMD -S "$SERVER" -U sa -P "$PASS" -d "$DB" -i /init/online_stream.sql

echo ">> INIT SELESAI. SQL Server siap dipakai."
