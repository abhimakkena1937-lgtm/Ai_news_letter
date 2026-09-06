import asyncio

# Allow only one Gemini request at a time
gemini_semaphore = asyncio.Semaphore(1)