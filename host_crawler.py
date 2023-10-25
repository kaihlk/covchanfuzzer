###Host_Crawler###
import requests
import time
import os
import concurrent.futures
from bs4 import BeautifulSoup
import http1_request_builder as request_builder
from custom_http_client import CustomHTTP
from urllib.parse import urlparse, urljoin, urlsplit

class host_crawler:
        
    def __init__(self, experiment_configuration, exp_log_folder):
        
        #domain, links_to_return, max_attempts
        #self.link_to_return=link_to_return
        #self.max_attempts=max_attempts
        
        self.timeout=5
        #os.environ["SSLKEYLOGFILE"] = "secrets.log"
        self.experiment_configuration=experiment_configuration
        self.exp_log_folder=exp_log_folder+"/crawl"
        os.makedirs(self.exp_log_folder, exist_ok=True)

    
    def is_external_link(self, base_url, link):
        """Check if the link points to a different subdomain or an external domain"""
        parsed_base_url = urlparse(base_url)
        parsed_link = urlparse(link)
        
        return parsed_base_url.netloc != parsed_link.netloc
        
    
    
    def get_links_from_url(self, url, max_links=5):
        """Looks for links on the URL, Filters them """
        #search_start=time.time()
        ALLOWED_CONTENT_TYPES = {'text/html', 'text/plain'}
        MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
        try: 
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1", 
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1", 
                "Sec-Fetch-Dest": "document", 
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "cross-site",
            }
            print("Crawler: ",url)
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            # Check the content type of the response
            content_type = response.headers.get('content-type', '').split(';')[0]
            if content_type not in ALLOWED_CONTENT_TYPES:
                # print(f"Skipped {url} (Content type: {content_type})")
                return []
            # Check the file size
            if 'content-length' in response.headers:
                file_size = int(response.headers['content-length'])
                if file_size > MAX_FILE_SIZE_BYTES:
                    #print(f"Skipped {url} (File size: {file_size} bytes)")
                    return []

            soup = BeautifulSoup(response.content, 'html.parser')
            parsed_url = urlparse(url)
            base_url = parsed_url.scheme + "://" + parsed_url.netloc
            original_path = parsed_url.path
            links = set()
            visited_links = set() 

            for link in soup.find_all('a', href=True):
               
                # Split the URL to separate the path from query string
                parsed_link = urlsplit(link['href'])
                path = '/'  # Set the default path to '/' shortest path
                if parsed_link.path:
                    path = parsed_link.path
                absolute_link = urljoin(base_url, path)  # Use the path component

                # Skip links leading to forms (typically POST requests)
                if 'form' in absolute_link.lower():
                    #print("Link contains form: ",absolute_link)
                    continue

                # Skip links with a hash fragment (e.g., #section) on the same site
                if '#' in absolute_link:
                    #print("Link contains fragment: ",absolute_link)
                    continue
                if absolute_link in visited_links:
                    continue
                visited_links.add(absolute_link) 
                # Skip links to different subdomains
                if self.is_external_link(base_url, absolute_link):
                    #print("Link is external: ",absolute_link)
                    continue                
                links.add(absolute_link)
                if len(links) >= max_links:
                    break
            filtered_links = set()
            for link in links:
                if original_path and original_path in link:
                    filtered_links.add(link)
            if filtered_links:
                links = filtered_links
   
            sorted_links = sorted(list(links), key=len)
            return sorted_links[:max_links]
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while getting links from {url}: {e}")
            return []

    def is_link_working(self, link):
        """Checks if a link is returning a 200 Resonsecode"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1", 
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1", 
                "Sec-Fetch-Dest": "document", 
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "cross-site",
            }
            response = requests.get(link, headers=headers, timeout=self.timeout)
            print("Link: "+ link +" response code: "+str(response.status_code))
            return 200 <= response.status_code < 300
        except requests.exceptions.Timeout as e:
            print(f"Timeout occurred while checking the link {link}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking the link {link}: {e}")
            return False

    def is_working_custom(self, link):
        """Checks if a link is returning a 200 Resonsecode"""
        try:
            host=urlparse(link).netloc
            request_string, _deviation_count, new_uri = request_builder.HTTP1_Request_Builder().generate_request(self.experiment_configuration, self.experiment_configuration["target_port"])
            #Replace Placeholders
            request, _deviation_count, _new_uri = request_builder.HTTP1_Request_Builder().replace_host_and_domain(request_string, link, self.experiment_configuration["standard_subdomain"], host, self.experiment_configuration["include_subdomain_host_header"], path="/")
            #Send request
            print(host)
            response_line, _response_header_fields, _body, _measured_times, _error_messages  = CustomHTTP().http_request(
                host=host,
                use_ipv4=self.experiment_configuration["use_ipv4"],
                port=self.experiment_configuration["target_port"],
                host_ip_info=None,
                custom_request=request,
                timeout=self.experiment_configuration["conn_timeout"],
                verbose=self.experiment_configuration["verbose"],
                log_path=None,    #Transfer to save TLS Keys
                )
            if response_line is not None:
                print(response_line)
                response_status_code = response_line["status_code"]
                first_digit=int(str(response_status_code)[0])
                if first_digit==2:
                    return True
            else:
                return False
        except requests.exceptions.Timeout as e:
            print(f"Timeout occurred while checking the link {link}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking the link {link}: {e}")
            return False

    def crawl_and_check_links(self, start_url, max_working_links, max_attempts=10):
        """Crawls to through domain, starting at the host_url and tries to get max working links, digs deeper into the website,  stops after max_attemps"""
        working_links = []
        try:
            links = self.get_links_from_url(start_url, 10 * max_working_links)
        except Exception as e:
            print(f"An error occurred when fetching links from {start_url}: {e}")
        print("Found links:", links)
        for link in links:
            try:
                if self.is_working_custom(link):
                    working_links.append(link)
                if len(working_links) >= max_working_links:
                    break
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while checking the link {link}: {e}")
        return working_links
    
    #def crawl_and_check_links(self, start_url, max_working_links, max_attempts=10):
        """Crawls to through domain, starting at the host_url and tries to get max working links, digs deeper into the website,  stops after max_attemps"""
        """       #Initialise Variables
        #starttime=time.time()
        visited = set()
        links_to_check = [start_url]
        working_links = []
        rounds=0
        # Loop through the page, until desired count of links are found, or no links are avaible
        while links_to_check and len(working_links) < max_working_links and rounds<max_attempts:            
            url = links_to_check.pop()
            
            try:
                links = self.get_links_from_url(url, 5 * max_working_links)
            except Exception as e:
                print(f"An error occurred when fetching links from {url}: {e}")
                rounds+=1
                continue
            visited.add(url)
            # Optionally, you can log the error or perform other error handling here.
            #check_time=time.time()
            print("Found links:", links)
            if len(links)==0: break
            for link in links:
                #maintain visited and links to check list
                if link not in visited and link not in links_to_check:
                    links_to_check.append(link)
                #Check if link is working
                try:
                    #if self.is_link_working(link):
                    if self.is_working_custom(link):
                        working_links.append(link)
                        if len(working_links) >= max_working_links:
                            break
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred while checking the link {link}: {e}")
                    rounds+=1
            rounds+=1
            #check_duration=time.time()-check_time
            #print("Round:", rounds," Checktime: ", check_duration)
            
        #duration=time.time()-starttime
        #print("Duration: ", duration)
        #print("Rounds: ",rounds)
        return working_links """

    def get_paths(self, domain, port, link_count, max_attempts, timeout):
        """Get a number of valid paths for domain"""
        self.timeout=timeout
        if "://" not in domain:
            if port==443:
                uri="https://"+domain
            elif port==80:
                uri="https://"+domain
        else:
            uri=domain

        paths=[]
        
        if link_count==0:
            return paths
        working_links=None
        try:
            working_links=self.crawl_and_check_links(uri, link_count, max_attempts)
        except Exception as e:
            # Log and handle other exceptions
            print(f"An error occurred during crawling: {e}")
            working_links = []
                
        """ try:
            with concurrent.futures.ThreadPoolExecutor() as executor2:
                future = executor2.submit(self.crawl_and_check_links, uri, link_count, max_attempts)
                working_links = future.result(timeout=timeout*link_count)
        except concurrent.futures.TimeoutError:
            print(f"Crawling for links exceeded timeout of {timeout*link_count} seconds.")
            working_links = []
        except Exception as e:
            # Log and handle other exceptions
            print(f"An error occurred during crawling: {e}")
            working_links = [] """


        for entry in working_links:
                parsed_link = urlparse(entry)
                paths.append(parsed_link.path)
        
        if len(paths)==0:
            paths.append("/")
    
        print("paths",paths)

        return paths


if __name__ == '__main__':
    

    experiment_configuration = {
        "experiment_no": 1,
        "comment": "description",
        "verbose": False,
        "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        # Covert Channel Option
        "covertchannel_request_number":31,
        "covertchannel_connection_number": 1,
        "covertchannel_timing_number": 1,
        "min_fuzz_value": 0.01,
        "spread_deviation": 0.9,
        # Target Selection Options
        "num_attempts": 10,
        "max_targets": 100,  # len(self.target_list):
        "max_workers": 1,  # Parallel Processing of subsets,
        "wait_between_request": 0,
        "base_line_check_frequency": 0,
        "check_basic_request": 1,

        # "target_list_subdomain_10000.csv",#"new_target_list.csv",
        "target_list": "target_list_subdomain_10000.csv",

        "target_subset_size": 10,
        "target_add_www": True,  # Add www if no other subdomain is known
        # "target_host": "www.example.com",  #Just for special useipvstt
        "target_port": 443,  # 443, 8080 Apache
        # Connection Options
        "conn_timeout": 5,  # seconds
        "nw_interface": "enp0s3",#"enp0s31f6",#"enp0s3",#s31f6#0s3",#31f6",#1s6",  # lo, docker, enp0s3
        "use_ipv4": True,
        "use_TLS": True,
        "use_HTTP2": False,

        # HTTP Message Options
        "HTTP_version": "HTTP/1.1",
        "method": "GET",
        "url": "",  # Complete URl
        "follow_redirects": 1, #Follow the first redirect if provided
        "path": "/",  # Dynamic, List, ?s
        "crawl_paths": 5, #(dafault 0 )

        "standard_subdomain": "www",  # use www if not provided
        # build a relative uri without the host in the requestline: /index.html
        "relative_uri": False,
        # include the subdomain, when building requestline, if none given use <standard_subdomain>
        "include_subdomain": True,  #Check maybe drop
        "include_port": False,
        "include_subdomain_host_header": True,
        "headers": None,
        # curl_HTTP/1.1(TLS), firefox_HTTP/1.1, firefox_HTTP/1.1_TLS, chromium_HTTP/1.1, chromium_HTTP/1.1_TLS"
        "standard_headers": "firefox_HTTP/1.1_TLS",
        "content": "random",  # "random", "some_text""fuzz_value": 0.9,
        "ip":0,
     
    }

    resp=requests.get("https://barnesandnoble.com")
    print(resp.headers)

    target_url = "https://www.microsoft.com/de-de/"  # Change this to the target URL
    max_links_to_return = 5
    max_attempts = 5
    crawler=host_crawler(experiment_configuration, "/home/kai/git/logs/experiment_91/")
    working_links = crawler.crawl_and_check_links(target_url, max_links_to_return, max_attempts)

    print("Working Links:")
    for link in working_links:
        print(link)