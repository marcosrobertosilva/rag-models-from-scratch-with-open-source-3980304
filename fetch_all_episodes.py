#!/usr/bin/env python3
"""
Script to fetch all Mr. Robot episode summaries from the season_episodes.csv file.
Creates a single comprehensive text file with all episodes in sequence.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import sys


def fetch_episode_summary(url, season_episode):
    """
    Fetch episode summary from the given URL.
    
    Args:
        url: The URL to fetch
        season_episode: Season and episode identifier (e.g., 'S1E01')
    
    Returns:
        tuple: (season_episode, text_content) or (None, None) if failed
    """
    print(f"Fetching {season_episode}: {url}")
    
    try:
        # Fetch the webpage
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
        
        if not content_div:
            print(f"  ⚠ Warning: Could not find content div for {season_episode}")
            return None, None
        
        # Extract text from paragraphs
        paragraphs = content_div.find_all('p')
        # Use separator=' ' to ensure spaces between HTML elements
        text_parts = [p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True)]
        # Clean up multiple spaces
        text_content = '\n'.join(re.sub(r'\s+', ' ', part) for part in text_parts)
        
        print(f"  ✓ Successfully fetched {season_episode} ({len(text_content)} characters)")
        
        return season_episode, text_content
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {season_episode}: {e}")
        return None, None
    except Exception as e:
        print(f"  ✗ Error processing {season_episode}: {e}")
        return None, None


def fetch_all_episodes(csv_file, output_file, delay=1.0):
    """
    Fetch all episodes from the CSV file and save to a single text file.
    
    Args:
        csv_file: Path to the CSV file with episode URLs
        output_file: Path to the output text file
        delay: Delay in seconds between requests (to be polite to the server)
    
    Returns:
        dict: Statistics about the fetch operation
    """
    episodes = []
    failed = []
    
    print(f"Reading episodes from: {csv_file}\n")
    
    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            season_episode = row['season_episode']
            url = row['url']
            
            # Fetch the episode
            se_id, content = fetch_episode_summary(url, season_episode)
            
            if se_id and content:
                episodes.append({
                    'id': se_id,
                    'content': content
                })
            else:
                failed.append(season_episode)
            
            # Be polite to the server
            if delay > 0:
                time.sleep(delay)
    
    print(f"\n{'='*70}")
    print(f"Fetch complete: {len(episodes)} successful, {len(failed)} failed")
    if failed:
        print(f"Failed episodes: {', '.join(failed)}")
    print(f"{'='*70}\n")
    
    # Write all episodes to a single file
    print(f"Writing all episodes to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, episode in enumerate(episodes):
            # Write episode header
            f.write(f"{'='*70}\n")
            f.write(f"EPISODE: {episode['id']}\n")
            f.write(f"{'='*70}\n\n")
            
            # Write episode content
            f.write(episode['content'])
            
            # Add spacing between episodes (but not after the last one)
            if i < len(episodes) - 1:
                f.write("\n\n")
    
    print(f"✓ Successfully wrote {len(episodes)} episodes to {output_file}")
    
    # Calculate total statistics
    total_chars = sum(len(ep['content']) for ep in episodes)
    total_words = sum(len(ep['content'].split()) for ep in episodes)
    
    stats = {
        'total_episodes': len(episodes),
        'failed_episodes': len(failed),
        'total_characters': total_chars,
        'total_words': total_words,
        'output_file': output_file
    }
    
    return stats


def main():
    """Main function to run the script."""
    csv_file = 'season_episodes.csv'
    output_file = 'mr_robot_all_episodes_summary.txt'
    
    # Allow custom parameters from command line
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print("="*70)
    print("Mr. Robot Episode Summary Fetcher")
    print("="*70)
    print(f"CSV file: {csv_file}")
    print(f"Output file: {output_file}")
    print("="*70 + "\n")
    
    # Fetch all episodes
    stats = fetch_all_episodes(csv_file, output_file, delay=1.0)
    
    # Print final statistics
    print("\n" + "="*70)
    print("FINAL STATISTICS")
    print("="*70)
    print(f"Total episodes fetched: {stats['total_episodes']}")
    print(f"Failed episodes: {stats['failed_episodes']}")
    print(f"Total characters: {stats['total_characters']:,}")
    print(f"Total words: {stats['total_words']:,}")
    print(f"Output file: {stats['output_file']}")
    print("="*70)


if __name__ == "__main__":
    main()
