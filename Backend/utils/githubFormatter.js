const axios = require('axios');

/**
 * Formats a list of clinical evidence using a hypothetical GitHub-based GPT-4o service.
 * @param {Array<Object>} evidenceList - An array of evidence objects, each with a 'source' and 'text'.
 * @returns {Promise<string>} A formatted string summarizing the evidence.
 */
async function formatEvidenceWithGithub(evidenceList) {
    if (!process.env.GITHUB_TOKEN) {
        return "Error: GITHUB_TOKEN environment variable is not set.";
    }

    if (!evidenceList || evidenceList.length === 0) {
        return "No evidence provided to format.";
    }

    const endpoint = 'http://127.0.0.1:5001/format'; // Hypothetical endpoint

    const payload = {
        model: 'gpt-4o', // Assuming the service knows what to do with this
        prompt: `
            You are a clinical assistant AI. Your task is to synthesize and format medical evidence into a clear, concise summary for an oncologist.
            The following is a list of evidence snippets from various sources (e.g., NCCN guidelines, clinical trial results).
            Please format this information into a structured summary. Use markdown for formatting, such as bolding for headers and bullet points for lists.

            Do not simply list the evidence. Synthesize it. Group related findings, highlight key takeaways, and present it in a logical order.

            Here is the evidence to format:
            ${evidenceList.map(e => `
--- ${e.source} ---
${e.text}`).join('')}
        `
    };

    const config = {
        headers: {
            'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
            'Content-Type': 'application/json'
        }
    };

    try {
        console.log(`Attempting to format evidence with hypothetical GitHub service at ${endpoint}...`);
        const response = await axios.post(endpoint, payload, config);
        
        // Assuming the response has a 'data' field with the formatted text
        return response.data.formattedText || JSON.stringify(response.data, null, 2);
    } catch (error) {
        console.error("Error formatting evidence with GitHub-based service:", error.message);
        if (error.response) {
            console.error("Response data:", error.response.data);
            console.error("Response status:", error.response.status);
        }
        return `Error: Could not connect to the formatting service at ${endpoint}. Please ensure it is running and configured correctly.`;
    }
}

module.exports = { formatEvidenceWithGithub };
