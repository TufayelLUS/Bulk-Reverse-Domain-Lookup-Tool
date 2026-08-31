import requests
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Thread-safe lock for file operations
file_lock = threading.Lock()
# Thread-safe set for collected domains
collected_domains = set()
collected_domains_lock = threading.Lock()

# Thread count control
THREADS = 30

def domainToIP(domain):
    """
    Convert a domain name to its IP address using a DNS lookup API
    """
    try:
        # Using a free DNS lookup API
        url = f"https://dns.google/resolve?name={domain.split('://')[-1].split('/')[0]}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if 'Answer' in data:
            for answer in data['Answer']:
                if answer['type'] == 1:  # A record (IPv4)
                    return answer['data']
        return None
    except requests.RequestException as e:
        print(f"Error getting IP for {domain}: {e}")
        return None

def getReverseIP(ip):
    """
    Get domain names associated with an IP address
    """
    try:
        # Use the provided reverse IP API
        url = f"https://api.reverseipdomain.com/?ip={ip}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        # The API returns a list of domains
        if 'result' in data:
            return data['result']
        elif isinstance(data, list):
            return data
        else:
            return data
    except requests.RequestException as e:
        print(f"Error getting reverse IP for {ip}: {e}")
        return None

def save_to_collected(domains, filename="collected.txt"):
    """
    Save discovered domains to a file, avoiding duplicates (Thread-safe)
    """
    try:
        # Read existing domains if file exists (with lock)
        with file_lock:
            existing_domains = set()
            try:
                with open(filename, 'r') as f:
                    existing_domains = set(line.strip() for line in f if line.strip())
            except FileNotFoundError:
                pass
            
            # Add new domains
            new_domains = set(domains) - existing_domains
            
            if new_domains:
                with open(filename, 'a') as f:
                    for domain in sorted(new_domains):
                        f.write(f"{domain}\n")
                print(f"  ✓ Added {len(new_domains)} new domain(s) to {filename}")
            else:
                print(f"  ℹ No new domains to add to {filename}")
                
        return len(new_domains)
        
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return 0

def process_single_domain(domain, index, total_doms):
    """
    Process a single domain - get IP and reverse IP lookup
    """
    discovered = []
    
    print(f"\n[{index}/{total_doms}] Domain: {domain}")
    
    # Check if already IP given
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
        ip = domain
    else:
        # Get IP for the domain
        ip = domainToIP(domain)
    
    if ip:
        print(f"  IP Address: {ip}")
        
        # Get reverse IP lookup
        reverse_domains = getReverseIP(ip)
        if reverse_domains:
            if isinstance(reverse_domains, list):
                print(f"  Domains on same IP ({len(reverse_domains)} found):")
                discovered.extend(reverse_domains)
                
                # Display first 10
                for d in reverse_domains[:10]:
                    print(f"    - {d}")
                if len(reverse_domains) > 10:
                    print(f"    ... and {len(reverse_domains) - 10} more")
            else:
                print(f"  Reverse IP result: {reverse_domains}")
                if isinstance(reverse_domains, str):
                    discovered.append(reverse_domains)
        else:
            print("  No reverse IP data found")
    else:
        print("  Could not resolve domain")
    
    print("-" * 60)
    return discovered

def process_input_file(filename="input.txt"):
    """
    Read domains from input.txt file and process each one using ThreadPoolExecutor
    """
    all_discovered_domains = []
    
    try:
        with open(filename, 'r') as file:
            domains = file.read().strip().splitlines()
        
        # Remove empty lines and strip whitespace
        domains = [domain.strip() for domain in domains if domain.strip()]
        
        # Make unique
        domains = list(set(domains))
        
        if not domains:
            print("No domains found in input.txt")
            return
        
        print(f"Processing {len(domains)} domain(s) using {THREADS} threads...\n")
        print("=" * 60)
        
        total_doms = len(domains)
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            # Submit all tasks
            future_to_domain = {
                executor.submit(process_single_domain, domain, index + 1, total_doms): domain 
                for index, domain in enumerate(domains)
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    discovered = future.result()
                    if discovered:
                        all_discovered_domains.extend(discovered)
                except Exception as e:
                    print(f"Error processing {domain}: {e}")
        
        # Save all discovered domains to collected.txt
        if all_discovered_domains:
            print("\n" + "=" * 60)
            print(f"Saving {len(all_discovered_domains)} discovered domain(s) to collected.txt...")
            # Remove duplicates
            unique_domains = list(set(all_discovered_domains))
            saved = save_to_collected(unique_domains)
            print(f"✓ Successfully saved {saved} new unique domains to collected.txt")
            print(f"Total unique domains discovered: {len(unique_domains)}")
        else:
            print("\nNo domains were discovered to save.")
            
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please create the file with domain names (one per line).")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Example usage
if __name__ == "__main__":
    # Clear collected.txt before starting
    open('collected.txt', mode='w').close()
    process_input_file()
