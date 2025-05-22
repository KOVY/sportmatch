// Skript pro přidání nového turnaje pro padel

// Import TournamentService
const tournamentService = require('./client/src/services/TournamentService').default;

// Vytvoření nového turnaje
const newTournament = {
  name: "Padel Czech Masters 2025",
  sport: "padel",
  startDate: "2025-09-15",
  endDate: "2025-09-20",
  location: "Padel Arena Praha",
  capacity: 32,
  format: "Vyřazovací pavouk + skupiny",
  price: 1200,
  registrationOpen: true,
  hasTickets: true,
  allowTokens: true,
  tokenPrice: 120,
  organizer: {
    id: "PAMP",
    name: "Padel Association Prague",
    avatar: ""
  }
};

try {
  // Přidání turnaje
  const result = tournamentService.addTournament(newTournament);
  console.log("Turnaj byl úspěšně přidán:", result);
  
  // Výpis všech turnajů
  const allTournaments = tournamentService.getAllTournaments();
  console.log("Všechny turnaje v systému:", allTournaments);
  
  // Výpis turnajů pro padel
  const padelTournaments = tournamentService.getTournamentsBySport('padel');
  console.log("Turnaje pro padel:", padelTournaments);
} catch (error) {
  console.error("Chyba při vytváření turnaje:", error);
}
