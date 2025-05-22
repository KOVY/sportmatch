/**
 * Diagnostický nástroj pro přímou kontrolu databáze turnajů
 * 
 * Tento skript provede přímý SQL dotaz na databázi a pokusí se najít turnaje
 * jak pomocí ORM, tak pomocí přímého SQL dotazu. Tak zjistíme, zda problém
 * je v kódu nebo v databázi samotné.
 */

import { db } from './server/db.js';
import { sql } from 'drizzle-orm';
import { tournaments } from './shared/schema.js';
import { eq } from 'drizzle-orm';

async function checkDatabase() {
  try {
    console.log('----------------------------------------------');
    console.log('DIAGNOSTIKA DATABÁZE TURNAJŮ');
    console.log('----------------------------------------------');
    
    // 1. Kontrola připojení k databázi
    console.log('1. Kontrola připojení k databázi:');
    try {
      const dbInfo = await db.execute(sql`SELECT current_database(), version();`);
      console.log('Databáze je dostupná:', dbInfo[0]);
      console.log('----------------------------------------------');
    } catch (error) {
      console.error('Chyba při připojení k databázi:', error);
      return;
    }
    
    // 2. Výpis schématu tabulky turnajů
    console.log('2. Schéma tabulky turnajů:');
    try {
      const tableSchema = await db.execute(sql`
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'tournaments'
      `);
      
      console.log('Sloupce tabulky tournaments:');
      tableSchema.forEach(column => {
        console.log(`- ${column.column_name}: ${column.data_type} (nullable: ${column.is_nullable})`);
      });
      console.log('----------------------------------------------');
    } catch (error) {
      console.error('Chyba při získávání schématu tabulky:', error);
    }
    
    // 3. Výpis všech turnajů v databázi
    console.log('3. Seznam všech turnajů v databázi:');
    try {
      const allTournaments = await db.select().from(tournaments);
      console.log(`Nalezeno ${allTournaments.length} turnajů:`);
      
      allTournaments.forEach(t => {
        console.log(`- ID: "${t.id}" (${typeof t.id}), název: "${t.name}", sport: "${t.sportId}"`);
      });
      console.log('----------------------------------------------');
      
      // 4. Pokus o nalezení konkrétního turnaje
      if (allTournaments.length > 0) {
        const lastTournament = allTournaments[allTournaments.length - 1];
        console.log(`4. Pokus o nalezení posledního turnaje s ID: ${lastTournament.id} (${typeof lastTournament.id})`);
        
        // 4.1 Pokus pomocí ORM
        console.log('4.1 Pokus pomocí ORM:');
        const tournamentByORM = await db.select().from(tournaments).where(eq(tournaments.id, lastTournament.id));
        console.log('Výsledek ORM dotazu:', tournamentByORM.length > 0 ? 'NALEZEN' : 'NENALEZEN');
        if (tournamentByORM.length > 0) {
          console.log('Detail turnaje (ORM):', tournamentByORM[0]);
        }
        
        // 4.2 Pokus pomocí přímého SQL dotazu
        console.log('4.2 Pokus pomocí přímého SQL:');
        const tournamentBySQL = await db.execute(sql`SELECT * FROM tournaments WHERE id = ${lastTournament.id}`);
        console.log('Výsledek SQL dotazu:', tournamentBySQL.length > 0 ? 'NALEZEN' : 'NENALEZEN');
        if (tournamentBySQL.length > 0) {
          console.log('Detail turnaje (SQL):', tournamentBySQL[0]);
        }
        
        // 4.3 Pokus pomocí textové verze ID
        console.log('4.3 Pokus pomocí textové verze ID:');
        const tournamentByTextId = await db.execute(sql`SELECT * FROM tournaments WHERE CAST(id AS TEXT) = ${String(lastTournament.id)}`);
        console.log('Výsledek SQL dotazu s textovým ID:', tournamentByTextId.length > 0 ? 'NALEZEN' : 'NENALEZEN');
        
        console.log('----------------------------------------------');
      } else {
        console.log('Databáze neobsahuje žádné turnaje, nelze provést další testy.');
      }
    } catch (error) {
      console.error('Chyba při získávání turnajů:', error);
    }
    
    console.log('DIAGNOSTIKA DOKONČENA');
    
  } catch (error) {
    console.error('Neočekávaná chyba při diagnostice:', error);
  }
}

// Spustíme diagnostiku
checkDatabase().then(() => {
  console.log('Diagnostika ukončena.');
  process.exit(0);
}).catch(error => {
  console.error('Fatální chyba při diagnostice:', error);
  process.exit(1);
});