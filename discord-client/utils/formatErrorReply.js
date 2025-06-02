// Error formatting utility
module.exports = function formatErrorReply(err, fallbackMsg) {
  if (!err) return fallbackMsg;
  if (err.response && err.response.data && err.response.data.text) return `❌ ${err.response.data.text}`;
  if (err.response && err.response.data && err.response.data.detail) return `❌ ${err.response.data.detail}`;
  if (err.message) return `❌ ${err.message}`;
  return fallbackMsg;
};
