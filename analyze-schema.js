const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Získá obsah schéma souboru
 */
function getSchemaContent() {
  const schemaPath = path.join(__dirname, 'shared/schema.ts');
  return fs.readFileSync(schemaPath, 'utf8');
}

/**
 * Komunikuje s AZR přes Python bridge
 */
async function askAZR(question) {
  return new Promise((resolve, reject) => {
    const pythonPath = 'python3';
    const scriptPath = path.join(__dirname, 'azr/azr_bridge.py');
    
    const pythonProcess = spawn(pythonPath, [scriptPath]);
    
    let dataString = '';
    let errorString = '';
    
    // Zachycení dat z stdout
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    // Zachycení chyb z stderr
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    // Po dokončení procesu
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`AZR process exited with code ${code}`);
        console.error(`AZR error: ${errorString}`);
        reject(new Error(`AZR process failed: ${errorString}`));
        return;
      }
      
      try {
        console.log("Raw response:", dataString);
        const result = JSON.parse(dataString);
        resolve(result);
      } catch (err) {
        reject(new Error(`Could not parse AZR response: ${err.message}`));
      }
    });
    
    // Poslání otázky na stdin
    const input = JSON.stringify({ question });
    pythonProcess.stdin.write(input);
    pythonProcess.stdin.end();
  });
}

/**
 * Hlavní funkce
 */
async function main() {
  try {
    const schemaContent = getSchemaContent();
    
    const question = `
Jako Absolute Zero Reasoner (AZR), potřebuji zanalyzovat a optimalizovat
schéma databáze pro multijazyčnou sportovní platformu SportMatch, která integruje
Supabase, Stripe platby a systém FitnessTokenů (1 token = 10 CZK).

Aktuální schéma:
\`\`\`typescript
${schemaContent}
\`\`\`

Zhodnoť kvalitu tohoto schématu a navrhni případné optimalizace, zejména s ohledem na:
1. Multijazyčnou podporu (cs/en/de) a URL prefixy (/cs/sporty/tenis, /en/sports/tennis)
2. Integraci plateb přes FitnessTokeny a Stripe
3. SportStream sekci pro živé přenosy a sociální funkce
4. Správu sportovních zařízení a rezervací

Odpověď strukturuj takto:
1. <think> tvé uvažování o schématu a jeho kvalitě </think>
2. <answer> tvé zhodnocení a návrhy na optimalizaci </answer>
`;

    console.log("Asking AZR for schema analysis...");
    const response = await askAZR(question);
    
    if (response && (response.thinking || response.answer)) {
      console.log("\n=== AZR THINKING ===\n");
      console.log(response.thinking || "No thinking provided");
      
      console.log("\n=== AZR ANSWER ===\n");
      console.log(response.answer || "No answer provided");
    } else {
      console.log("AZR response format is unexpected:", response);
    }
  } catch (error) {
    console.error("Error occurred:", error);
  }
}

main();