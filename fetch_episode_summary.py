#!/usr/bin/env python3
"""
Script to fetch Mr. Robot episode summaries from Fandom wiki.
Extracts the main content from the episode summary pages.
"""

import requests
from bs4 import BeautifulSoup
import sys
import os
import re


def fetch_episode_summary(url, output_file=None):
    """
    Fetch episode summary from the given URL and save to a text file.
    
    Args:
        url: The URL to fetch
        output_file: Optional output filename. If not provided, generates from URL.
    
    Returns:
        str: Path to the saved file
    """
    print(f"Fetching content from: {url}")
    
    try:
        # Fetch the webpage
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
        
        if not content_div:
            print("Error: Could not find the content div")
            return None
        
        # Extract text from paragraphs (no blank lines)
        paragraphs = content_div.find_all('p')
        # Use separator=' ' to ensure spaces between HTML elements
        text_parts = [p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True)]
        # Clean up multiple spaces
        text_content = '\n'.join(re.sub(r'\s+', ' ', part) for part in text_parts)
        
        # Generate output filename if not provided
        if output_file is None:
            # Extract episode identifier from URL
            episode_id = url.split('/wiki/')[-1].split('/')[0]
            output_file = f"{episode_id}_summary.txt"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Summary saved to: {output_file}")
        print(f"Content length: {len(text_content)} characters")
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Error processing content: {e}")
        return None


def fetch_multiple_episodes(episode_ids, base_url="https://mrrobot.fandom.com/wiki/{}/Summary"):
    """
    Fetch summaries for multiple episodes.
    
    Args:
        episode_ids: List of episode identifiers (e.g., ['405_Method_Not_Allowed', '406_Not_Acceptable'])
        base_url: URL template with {} placeholder for episode ID
    """
    results = []
    
    for episode_id in episode_ids:
        url = base_url.format(episode_id)
        output_file = fetch_episode_summary(url)
        if output_file:
            results.append(output_file)
        print()  # Blank line between episodes
    
    print(f"\nSuccessfully fetched {len(results)} of {len(episode_ids)} episodes")
    return results


def main():
    """Main function to run the script."""
    if len(sys.argv) > 1:
        # Use URL from command line argument
        url = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        fetch_episode_summary(url, output_file)
    else:
        # Default: fetch the example episode
        url = "https://mrrobot.fandom.com/wiki/405_Method_Not_Allowed/Summary"
        fetch_episode_summary(url)


if __name__ == "__main__":
    main()
