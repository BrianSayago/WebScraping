import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
from pymongo import MongoClient


class MongoDBManager:
    def __init__(self, db_name, collection_name):
        self.client = MongoClient("mongodb://localhost:27017/")  
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def upsert_product(self, product):
        existing_product = self.collection.find_one({"link": product["link"]})
        
        #Producto existente
        if existing_product:
            if existing_product["precio_actual"] != product["precio_actual"]:
                historial = existing_product.get("historial_precios", [])
                historial.append({
                    "precio": existing_product["precio_actual"],
                    "fecha": existing_product["ultima_actualizacion"]
                })

                # Actualizar producto en bd
                self.collection.update_one(
                    {"_id": existing_product["_id"]},
                    {
                        "$set": {
                            "precio_actual": product["precio_actual"],
                            "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                            "historial_precios": historial
                        }
                    }
                )
                print(f"Producto actualizado: {product['titulo']}")
            else:
        
                print(f"Producto sin cambios: {product['titulo']}")
        #Producto nuevo         
        else:
            product["historial_precios"] = []
            product["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d")
            self.collection.insert_one(product)
            print(f"Producto nuevo insertado: {product['titulo']}")           

    def close_connection(self):
        self.client.close()          

class MercadoLibreScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        self.base_url = "https://listado.mercadolibre.com.ar"

    def get_page(self, url):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 2))
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Error en intento {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise

    def parse_product(self, product_element):
        try:
            # Titulo
            title_element = product_element.find('h2', {'class': 'poly-box poly-component__title'})
            title = title_element.a.text.strip() if title_element and title_element.a else None

            # Precio
            price_element = product_element.find('span', {'class': 'andes-money-amount__fraction'}) or \
                            product_element.find('div', {'class': 'price__fraction'})
            price = price_element.text.strip() if price_element else None

            # Marca
            brand_element = product_element.find('span', {'class': 'poly-component__brand'})
            brand = brand_element.text.strip() if brand_element else "No especificada"

            # Link 
            link_element = product_element.find('a')
            link = link_element['href'] if link_element and 'href' in link_element.attrs else None

            if not title or not price:
                print(f"Datos incompletos encontrados en producto: Título={title}, Precio={price}")
                return None

            return {
                'titulo': title,
                'precio': price,
                'marca': brand,
                'link': link if link else "No disponible",
                'fecha_scraping': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Error al procesar producto: {e}")
            return None

    def scrape_category(self, category_url, num_pages=1):
        all_products = []
        current_url = category_url
        
        for page in range(1, num_pages + 1):
            try:
                print(f"\nProcesando página {page}...")
                html = self.get_page(current_url)
                soup = BeautifulSoup(html, 'html.parser')
                
                #Busca todos los productos
                products = soup.find_all('div', {'class': 'poly-card poly-card--list'})
                
                print(f"Productos encontrados en página {page}: {len(products)}")
                
                for product in products:
                    product_data = self.parse_product(product)
                    if product_data:
                        all_products.append(product_data)
                        print(f"Producto procesado: {product_data['titulo'][:50]}...")
                
                #Siguiente pagina
                next_page = soup.find('a', {'title': 'Siguiente'}) or \
                           soup.find('a', {'class': 'andes-pagination__link'}, text='Siguiente')
                
                if next_page and page < num_pages:
                    current_url = next_page['href']
                    print(f"URL siguiente página: {current_url}")
                else:
                    break
                
            except Exception as e:
                print(f"Error en página {page}: {e}")
                continue
        
        return pd.DataFrame(all_products)

    def save_results(self, df, filename):
        try:
            if df.empty:
                print("No hay datos para guardar")
                return
                
            df.to_csv(f"{filename}.csv", index=False, encoding='utf-8-sig')
            df.to_excel(f"{filename}.xlsx", index=False)
            print(f"Resultados guardados en {filename}.csv y {filename}.xlsx")
        except Exception as e:
            print(f"Error al guardar resultados: {e}")

def main():
    try:
        scraper = MercadoLibreScraper()
        db_manager = MongoDBManager(db_name="mercadolibre_db", collection_name="notebooks")
        
        category_url = "https://listado.mercadolibre.com.ar/notebook"
        
        # Iniciar scraping
        print("Iniciando scraping...")
        results = scraper.scrape_category(category_url, num_pages=2)
        
        # Guardar resultados
        scraper.save_results(results, 'notebooks_mercadolibre')

        if not results.empty:
            print(f"\nTotal de productos encontrados: {len(results)}")
            print("\nGuardando en la base de datos...")

        # Guardar resultados en MongoDB
            documents = results.to_dict("records")  # Convertir el DataFrame a una lista de diccionarios
            for product in documents:
                db_manager.upsert_product(product)
            
            print("Productos procesados y guardados en MongoDB.")
        else:
            print("\nNo se encontraron productos para guardar.")

        if not results.empty:
            print("\nPrimeros 5 productos:")
            print(results.head())
        else:
            print("\nNo se encontraron productos")      
            
    except Exception as e:
        print(f"Error en la ejecución principal: {e}")

        

if __name__ == "__main__":
    main()