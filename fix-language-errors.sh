#!/bin/bash

# Function to fix language errors in a file
fix_language_file() {
    local file=$1
    echo "Fixing language errors in $file"
    
    # Replace all occurrences of createLocalizedLink with the type-casted version
    sed -i 's/createLocalizedLink(\([^,]*\), lang)/createLocalizedLink(\1, lang as any)/g' "$file"
}

# Process all sport pages
for file in client/src/pages/sports/*.tsx; do
    fix_language_file "$file"
done

echo "All files fixed!"