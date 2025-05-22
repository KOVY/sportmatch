#!/bin/bash
sed -i 's/requireAuth/authenticateUser/g' server/routes/substitutes.ts
sed -i 's/AuthenticatedRequest/AuthRequest/g' server/routes/substitutes.ts
chmod +x fix_substitutes.sh
./fix_substitutes.sh
