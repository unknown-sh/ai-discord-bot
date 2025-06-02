// Discord client memory helpers for user and bot context (via MCP server)
const axios = require('axios');
// Prefer localhost for local/dev, fallback to Docker service name for Compose
const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://localhost:8001';
console.log('[memory.js] MCP_SERVER_URL at startup:', MCP_SERVER_URL);

async function getUserContext(userId, key) {
  try {
    console.log(`[memory.js] getUserContext: userId=${userId}, key=${key}`);
    const resp = await axios.get(`${MCP_SERVER_URL}/memory/${key}`, {
      headers: { 'X-User-ID': userId }
    });
    console.log(`[memory.js] getUserContext: success, data=`, resp.data);
    // Defensive: handle both dict and list responses
    if (Array.isArray(resp.data)) {
      if (resp.data.length > 0 && typeof resp.data[0] === 'object' && resp.data[0].value !== undefined) {
        return { value: resp.data[0].value };
      } else {
        console.error('[memory.js] getUserContext: Unexpected list response from memory API:', resp.data);
        throw new Error('[getUserContext] MCP returned a list, but no usable value found.');
      }
    } else if (resp.data && typeof resp.data === 'object') {
      return resp.data;
    } else {
      console.error('[memory.js] getUserContext: Unexpected response type from memory API:', resp.data);
      throw new Error('[getUserContext] MCP returned unexpected response type.');
    }
  } catch (err) {
    console.error(`[memory.js] getUserContext ERROR:`, err && err.stack || err);
    if (err.response) {
      throw new Error(`[getUserContext] MCP error: ${err.response.status} ${err.response.statusText} - ${JSON.stringify(err.response.data)}`);
    } else if (err.request) {
      throw new Error(`[getUserContext] MCP no response: ${err.message}`);
    } else {
      throw new Error(`[getUserContext] MCP unknown error: ${err && err.stack || err}`);
    }
  }
}

async function setUserContext(userId, key, value) {
  try {
    console.log(`[memory.js] setUserContext: userId=${userId}, key=${key}, value=${value}`);
    const resp = await axios.post(`${MCP_SERVER_URL}/memory`, { key, value }, {
      headers: { 'X-User-ID': userId }
    });
    console.log(`[memory.js] setUserContext: success, data=`, resp.data);
    return resp.data;
  } catch (err) {
    console.error(`[memory.js] setUserContext ERROR:`, err && err.stack || err);
    if (err.response) {
      throw new Error(`[setUserContext] MCP error: ${err.response.status} ${err.response.statusText} - ${JSON.stringify(err.response.data)}`);
    } else if (err.request) {
      throw new Error(`[setUserContext] MCP no response: ${err.message}`);
    } else {
      throw new Error(`[setUserContext] MCP unknown error: ${err && err.stack || err}`);
    }
  }
}

async function getBotContext(key) {
  const resp = await axios.get(`${MCP_SERVER_URL}/bot-context/${key}`, {
    headers: { 'X-User-ID': 'bot' }
  });
  return resp.data;
}

async function setBotContext(key, value) {
  const resp = await axios.post(`${MCP_SERVER_URL}/bot-context`, { key, value }, {
    headers: { 'X-User-ID': 'bot' }
  });
  return resp.data;
}

module.exports = {
  getUserContext,
  setUserContext,
  getBotContext,
  setBotContext
};
