// Ask command handler with persistent memory integration
const { getUserContext, setUserContext } = require('../memory');

module.exports = async function handleAskCommand(message, args, axios, logger, getDiscordHeaders, formatErrorReply) {
  const userId = message.author.id;
  const input = args.join(' ');

  // 1. Load conversation history (if any)
  let history = [];
  try {
    const mem = await getUserContext(userId, 'conversation_history');
    if (mem && mem.value) {
      history = JSON.parse(mem.value);
    }
  } catch (e) {
    logger.warn(`No prior conversation history for user ${userId}`);
  }

  // 2. Send message and history to AI gateway
  try {
    const response = await axios.post('http://ai-gateway:8000/ask', {
      message: input,
      history
    }, { headers: getDiscordHeaders(message) });
    logger.info(`AI Gateway /ask response: ${JSON.stringify(response.data)}`);
    const replyText = response.data.reply;
    // 3. Update conversation history
    const newHistory = [...history, { user: input, bot: replyText }].slice(-10); // keep last 10 exchanges
    try {
      await setUserContext(userId, 'conversation_history', JSON.stringify(newHistory));
    } catch (setErr) {
      logger.error(`setUserContext failed:`, setErr);
      await message.reply(formatErrorReply(setErr, `\u274c Failed to save conversation history. ${setErr && setErr.stack || setErr}`));
      return;
    }
    try {
      if (replyText && replyText.trim().length > 0) {
        const chunks = replyText.match(/.{1,2000}/gs) || [replyText];
        for (const chunk of chunks) {
          await message.reply(chunk);
        }
      } else {
        await message.reply("Sorry, I couldn't generate a response.");
      }
    } catch (replyErr) {
      logger.error(`Discord message.reply failed:`, replyErr);
    }
  } catch (err) {
    logger.error(`AI/ask failed:`, err);
    let errorDetails = '';
    if (err instanceof Error) {
      errorDetails = err.stack || err.message;
    } else if (typeof err === 'object') {
      try {
        errorDetails = JSON.stringify(err);
      } catch (e) {
        errorDetails = String(err);
      }
    } else {
      errorDetails = String(err);
    }
    await message.reply(formatErrorReply(err, `\u274c AI error. ${errorDetails}`));
  }
};
