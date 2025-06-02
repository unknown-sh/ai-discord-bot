// Discord headers utility
module.exports = function getDiscordHeaders(message) {
  return {
    'X-User-ID': message.author.id,
    'X-Discord-User-ID': message.author.id,
    'X-Discord-Username': message.author.username
  };
};
