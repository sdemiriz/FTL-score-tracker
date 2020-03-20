from TwitchWebsocket import TwitchWebsocket
import pandas as pd
import re

class ftlScoreBot:
    def __init__(self):
        self.host = "irc.chat.twitch.tv"
        self.port = 6667
        self.chan = "#the_farb"
        self.nick = "ftltrackerbot"
        self.auth = "oauth:19wyalzmxpekmfvne7off4l0y21jy5"
        
        # Send along all required information, and the bot will start 
        # sending messages to your callback function. (self.message_handler in this case)
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=["membership", "tags", "commands"],
                                  live=True)

        # Temporary dataframe for storing score guesses                                  
        self.df = pd.DataFrame(columns=['User', 'Score'])
        self.ws.start_bot()
        # Any code after this will be executed after a KeyboardInterrupt

    # Check if user is Moderator+
    def check_user_hard(self, m):
        return ("moderator" in m.tags["badges"] or "broadcaster" in m.tags["badges"] or "bloodlad_" == m.user.lower())

    # Handle score guesses and tally
    def message_handler(self, m):  

        # Matching for score guess
        num_pat = re.compile('^[0-9]+')
        # Matching for !score command
        comm_pat = re.compile('!score [0-9]+')

        # Ignore network based errors
        try:             

            # Check for patterns in message
            match = num_pat.match(m.message)
            command = comm_pat.match(m.message)
            
            # If a user guess is identified
            if match:

                # Localize variables with appropriate typing
                score = int(match.group())
                username = str(m.user)

                # Report guess is recieved
                # self.ws.send_message("Score guess received: " + str(score) + " from: " + username)

                if username in self.df.User.values:
                    # If guess is from the same user, replace existing guess
                    self.df.loc[(self.df.User == username), 'Score'] = score
                else:
                    # Otherwise, add to the list
                    self.df = self.df.append({'User': username, 'Score': score}, ignore_index=True)

                # For testing purposes
                print(self.df); print()
            
            # If Moderator+ have put in correct score
            elif command and self.check_user_hard(m):

                # Get correct score
                correct = int(re.split(' ', command.group())[1])

                # Get differences from the correct score
                self.df['Diff'] = abs(self.df['Score'] - correct)
                self.df = self.df.sort_values('Diff')

                # Display winner
                self.ws.send_message("Winner: " + self.df['User'].iloc[0] + " with " + str(self.df['Score'].iloc[0]))

                # Drop all entries, guesses have ended
                print(self.df); print()
                self.df = self.df.iloc[0:0]
                self.df = self.df.drop('Diff')

            else:
                pass  
                
        # TODO: Implement error logging
        except:
            pass

# Start bot when launched from CLI
if __name__ == "__main__":
    ftlScoreBot()