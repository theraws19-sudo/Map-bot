import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        """Создает карту мира с отмеченными городами"""
        # Создаем фигуру с проекцией PlateCarree
        fig, ax = plt.subplots(figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        
        # Добавляем географические объекты
        ax.coastlines()
        ax.add_feature(plt.matplotlib.patches.Rectangle((0, 0), 1, 1, 
                      transform=ax.transAxes, facecolor='lightblue', alpha=0.3))
        
        # Устанавливаем глобальные границы
        ax.set_global()
        
        # Отмечаем города на карте
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                # Добавляем точку города
                ax.plot(lng, lat, 'ro', markersize=8, transform=ccrs.PlateCarree(), 
                       marker='o', markerfacecolor='red', markeredgecolor='darkred', 
                       markeredgewidth=1.5)
                # Добавляем подпись города
                ax.text(lng, lat, f'  {city}', transform=ccrs.PlateCarree(),
                       fontsize=9, verticalalignment='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Добавляем сетку координат
        ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
        
        # Сохраняем карту
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return path
        
    def draw_distance(self, city1, city2):
        """Рисует карту с двумя городами и линией между ними"""
        from math import radians, cos, sin, asin, sqrt
        
        # Получаем координаты городов
        coords1 = self.get_coordinates(city1)
        coords2 = self.get_coordinates(city2)
        
        if not coords1 or not coords2:
            return None
        
        lat1, lng1 = coords1
        lat2, lng2 = coords2
        
        # Вычисляем расстояние по формуле гаверсинусов
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Радиус Земли в километрах
        distance = c * r
        
        # Создаем карту
        fig, ax = plt.subplots(figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.coastlines()
        ax.set_global()
        
        # Отмечаем города
        lat1_deg, lng1_deg = coords1
        lat2_deg, lng2_deg = coords2
        
        ax.plot(lng1_deg, lat1_deg, 'go', markersize=10, transform=ccrs.PlateCarree(),
               marker='o', markerfacecolor='green', markeredgecolor='darkgreen', markeredgewidth=2)
        ax.text(lng1_deg, lat1_deg, f'  {city1}', transform=ccrs.PlateCarree(),
               fontsize=10, verticalalignment='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))
        
        ax.plot(lng2_deg, lat2_deg, 'bo', markersize=10, transform=ccrs.PlateCarree(),
               marker='o', markerfacecolor='blue', markeredgecolor='darkblue', markeredgewidth=2)
        ax.text(lng2_deg, lat2_deg, f'  {city2}', transform=ccrs.PlateCarree(),
               fontsize=10, verticalalignment='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
        
        # Рисуем линию между городами
        ax.plot([lng1_deg, lng2_deg], [lat1_deg, lat2_deg], 'r-', 
               linewidth=2, transform=ccrs.PlateCarree(), alpha=0.6)
        
        # Добавляем подпись с расстоянием в центре линии
        mid_lng = (lng1_deg + lng2_deg) / 2
        mid_lat = (lat1_deg + lat2_deg) / 2
        ax.text(mid_lng, mid_lat, f'{distance:.0f} км', transform=ccrs.PlateCarree(),
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
        
        ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)
        
        path = f'distance_{city1}_{city2}.png'
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return path, distance


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()