/**
 * Import scraped dat sportovišť z JSON souboru do databáze
 * 
 * Tento skript načte data získaná scraperem facilities.json a importuje je do databáze
 * s funkcí deduplikace a správného přiřazení sportů
 */

import fs from 'fs';
import { db } from './server/db.js';
import { eq, desc, inArray } from 'drizzle-orm';
import { 
  facilities, 
  sports, 
  facilitySports,
  facilityImports 
} from './shared/schema-sports-facilities.js';

// Mapování kódů sportů na jejich ID v databázi
const SPORT_CODES = {
  "TEN": { name: "Tenis", icon: "tennis", color: "#4caf50" },
  "BAD": { name: "Badminton", icon: "badminton", color: "#8bc34a" },
  "SQU": { name: "Squash", icon: "squash", color: "#cddc39" },
  "PAD": { name: "Padel", icon: "padel", color: "#ffeb3b" },
  "TTP": { name: "Stolní tenis", icon: "table-tennis", color: "#ffc107" },
  "VOL": { name: "Volejbal", icon: "volleyball", color: "#ff9800" },
  "FOO": { name: "Fotbal", icon: "football", color: "#ff5722" },
  "BAS": { name: "Basketbal", icon: "basketball", color: "#795548" },
  "SWI": { name: "Plavání", icon: "swimming", color: "#2196f3" },
  "ICE": { name: "Hokej", icon: "ice-hockey", color: "#9c27b0" },
  "GOL": { name: "Golf", icon: "golf", color: "#3f51b5" },
  "FIT": { name: "Fitness", icon: "fitness", color: "#673ab7" },
  "ATH": { name: "Atletika", icon: "athletics", color: "#e91e63" },
  "BVO": { name: "Plážový volejbal", icon: "beach-volleyball", color: "#ff6d00" },
  "BOW": { name: "Bowling", icon: "bowling", color: "#607d8b" },
};

/**
 * Hlavní funkce importu dat
 */
async function importScrapedFacilitiesData(jsonFilePath = './facilities.json') {
  try {
    console.log(`Starting import of scraped facilities from ${jsonFilePath}...`);
    
    // Načtení dat ze souboru
    const rawData = fs.readFileSync(jsonFilePath, 'utf8');
    const data = JSON.parse(rawData);
    
    if (!data || !data.facilities || !Array.isArray(data.facilities)) {
      console.error("Invalid data format in JSON file");
      return;
    }
    
    const facilitiesData = data.facilities;
    console.log(`Found ${facilitiesData.length} facilities to import`);
    
    // Příprava sportů
    await prepareAllSports();
    
    // Získání existujících sportů z databáze
    const existingSports = await db.select().from(sports);
    const sportCodeToId = {};
    
    for (const sport of existingSports) {
      for (const [code, info] of Object.entries(SPORT_CODES)) {
        if (info.name === sport.name) {
          sportCodeToId[code] = sport.id;
          break;
        }
      }
    }
    
    // Import dat sportovišť
    let importedCount = 0;
    let updatedCount = 0;
    let skippedCount = 0;
    let errorCount = 0;
    
    for (const facilityData of facilitiesData) {
      try {
        // Vyhodnocení, zda je sportoviště již importováno (na základě URL)
        let isUpdate = false;
        const existingImport = facilityData.sourceUrl 
          ? await db.select()
              .from(facilityImports)
              .where(eq(facilityImports.sourceUrl, facilityData.sourceUrl))
              .limit(1)
          : [];
        
        // Kontrola, zda sportoviště již neexistuje (na základě názvu a adresy)
        const existingFacility = await db.select()
          .from(facilities)
          .where(eq(facilities.name, facilityData.name))
          .limit(1);
          
        // Pokud již existuje, aktualizujeme stávající záznam
        if (existingFacility.length > 0 && existingImport.length > 0) {
          const facilityId = existingFacility[0].id;
          const importId = existingImport[0].id;
          
          console.log(`Updating facility "${facilityData.name}" (ID: ${facilityId})`);
          
          // Příprava dat pro aktualizaci
          const facilityUpdateData = {
            description: facilityData.description || existingFacility[0].description || "",
            address: facilityData.address || existingFacility[0].address || "",
            city: facilityData.city || existingFacility[0].city || "",
            postalCode: facilityData.postalCode || existingFacility[0].postalCode || "",
            country: facilityData.country || existingFacility[0].country || "Czech Republic",
            phone: facilityData.phone || existingFacility[0].phone || "",
            email: facilityData.email || existingFacility[0].email || "",
            website: facilityData.website || existingFacility[0].website || "",
            openingHours: facilityData.openingHours || existingFacility[0].openingHours || "",
            amenities: Array.isArray(facilityData.amenities) ? facilityData.amenities.join(',') : (existingFacility[0].amenities || ""),
            hasParking: facilityData.hasParking !== undefined ? facilityData.hasParking : existingFacility[0].hasParking || false,
            isIndoor: facilityData.isIndoor !== undefined ? facilityData.isIndoor : existingFacility[0].isIndoor || false,
            isOutdoor: facilityData.isOutdoor !== undefined ? facilityData.isOutdoor : existingFacility[0].isOutdoor || false,
            images: Array.isArray(facilityData.images) && facilityData.images.length > 0 ? 
              facilityData.images.join(',') : existingFacility[0].images || "",
            updatedAt: new Date()
          };
          
          // Aktualizace sportoviště
          await db.update(facilities)
            .set(facilityUpdateData)
            .where(eq(facilities.id, facilityId));
          
          // Aktualizace importu
          await db.update(facilityImports)
            .set({
              dataJson: JSON.stringify(facilityData),
              status: "updated",
              processedAt: new Date(),
              updatedAt: new Date()
            })
            .where(eq(facilityImports.id, importId));
          
          // Aktualizace sportů
          if (Array.isArray(facilityData.sports) && facilityData.sports.length > 0) {
            for (const sportCode of facilityData.sports) {
              const sportId = sportCodeToId[sportCode];
              
              if (sportId) {
                // Kontrola, zda sport již není přiřazen
                const existingSport = await db.select()
                  .from(facilitySports)
                  .where(eq(facilitySports.facilityId, facilityId))
                  .where(eq(facilitySports.sportId, sportId))
                  .limit(1);
                
                if (existingSport.length === 0) {
                  await db.insert(facilitySports)
                    .values({
                      facilityId: facilityId,
                      sportId: sportId,
                      isMainSport: facilityData.sports.indexOf(sportCode) === 0, // První sport je hlavní
                    })
                    .onConflictDoNothing();
                    
                  console.log(`  - Added sport "${sportCode}" to facility`);
                }
              }
            }
          }
          
          updatedCount++;
          isUpdate = true;
        } 
        // Pokud sportoviště neexistuje, vytvoříme nový záznam
        else if (existingFacility.length === 0) {
          // Příprava dat pro vložení
          const facilityInsertData = {
            name: facilityData.name,
            description: facilityData.description || "",
            address: facilityData.address || "",
            city: facilityData.city || "",
            postalCode: facilityData.postalCode || "",
            country: facilityData.country || "Czech Republic",
            phone: facilityData.phone || "",
            email: facilityData.email || "",
            website: facilityData.website || "",
            latitude: facilityData.latitude || null,
            longitude: facilityData.longitude || null,
            openingHours: facilityData.openingHours || "",
            amenities: Array.isArray(facilityData.amenities) ? facilityData.amenities.join(',') : "",
            hasParking: facilityData.hasParking || false,
            isIndoor: facilityData.isIndoor || false,
            isOutdoor: facilityData.isOutdoor || false,
            images: Array.isArray(facilityData.images) ? facilityData.images.join(',') : "",
            maxCapacity: facilityData.maxCapacity || null,
            pricing: facilityData.pricing || null,
            courtsCount: facilityData.courtsCount || null,
            acceptsFitnessTokens: facilityData.acceptsFitnessTokens !== false, // defaultně true
          };
          
          // Vložení sportoviště do databáze
          const [newFacility] = await db.insert(facilities)
            .values(facilityInsertData)
            .returning();
            
          console.log(`Imported facility: "${newFacility.name}" (ID: ${newFacility.id})`);
          
          // Vytvoření záznamu o importu
          const importRecord = {
            source: facilityData.source || "scraper",
            sourceId: facilityData.sourceId || String(newFacility.id),
            sourceUrl: facilityData.sourceUrl || "",
            dataJson: JSON.stringify(facilityData),
            status: "imported",
            processedAt: new Date()
          };
          
          await db.insert(facilityImports)
            .values(importRecord)
            .onConflictDoNothing();
          
          // Přidání sportů ke sportovišti
          if (Array.isArray(facilityData.sports) && facilityData.sports.length > 0) {
            for (const sportCode of facilityData.sports) {
              const sportId = sportCodeToId[sportCode];
              
              if (sportId) {
                await db.insert(facilitySports)
                  .values({
                    facilityId: newFacility.id,
                    sportId: sportId,
                    isMainSport: facilityData.sports.indexOf(sportCode) === 0, // První sport je hlavní
                  })
                  .onConflictDoNothing();
                  
                console.log(`  - Added sport "${sportCode}" to facility`);
              }
            }
          }
          
          importedCount++;
        } else {
          console.log(`Skipping facility "${facilityData.name}" (already exists and no source URL match)`);
          skippedCount++;
        }
      } catch (facilityError) {
        console.error(`Error importing facility "${facilityData.name}":`, facilityError);
        errorCount++;
      }
    }
    
    console.log("\nImport completed:");
    console.log(`- Newly imported: ${importedCount} facilities`);
    console.log(`- Updated: ${updatedCount} facilities`);
    console.log(`- Skipped: ${skippedCount} facilities (already exist)`);
    console.log(`- Errors: ${errorCount} facilities`);
    
  } catch (error) {
    console.error("Error during import:", error);
  }
}

/**
 * Příprava všech sportů v databázi
 */
async function prepareAllSports() {
  try {
    console.log("Ensuring all required sports exist in the database...");
    
    for (const [code, sportInfo] of Object.entries(SPORT_CODES)) {
      // Kontrola, zda sport již existuje
      const existingSport = await db.select()
        .from(sports)
        .where(eq(sports.name, sportInfo.name))
        .limit(1);
        
      if (existingSport.length === 0) {
        // Sport neexistuje, vytvoříme ho
        const [newSport] = await db.insert(sports)
          .values({
            name: sportInfo.name,
            description: `${sportInfo.name} sport`,
            icon: sportInfo.icon,
            color: sportInfo.color,
            category: "sports",
            popularity: 1,
          })
          .returning();
          
        console.log(`Created sport: ${newSport.name} (ID: ${newSport.id})`);
      } else {
        console.log(`Sport already exists: ${sportInfo.name}`);
      }
    }
    
    console.log("All sports prepared successfully!");
  } catch (error) {
    console.error("Error preparing sports:", error);
    throw error;
  }
}

// Spuštění hlavní funkce s volitelným argumentem pro cestu k souboru
const args = process.argv.slice(2);
const jsonFilePath = args[0] || './facilities.json';

importScrapedFacilitiesData(jsonFilePath)
  .then(() => console.log("Import script finished"))
  .catch(err => console.error("Fatal error:", err));