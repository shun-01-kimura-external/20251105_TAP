import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_roll_dice_tool(n_dice: int):
    async with client:
        result = await client.call_tool("roll_dice", {"n_dice": n_dice})
        print(result.data)

if __name__ == "__main__":
    asyncio.run(call_roll_dice_tool(2))
