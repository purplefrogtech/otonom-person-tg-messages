import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
import json
import os

class TelegramMessageSender:
    def __init__(self, api_id, api_hash, phone_number):
        """
        Initialize Telegram client and tracking mechanism
        
        :param api_id: Your Telegram API ID
        :param api_hash: Your Telegram API Hash
        :param phone_number: Your registered phone number
        """
        self.client = TelegramClient(phone_number, api_id, api_hash)
        self.sent_users_file = 'sent_users.json'
        self.sent_users = self.load_sent_users()

    def load_sent_users(self):
        """
        Load list of users already sent messages to prevent duplicate sending
        
        :return: Set of user IDs
        """
        if os.path.exists(self.sent_users_file):
            with open(self.sent_users_file, 'r') as f:
                return set(json.load(f))
        return set()

    def save_sent_users(self):
        """
        Save list of users who have been sent messages
        """
        with open(self.sent_users_file, 'w') as f:
            json.dump(list(self.sent_users), f)

    async def send_group_messages(self, group_username, message):
        """
        Send message to group members who haven't been messaged before
        
        :param group_username: Target group's username
        :param message: Message to send
        """
        await self.client.start()
        
        try:
            # Get group entity
            group = await self.client.get_entity(group_username)
            
            # Fetch group participants
            participants = await self.client.get_participants(group)
            
            for participant in participants:
                # Skip if user already messaged
                if participant.id in self.sent_users:
                    continue
                
                try:
                    # Send message to individual user
                    await self.client.send_message(participant, message)
                    
                    # Track sent user
                    self.sent_users.add(participant.id)
                    
                    # Optional: Add a delay to avoid rate limiting
                    await asyncio.sleep(2)
                
                except Exception as send_error:
                    print(f"Error sending to {participant.first_name}: {send_error}")
            
            # Save sent users after process completes
            self.save_sent_users()
        
        except Exception as group_error:
            print(f"Group access error: {group_error}")
        
        finally:
            await self.client.disconnect()

def main():
    # Replace with your actual credentials
    API_ID = '21811515'
    API_HASH = 'c6ba0ed1de633b8c6bfec9fc2c216bb1'
    PHONE_NUMBER = '+905528213519'
    
    # Target group and message
    GROUP_USERNAME = '@paraloper'
    MESSAGE = "Hocam merhaba @paraloper gurubunun adminiyim, çekiliş düzenliyoruz katılmak ister misiniz?"
    
    sender = TelegramMessageSender(API_ID, API_HASH, PHONE_NUMBER)
    
    # Run async function
    asyncio.run(sender.send_group_messages(GROUP_USERNAME, MESSAGE))

if __name__ == "__main__":
    main()