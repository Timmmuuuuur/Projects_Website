from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import Project
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import NewUserForm, AddressInputForm, UniAdminForm, PortfolioAuthenticationForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from math import cos, asin, sqrt
import pandas as pd
import numpy as np
import pickle
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset = pd.read_csv(os.path.join(BASE_DIR, "main/binary.csv"))

# Cache file for geocoding results
GEOCODE_CACHE_FILE = os.path.join(BASE_DIR, "geocode_cache.json")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# C:\Users\idaul\OneDrive\Desktop\djangoMigration\main\views.py
# C:\Users\idaul\OneDrive\Desktop\djangoMigration\main\binary.csv
# Create your views here.
def homepage(request):
    return render(
        request = request, template_name='main/home.html',
        context={'projects':Project.objects.all()}
    )


def resume_download(request):
    """
    Prefer PDF if you add one under main/static/main/.
    Otherwise serve the canonical text resume (synced from your latest CV — cv_timur_dauletov.txt).
    """
    pdf_paths = [
        os.path.join(BASE_DIR, "main", "static", "main", "resume.pdf"),
        os.path.join(BASE_DIR, "main", "static", "main", "Timur_Dauletov_Resume.pdf"),
    ]
    for path in pdf_paths:
        if os.path.isfile(path):
            return FileResponse(
                open(path, "rb"),
                as_attachment=True,
                filename="Timur_Dauletov_Resume.pdf",
            )

    txt_path = os.path.join(BASE_DIR, "main", "static", "main", "cv_timur_dauletov.txt")
    if os.path.isfile(txt_path):
        return FileResponse(
            open(txt_path, "rb"),
            as_attachment=True,
            filename="Timur_Dauletov_Resume.txt",
            content_type="text/plain; charset=utf-8",
        )

    return redirect("https://www.linkedin.com/in/timur-dauletov")

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            messages.success(request, f"New account created: {username}")
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "main/register.html",
                          context={"form":form})

    form = NewUserForm
    return render(request = request,
                  template_name = "main/register.html",
                  context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")

def login_request(request):
    if request.method == 'POST':
        form = PortfolioAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('main:homepage')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = PortfolioAuthenticationForm()
    return render(request=request,
                  template_name="main/login.html",
                  context={"form":form})

def print_request(request):


    form = AddressInputForm(request.POST)
    if form.is_valid():
        try:
            vehicle_count = int(form.cleaned_data['vehicle_count'])
        except ValueError:
            messages.error(request, "Please enter a valid number of addresses")
            return render(request, "main/vrp.html", context={"form": form})

        address_string = form.cleaned_data['address_string'].split(";")

        def minIgnoringVisited(distArray, visited):
            """Optimized: Find minimum distance to unvisited city"""
            minValue = float('inf')
            minKey = -1
            for i in range(len(distArray)):
                if i not in visited and distArray[i] < minValue and distArray[i] > 0:
                    minValue = distArray[i]
                    minKey = i
            return minKey, minValue

        def geocode_with_osm_nominatim(address):
            """
            Geocode address using OpenStreetMap's Nominatim API
            Returns (address, (lat, lon)) tuple or (address, None) if failed
            """
            try:
                # OpenStreetMap Nominatim API - free and open source
                # Searches OSM's database for address and returns coordinates
                url = f"https://nominatim.openstreetmap.org/search"
                params = {
                    'q': address,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'ca'  # Prioritize Canadian addresses
                }
                headers = {
                    'User-Agent': 'VRP-Optimizer/1.0'  # Required by Nominatim
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return (address, (lat, lon))
                return (address, None)
                
            except Exception as e:
                return (address, None)

        def load_geocode_cache():
            """Load cached geocoding results from disk"""
            try:
                if os.path.exists(GEOCODE_CACHE_FILE):
                    with open(GEOCODE_CACHE_FILE, 'r') as f:
                        return json.load(f)
            except:
                pass
            return {}
        
        def save_geocode_cache(cache):
            """Save geocoding results to disk cache"""
            try:
                with open(GEOCODE_CACHE_FILE, 'w') as f:
                    json.dump(cache, f, indent=2)
            except:
                pass

        def getCoordinatesFromCsv(incomingDocument):
            """
            Get coordinates for addresses using OpenStreetMap Nominatim API with caching
            Falls back to Selenium web scraping if OSM fails, then to demo data
            """
            one = [j for i in incomingDocument for j in i]
            coords = {}
            osm_success_count = 0
            cache_hit_count = 0

            # Load cache
            cache = load_geocode_cache()
            
            # Check cache first
            addresses_to_geocode = []
            for address in one:
                if address in cache and cache[address] is not None:
                    coords[address] = cache[address]
                    cache_hit_count += 1
                else:
                    addresses_to_geocode.append(address)
                    coords[address] = None
            
            if cache_hit_count > 0:
                messages.success(request, f"💾 Loaded {cache_hit_count} addresses from cache")
            
            # Only geocode addresses not in cache
            if addresses_to_geocode:
                messages.info(request, f"🗺️ Geocoding {len(addresses_to_geocode)} new addresses with OpenStreetMap...")
                
                # Use ThreadPoolExecutor for concurrent requests
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = {
                        executor.submit(geocode_with_osm_nominatim, address): address 
                        for address in addresses_to_geocode
                    }
                    
                    for future in as_completed(futures):
                        address, result = future.result()
                        if result:
                            coords[address] = list(result)
                            cache[address] = list(result)  # Save to cache
                            osm_success_count += 1
                
                # Save updated cache
                if osm_success_count > 0:
                    save_geocode_cache(cache)
                    messages.success(request, f"✅ OpenStreetMap geocoded {osm_success_count} new addresses")
            else:
                messages.success(request, f"⚡ All addresses loaded from cache - instant results!")

            # Secondary Method: Selenium fallback for failed addresses
            failed_addresses = [addr for addr, coord in coords.items() if coord is None]
            
            if failed_addresses:
                messages.info(request, f"🔄 Trying Selenium fallback for {len(failed_addresses)} addresses...")
                selenium_success_count = 0
                try:
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--window-size=1920,1080")
                    
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.set_page_load_timeout(30)
                    url = "https://geocoder.ca/"

                    for address in failed_addresses:
                        try:
                            driver.get(url)
                            elem = WebDriverWait(driver, 15).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'input-block-level'))
                            )
                            elem.clear()
                            elem.send_keys(address)

                            second = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="geocode"]/input[2]'))
                            )
                            second.click()
                            
                            try:
                                result_elem = WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/table[2]/tbody/tr/td[2]/p/strong'))
                                )
                                result_text = result_elem.get_attribute('innerHTML')
                                coords[address] = [float(j) for j in result_text.split(", ")]
                                selenium_success_count += 1
                            except:
                                pass  # Will use demo coordinates
                                
                        except Exception as e:
                            pass  # Will use demo coordinates
                            
                    driver.quit()
                    
                    if selenium_success_count > 0:
                        messages.success(request, f"✅ Selenium geocoded {selenium_success_count} additional addresses")
                    
                except Exception as e:
                    messages.warning(request, "⚠️ Selenium fallback unavailable")

            # Final fallback: Demo coordinates for any remaining failures
            demo_count = 0
            for i, (addr, coord) in enumerate(coords.items()):
                if coord is None:
                    coords[addr] = [43.65 + (i * 0.02), -79.38 + (i * 0.02)]
                    demo_count += 1
            
            if demo_count > 0:
                messages.warning(request, f"⚠️ Using demo coordinates for {demo_count} addresses")
            
            return coords

        # print(getCoordinatesFromCsv("waterlooWebScrapingTest.csv"))

        def distance(lat1, lon1, lat2, lon2):
            """Vectorized Haversine distance calculation"""
            p = 0.017453292519943295  # Pi/180
            a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
            return 12742 * asin(sqrt(a))  # 2*R*asin...

        def distanceMatrix(coords):
            """Optimized distance matrix calculation using symmetry"""
            n = len(coords)
            distMatrix = np.zeros((n, n))
            coord_list = list(coords.items())
            
            # Only calculate upper triangle (matrix is symmetric)
            for i in range(n):
                for j in range(i + 1, n):
                    dist = distance(
                        coord_list[i][1][0], coord_list[i][1][1],
                        coord_list[j][1][0], coord_list[j][1][1]
                    )
                    distMatrix[i][j] = dist
                    distMatrix[j][i] = dist  # Symmetric
            
            return distMatrix, [addr for addr, _ in coord_list]

        def nearestNeighborVRP(numVehicles, depotLocation, distanceMatrix):
            """Optimized greedy nearest-neighbor VRP solver"""
            n = len(distanceMatrix)
            visited = {depotLocation}  # Use set for O(1) lookup
            routes = [[depotLocation] for _ in range(numVehicles)]
            distances = [0.0] * numVehicles
            
            # Assign cities to vehicles in round-robin fashion
            cities_to_visit = n - 1  # Exclude depot
            
            for i in range(cities_to_visit):
                vehicle_idx = i % numVehicles
                current_loc = routes[vehicle_idx][-1]
                
                # Find nearest unvisited city
                next_city, dist = minIgnoringVisited(distanceMatrix[current_loc], visited)
                
                if next_city != -1:
                    routes[vehicle_idx].append(next_city)
                    visited.add(next_city)
                    distances[vehicle_idx] += dist
            
            # Return to depot
            for i in range(numVehicles):
                if len(routes[i]) > 1:  # Only if vehicle visited any cities
                    last_city = routes[i][-1]
                    distances[i] += distanceMatrix[last_city][depotLocation]
                    routes[i].append(depotLocation)

            return routes, distances

        def routeVisualization(pointerStorage, totalDistanceStorage, locationAddresses, coordinatesDict):
            """Generate Google Maps URLs for each vehicle route"""
            urls = []
            route_details = []

            for vehicle_idx, vehicles in enumerate(pointerStorage):
                # Modern Google Maps URL format using coordinates
                waypoints = []
                
                for loc_idx in vehicles:
                    addr = locationAddresses[loc_idx]
                    # Use coordinates for more reliable routing
                    if addr in coordinatesDict:
                        lat, lon = coordinatesDict[addr]
                        waypoints.append(f"{lat},{lon}")
                
                if len(waypoints) >= 2:
                    # Create URL with origin, destination, and waypoints
                    origin = waypoints[0]
                    destination = waypoints[-1]
                    
                    if len(waypoints) > 2:
                        middle_points = waypoints[1:-1]
                        waypoints_param = "|".join(middle_points)
                        mapURL = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints_param}&travelmode=driving"
                    else:
                        mapURL = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
                    
                    urls.append(mapURL)
                    
                    # Create human-readable route description
                    route_desc = f"Vehicle {vehicle_idx + 1} Route ({totalDistanceStorage[vehicle_idx]:.2f} km):<br>"
                    for loc_idx in vehicles:
                        route_desc += f"→ {locationAddresses[loc_idx]}<br>"
                    route_details.append(route_desc)
                    
            return urls, route_details

        # Get coordinates for all addresses
        start_time = time.time()
        
        coords = getCoordinatesFromCsv([address_string])
        geocoding_time = time.time() - start_time
        
        matrix_start = time.time()
        globalDistanceMatrix, allAddresses = distanceMatrix(coords)
        matrix_time = time.time() - matrix_start
        
        route_start = time.time()
        vehiclesVisited, allDistances = nearestNeighborVRP(vehicle_count, 0, globalDistanceMatrix)
        route_time = time.time() - route_start
        
        # Show timing info
        messages.info(request, mark_safe(
            f"⏱️ Performance: Geocoding: {geocoding_time:.1f}s | "
            f"Matrix: {matrix_time:.2f}s | Routing: {route_time:.2f}s"
        ))

        urls, route_details = routeVisualization(
            pointerStorage=vehiclesVisited, 
            totalDistanceStorage=allDistances,
            locationAddresses=allAddresses,
            coordinatesDict=coords
        )

        messages.success(request, f"✅ Route optimization complete! Calculated routes for {vehicle_count} vehicle(s).")
        
        # Prepare route data for interactive map visualization
        route_data = {
            "routes": []
        }
        
        for vehicle_idx, vehicle_route in enumerate(vehiclesVisited):
            if len(vehicle_route) >= 2:
                route_info = {
                    "coordinates": [],
                    "addresses": [],
                    "distance": allDistances[vehicle_idx]
                }
                
                # Collect coordinates and addresses for this route
                for loc_idx in vehicle_route:
                    address = allAddresses[loc_idx]
                    if address in coords:
                        lat, lon = coords[address]
                        route_info["coordinates"].append([lat, lon])
                        route_info["addresses"].append(address)
                
                route_data["routes"].append(route_info)
        
        for i in range(len(urls)):
            # Show route details
            messages.warning(request, mark_safe(route_details[i]))
            # Show clickable Google Maps link
            messages.info(request, mark_safe(f'<a href="{urls[i]}" target="_blank" style="color: white; text-decoration: underline; font-weight: bold;">🗺️ Open Vehicle {i+1} Route in Google Maps</a>'))
        
        # Pass route data as JSON to template
        import json
        return render(request, "main/vrp.html", context={
            "form": form,
            "route_data_json": json.dumps(route_data)
        })
        
    return render(request, "main/vrp.html", context={"form":form})

def admission_prob_request(request):
    form = UniAdminForm(request.POST)
    train_class = True
    if form.is_valid():
        try:
            gre = float(form.cleaned_data['gre'])
            gpa = float(form.cleaned_data['gpa'])
            rank = int(form.cleaned_data['rank'])
        except ValueError:
            messages.error(request, "Please make sure all the data you enter is valid")
            return render(request, "main/uni_admin.html", context={"form": form})

        # convert dataframe into matrix
        if train_class:
            dataArray = dataset.values

            # splitting input features & o/p vars
            X = dataArray[:, 1:4]
            y = dataArray[:, 0:1]

            # splitting training & testing
            validation_size = 0.10
            seed = 9
            X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=validation_size, random_state=seed)


            # create prediction model
            model = LogisticRegression()

            # fit model
            model.fit(X_train, Y_train)
            filename = 'finalized_model.sav'
            pickle.dump(model, open(filename, 'wb'))


        # load the model from disk

        new_data = [(gre, gpa, rank)]

        new_array = np.asarray(new_data)
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
        prediction = loaded_model.predict_proba(new_array)[:, 1]

        # get no of test cases used
        no_of_test_cases, cols = new_array.shape

        # Message shooting the probs
        for i in range(no_of_test_cases):
            messages.warning(request,"The probability of getting into your institution of choice is {}".format(prediction[i]))

    return render(request, "main/uni_admin.html", context={"form":form})

def stock_analysis_request(request):
    """Stock analysis page - placeholder for now"""
    return render(request, "main/stocks.html", context={})