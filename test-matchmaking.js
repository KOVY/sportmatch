// This file is treated as an ES Module because "type": "module" is set in package.json
import fetch from 'node-fetch';

// Sample group data for testing the matchmaking algorithm
const sampleGroup = {
  id: 123,
  name: "Casual Tennis Group",
  sport: "Tennis",
  level: "Intermediate",
  members: [1, 2, 3], // IDs of existing members to exclude from recommendations
  location: "Prague",
  required_skills: ["forehand", "backhand", "serve"],
  social_style: "balanced",
  active_times: {
    "monday": { "morning": true, "evening": true },
    "wednesday": { "afternoon": true },
    "saturday": { "morning": true }
  },
  privacy_mode: "hybrid"
};

// Call the matchmaking API
async function testMatchmaking() {
  try {
    // Use the correct API endpoint - we found it's "/api/groups/matchmaking" in server/routes.ts
    const apiUrl = 'http://localhost:3000/api/groups/matchmaking';
    console.log('Trying URL:', apiUrl);
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ group: sampleGroup }),
    });
    
    // Log the raw response first for debugging
    const text = await response.text();
    console.log('Raw API Response:', text);
    
    // Try to parse as JSON if possible
    let data;
    try {
      data = JSON.parse(text);
      console.log('Parsed JSON Response:');
      console.log(JSON.stringify(data, null, 2));
    } catch (parseError) {
      console.error('Failed to parse response as JSON');
    }
  } catch (error) {
    console.error('Error calling matchmaking API:', error);
  }
}

testMatchmaking();