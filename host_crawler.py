###Host_Crawler###
import requests
import time
import os
from bs4 import BeautifulSoup

from urllib.parse import urlparse, urljoin

class host_crawler:
        
    def __init__(self):
        
        #domain, links_to_return, max_attempts
        #self.link_to_return=link_to_return
        #self.max_attempts=max_attempts
        self.ALLOWED_CONTENT_TYPES = {'text/html', 'text/plain'}
        self.MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
        os.environ["SSLKEYLOGFILE"] = "secrets.log"

    
    def is_external_link(self, base_url, link):
        """Check if the link points to a different subdomain or an external domain"""
        parsed_base_url = urlparse(base_url)
        parsed_link = urlparse(link)
        
        return parsed_base_url.netloc != parsed_link.netloc
        
    
    
    def get_links_from_url(self, url, max_links=5):
        """Looks for links on the URL, Filters them """
        #search_start=time.time()
        try: 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
                
                # Add any other headers you need
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            # Check the content type of the response
            content_type = response.headers.get('content-type', '').split(';')[0]
            if content_type not in self.ALLOWED_CONTENT_TYPES:
                # print(f"Skipped {url} (Content type: {content_type})")
                return []
            # Check the file size
            if 'content-length' in response.headers:
                file_size = int(response.headers['content-length'])
                if file_size > self.MAX_FILE_SIZE_BYTES:
                    #print(f"Skipped {url} (File size: {file_size} bytes)")
                    return []

            soup = BeautifulSoup(response.content, 'html.parser')

            base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
            links = set()

            for link in soup.find_all('a', href=True):
                absolute_link = urljoin(base_url, link['href'])
                
                # Skip links leading to forms (typically POST requests)
                if 'form' in absolute_link.lower():
                    #print("Link contains form: ",absolute_link)
                    continue

                # Skip links with a hash fragment (e.g., #section) on the same site
                if '#' in absolute_link:
                    #print("Link contains fragment: ",absolute_link)
                    continue
                    parsed_link = urlparse(absolute_link)
                    absolute_link = parsed_link.scheme + "://" + parsed_link.netloc + parsed_link.path
                    

                # Skip links to different subdomains
                if self.is_external_link(base_url, absolute_link):
                    #print("Link is external: ",absolute_link)
                    continue                
                links.add(absolute_link)
                
                if len(links) >= max_links:
                    break
            #search_duration=time.time()-search_start
            #print("Link search duration: ", search_duration)
            return list(links)
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while getting links from {url}: {e}")
            return []

    def is_link_working(self, link):
        """Checks if a link is returning a 200 Resonsecode"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',

            }
            response = requests.head(link, headers=headers)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def crawl_and_check_links(self, start_url, max_working_links, max_attempts=10):
        """Crawls to through domain, starting at the host_url and tries to get max working links, digs deeper into the website,  stops after max_attemps"""
        #Initialise Variables
        #starttime=time.time()
        visited = set()
        links_to_check = [start_url]
        working_links = []
        rounds=0
        # Loop through the page, until desired count of links are found, or no links are avaible
        while links_to_check and len(working_links) < max_working_links and rounds<max_attempts:            
            url = links_to_check.pop()
            visited.add(url)
            try:
                links = self.get_links_from_url(url, 5 * max_working_links)
            except Exception as e:
                print(f"An error occurred when fetching links from {url}: {e}")
            # Optionally, you can log the error or perform other error handling here.
            #check_time=time.time()
            for link in links:
                #maintain visited and links to check list
                if link not in visited and link not in links_to_check:
                    links_to_check.append(link)
                #Check if link is working
                if self.is_link_working(link):
                    working_links.append(link)
                    if len(working_links)>=max_working_links:
                        break

            #check_duration=time.time()-check_time
            #print("Round:", rounds," Checktime: ", check_duration)
            rounds+=1
        #duration=time.time()-starttime
        #print("Duration: ", duration)
        #print("Rounds: ",rounds)
        return working_links

    def get_paths(self, domain, port, link_count, max_attempts, time_out):
        """Get a number of valid paths for domain"""
        if port==443:
            scheme_domain="https://"+domain
        elif port==80:
            scheme_domain="https://"+domain
        else:
            scheme_domain=domain

        paths=[]
        paths.append("")
        if link_count==0:
            return paths
        start_time=time.time()
        try:
            while start_time-time.time()<time_out*link_count:
                working_links=self.crawl_and_check_links(scheme_domain, link_count, max_attempts)
        except Exception as e:
            print("Error during Crawling for links:",e)
            return paths
        
        for entry in working_links:
                parsed_link = urlparse(entry)
                paths.append(parsed_link.path)

        return paths


if __name__ == '__main__':
    
    target_url = "https://www.google.com"  # Change this to the target URL
    max_links_to_return = 5
    max_attempts = 5
    crawler=host_crawler()
    working_links = crawler.crawl_and_check_links(target_url, max_links_to_return, max_attempts)

    print("Working Links:")
    for link in working_links:
        print(link)