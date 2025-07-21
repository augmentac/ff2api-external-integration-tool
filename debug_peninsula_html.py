#!/usr/bin/env python3
"""
Debug Peninsula HTML responses
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_peninsula_html():
    """Debug Peninsula HTML responses"""
    
    async with aiohttp.ClientSession() as session:
        urls = [
            "https://www.peninsulatrucklines.com",
            "https://www.peninsulatrucklines.com/tracking",
            "https://www.peninsulatrucklines.com/track"
        ]
        
        for url in urls:
            try:
                print(f"\n🔍 Examining: {url}")
                async with session.get(url) as response:
                    print(f"Status: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    
                    content = await response.text()
                    print(f"Content length: {len(content)}")
                    print(f"Content preview:\n{content[:500]}...")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for tracking-related elements
                    forms = soup.find_all('form')
                    inputs = soup.find_all('input')
                    
                    print(f"Forms found: {len(forms)}")
                    print(f"Input fields found: {len(inputs)}")
                    
                    if forms:
                        for i, form in enumerate(forms):
                            print(f"  Form {i}: action='{form.get('action')}', method='{form.get('method')}'")
                    
                    if inputs:
                        for i, inp in enumerate(inputs):
                            print(f"  Input {i}: name='{inp.get('name')}', type='{inp.get('type')}', value='{inp.get('value')}'")
                    
            except Exception as e:
                print(f"❌ Error with {url}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_peninsula_html())