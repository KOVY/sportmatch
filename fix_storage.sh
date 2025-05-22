#!/bin/bash
# Tento skript opraví přebytečnou závorku v server/storage.ts
sed -i '395d' server/storage.ts
chmod +x fix_storage.sh
./fix_storage.sh
