import aiofiles
import json


global_list = []

class memory:
    def __init__(self) :
        self.filename = "memory.json"

    async def add_new_session(self, userid: str , history: list = [] ):
        try:
            new_session = {
                "userid": userid,
                "history": history,
            }
            try:
                async with aiofiles.open(self.filename, 'r') as file:
                    try:
                        existing_data = json.loads(await file.read())
                    except json.JSONDecodeError:
                        existing_data = []
            except FileNotFoundError:
                existing_data = []
            for session in existing_data:
                if session['userid'] == userid:
                    print("Session already exists")
                    return False
            existing_data.append(new_session)
            async with aiofiles.open(self.filename, 'w') as file:
                await file.write(json.dumps(existing_data, indent=4))
            print("Session added successfully")
            return True
        except json.JSONDecodeError:
            print("Error decoding JSON from file")
            return False
        except FileNotFoundError:
            print("File not found")
            return False
        except Exception as e:
            print(str(e))
            return False


    async def add_to_memory(self, userid: str, memory_item: dict = {}):
            # print("\n\n\n\n\n\t\t\t\t  now mmry item  :  ",memory_item)
            try:
                if not memory_item:
                    return False
                try:
                    async with aiofiles.open(self.filename, 'r') as file:
                        try:
                            existing_data = json.loads(await file.read())
                        except json.JSONDecodeError:
                            existing_data = []
                except FileNotFoundError:
                    existing_data = []
                print("existing data in add mmry  :  ",existing_data)
                user_found = False
                for user in existing_data:
                    if user['userid'] == userid:
                        user_found = True
                        if len(user['history']) >= 20:
                            user['history'].pop(0)  # Remove the oldest item
                        if "Human" in memory_item:
                            print("going to add new item")
                            user['history'].append(memory_item)
                        elif "response" in memory_item:
                            print("going to add new response")
                            if user['history']:
                                user['history'][-1]["Ai"]=memory_item['response']
                        break
                # print("existing data after loop  :  ",json.dumps(existing_data))
                if not user_found:
                    print("user not found")
                    return False
                async with aiofiles.open(self.filename, 'w') as file:
                    await file.write(json.dumps(existing_data, indent=4))
                print("Item added to memory successfully")
                return True
            except json.JSONDecodeError:
                print("Error decoding JSON from file")
                return False
            except FileNotFoundError:
                print("File not found")
                return False
            except Exception as e:
                print(str(e))
                return False


    async def get_history(self, userid: str):
        try:
            async with aiofiles.open(self.filename, 'r') as file:
                try:
                    existing_data = json.loads(await file.read())
                except json.JSONDecodeError:
                    existing_data = []
        except FileNotFoundError:
            existing_data = []
        
        for user in existing_data:
            if user['userid'] == userid:
                return user['history']
        
        print("User not found")
        return None
    async def remove_session(self, userid: str):
        try:
            async with aiofiles.open(self.filename, 'r') as file:
                try:
                    existing_data = json.loads(await file.read())
                except json.JSONDecodeError:
                    existing_data = []
        except FileNotFoundError:
            existing_data = []

        # Filter out the user with the given userid
        new_data = [session for session in existing_data if session['userid'] != userid]

        if len(new_data) == len(existing_data):
            print("User not found, nothing to remove")
            return False

        # Write the updated data back to the file
        async with aiofiles.open(self.filename, 'w') as file:
            await file.write(json.dumps(new_data, indent=4))

        print("Session removed successfully")
        return True

            
# obj = memory()
# import asyncio
# asyncio.run(obj.add_new_session("2"))
# # asyncio.run(obj.add_to_memory("1",{"Human":"hi"}))