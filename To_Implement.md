# Features:
1. Wish Slack Chat a Happy Birthday on Aug 8th (originally started in 2018)
2. Bot should wish herself a happy birthday on March 3rd
3. Implement DynamoDB connection so bot has access to state information
4. Implement CI/CD
5. Allow bot to react to Direct, Private and Group Messages she's been invited to.
6. If sent a request from a Serious Channel. Should not respond in channel. Should send
   User a Private Message explaning channel rules and that she is not allowed to post there.

# Commands:
1. Praise @user (has the bot say some nice things about the user)
2. Kill me (change to kick user from a channel, and give them a PM explaining what happened)
3. Quote (add, remove, list) # requires a database (could be seeded with funny quotes)
4. Spotify me (album, artist, track, song)
5. Roll (default: 1d6 max: 300d20)
6. Recipe me (responds with a recipe of the given query)
7. Booze me: should respond with drink recipe (or occasionally chide the user for their drinking problem)
8. Poll me (creates a small poll people can react to)
