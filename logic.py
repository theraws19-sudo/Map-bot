import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import io


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

    def add_city(self, user_id, city_name):
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

    def create_graph(self, cities):
        """
        Создаёт карту мира с отмеченными городами.
        Принимает список названий городов.
        Возвращает объект BytesIO с PNG-изображением.
        """
        fig = plt.figure(figsize=(14, 8))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Добавляем базовые слои карты
        ax.add_feature(cfeature.LAND, facecolor='#f5f5dc')
        ax.add_feature(cfeature.OCEAN, facecolor='#aadaff')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.4)
        ax.set_global()

        if not cities:
            ax.set_title('Нет городов для отображения', fontsize=14)
        else:
            coords = []
            for city in cities:
                result = self.get_coordinates(city)
                if result:
                    lat, lng = result
                    coords.append((city, lat, lng))

            if coords:
                lats = [c[1] for c in coords]
                lngs = [c[2] for c in coords]

                ax.scatter(lngs, lats, color='red', s=60,
                           transform=ccrs.PlateCarree(), zorder=5)

                for city, lat, lng in coords:
                    ax.text(lng + 1, lat + 1, city, fontsize=8,
                            transform=ccrs.PlateCarree(), zorder=6,
                            bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.2'))

                title = cities[0] if len(cities) == 1 else f'Города на карте ({len(cities)} шт.)'
                ax.set_title(title, fontsize=14)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close(fig)
        buf.seek(0)
        return buf

    def draw_distance(self, city1, city2):
        pass


if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
