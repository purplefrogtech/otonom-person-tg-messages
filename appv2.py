import asyncio
from telethon import TelegramClient
import json
import os

class TelegramMessageSender:
    def __init__(self, api_id, api_hash, phone):
        """
        Initialize Telegram client with user tracking mechanism
        
        :param api_id: Telegram API ID
        :param api_hash: Telegram API Hash
        :param phone: Phone number
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient('session_name', api_id, api_hash)
        
        # File to track sent users
        self.sent_users_file = 'sent_users.json'
        self.sent_users = self.load_sent_users()

    def load_sent_users(self):
        """
        Load list of users already sent messages to
        
        :return: Set of user IDs
        """
        if os.path.exists(self.sent_users_file):
            try:
                with open(self.sent_users_file, 'r') as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, IOError):
                return set()
        return set()

    def save_sent_users(self):
        """
        Save list of users who have been sent messages
        """
        try:
            with open(self.sent_users_file, 'w') as f:
                json.dump(list(self.sent_users), f)
        except IOError as e:
            print(f"Error saving sent users: {e}")

    async def send_group_messages(self, group_username, message):
        """
        Send messages to group members, avoiding duplicates
        
        :param group_username: Target group's username
        :param message: Message to send
        """
        await self.client.start(self.phone)
        
        try:
            # Get group entity
            group_entity = await self.client.get_entity(group_username)
            participants = await self.client.get_participants(group_entity)

            for participant in participants:
                # Skip bots and already messaged users
                if (participant.bot or 
                    participant.id in self.sent_users):
                    continue

                try:
                    # Send message to individual user
                    await self.client.send_message(participant.id, message)
                    
                    # Add user to sent users list
                    self.sent_users.add(participant.id)
                    
                    # Save after each successful send to prevent duplicate sends if script interrupts
                    self.save_sent_users()
                    
                    print(f"Message sent to {participant.username or participant.id}")
                    
                    # Wait between messages to avoid rate limiting
                    await asyncio.sleep(120)  # 2 minutes between messages
                
                except Exception as send_error:
                    print(f"Could not send message to {participant.username or participant.id}: {send_error}")
        
        except Exception as group_error:
            print(f"An error occurred: {group_error}")
        
        finally:
            await self.client.disconnect()

def main():
    # Telegram credentials
    API_ID = '29444056'
    API_HASH = '2f4d6c5ad97e4f9fbb15a9809d5f9056'
    PHONE = '+905525515184'
    
    # Group and message details
    GROUP_USERNAME = '@paraloper'
    MESSAGE = '''Hocam merhaba @paraloper gurubunun adminiyim, çekiliş düzenliyoruz katılmak ister misiniz? '''

    # Create and run sender
    sender = TelegramMessageSender(API_ID, API_HASH, PHONE)
    
    # Run async function
    asyncio.run(sender.send_group_messages(GROUP_USERNAME, MESSAGE))

if __name__ == "__main__":
    main()