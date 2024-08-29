import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import matplotlib.cm as cm
import seaborn as sns
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from bokeh.models import HoverTool
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
import time
import scipy as sp
from pyvis.network import Network









# Verileri Yükleme
data = pd.read_csv("C:/Users/MONSTER/Downloads/listings.csv", nrows=500)

# Fiyat Aralığı Seçimi
min_price = st.sidebar.number_input("Minimum Fiyat", min_value=0, max_value=int(max(data["price"])), value=0)
max_price = st.sidebar.number_input("Maksimum Fiyat", min_value=int(min(data["price"])), max_value=int(max(data["price"])), value=int(max(data["price"])))

# Fiyat Aralığına Göre Veriyi Filtreleme
data_filtered = data[(data["price"] >= min_price) & (data["price"] <= max_price)]

# Grafiklerin Adları
graph_names = [
    "Oda Tipine Göre Dağılım",
    "Ev Sahibinin İnceleme Puanı ve Minimum Gece Sayısı İlişkisi",
    "Konuma Göre Ortalama Fiyat ve Minimum Gece Sayısı",
    "Fiyat ve İnceleme Puanı İlişkisi",
    "Bölgeye Göre Oda Sayısı ve Doluluk Durumu"
]

# Butonlar için döngü oluşturma
selected_graph = None
for graph_name in graph_names:
    if st.button(graph_name, key=f"{graph_name}_button"):
        selected_graph = graph_name

# Seçilen grafikleri gösterme
if selected_graph == "Oda Tipine Göre Dağılım":
    st.subheader("Oda Tipine Göre Dağılım")
    room_type_counts = data_filtered["room_type"].value_counts()
    fig, ax = plt.subplots()
    room_type_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")  # Y ekseni etiketini kaldırma
    ax.set_title("Oda Tipine Göre Dağılım")
    st.pyplot(fig)

elif selected_graph == "Ev Sahibinin İnceleme Puanı ve Minimum Gece Sayısı İlişkisi":
    st.subheader("Ev Sahibinin İnceleme Puanı ve Minimum Gece Sayısı İlişkisi")
    fig, ax = plt.subplots()
    ax.scatter(data_filtered["reviews_per_month"], data_filtered["minimum_nights"], alpha=0.5)
    ax.set_xlabel("İnceleme Puanı")
    ax.set_ylabel("Minimum Gece Sayısı")
    ax.set_title("Ev Sahibinin İnceleme Puanı ve Minimum Gece Sayısı İlişkisi")
    st.pyplot(fig)

elif selected_graph == "Konuma Göre Ortalama Fiyat ve Minimum Gece Sayısı":
    st.subheader("Konuma Göre Ortalama Fiyat ve Minimum Gece Sayısı")
    avg_price_min_nights = data_filtered.groupby("neighbourhood")[["price", "minimum_nights"]].mean()
    fig, ax = plt.subplots()
    avg_price_min_nights.plot(kind="bar", alpha=0.75, ax=ax)
    ax.set_xlabel("Konum")
    ax.set_ylabel("Ortalama Fiyat / Minimum Gece Sayısı")
    ax.set_title("Konuma Göre Ortalama Fiyat ve Minimum Gece Sayısı")
    st.pyplot(fig)

elif selected_graph == "Fiyat ve İnceleme Puanı İlişkisi":
    st.subheader("Fiyat ve İnceleme Puanı İlişkisi")
    fig, ax = plt.subplots()
    ax.scatter(data_filtered["price"], data_filtered["reviews_per_month"], alpha=0.5)
    ax.set_xlabel("Fiyat")
    ax.set_ylabel("İnceleme Puanı")
    ax.set_title("Fiyat ve İnceleme Puanı İlişkisi")
    st.pyplot(fig)

elif selected_graph == "Bölgeye Göre Oda Sayısı ve Doluluk Durumu":
    st.subheader("Bölgeye Göre Oda Sayısı ve Doluluk Durumu")
    room_counts = data_filtered["neighbourhood"].value_counts()
    fig, ax = plt.subplots()
    room_counts.plot(kind="bar", alpha=0.75, ax=ax)
    ax.set_xlabel("Konum")
    ax.set_ylabel("Oda Sayısı")
    ax.set_title("Bölgeye Göre Oda Sayısı ve Doluluk Durumu")
    st.pyplot(fig)

# Harita oluşturma ve konumları işaret etme
st.subheader("Tüm Konumların Gösterildiği Harita")
m = folium.Map(location=[data_filtered["latitude"].mean(), data_filtered["longitude"].mean()], zoom_start=12)
for index, row in data_filtered.iterrows():
    folium.Marker([row["latitude"], row["longitude"]], popup=row["neighbourhood"]).add_to(m)

# Folium haritasını Streamlit'e gömmek için folium_static kullanılıyor
folium_static(m)














# Verileri Yükleme ve İlk 20 Satırı Seçme
data_filtered = pd.read_csv("C:/Users/MONSTER/Downloads/listings.csv").head(20)

# Konum ve fiyat temelli gruplama
grouped_data = data_filtered.groupby(["neighbourhood", "price"])

# Ortalama fiyat ve ilan sayısını hesaplama
average_prices = grouped_data["price"].mean().reset_index(name="average_price")
average_prices["listing_count"] = grouped_data["id"].size().reset_index(name="count")["count"].to_list()

# En iyi puanlı konaklamaları seçme
best_listings = data_filtered.groupby('neighbourhood').apply(lambda x: x.nlargest(1, 'number_of_reviews')).reset_index(drop=True)

# Ağ oluşturma
G = nx.Graph()

for index, row in average_prices.iterrows():
    node_id = f"{row['neighbourhood']}_{row['average_price']}"
    G.add_node(node_id, price=row["average_price"], listing_count=row["listing_count"])

for _, row in best_listings.iterrows():
    G.add_node(row['neighbourhood'], best_listing=row['name'], review_score=row['number_of_reviews'])

for i, node1 in average_prices.iterrows():
    for j, node2 in average_prices.iterrows():
        if i != j and node1["neighbourhood"] == node2["neighbourhood"]:
            price_diff = abs(node1["average_price"] - node2["average_price"])
            if price_diff <= 100:
                weight = 3
            elif price_diff <= 200:
                weight = 2
            else:
                weight = 1
            G.add_edge(f"{node1['neighbourhood']}_{node1['average_price']}",
                       f"{node2['neighbourhood']}_{node2['average_price']}",
                       weight=weight)

# Görselleştirme
nt = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# Düğümleri ekleme
for node in G.nodes():
    if 'best_listing' in G.nodes[node]:
        nt.add_node(node, label=node, title=f"En İyi İlan: {G.nodes[node]['best_listing']}\nİnceleme Puanı: {G.nodes[node]['review_score']}", size=50)
    else:
        nt.add_node(node, label=node, title=f"Ortalama Fiyat: {G.nodes[node]['price']}\nİlan Sayısı: {G.nodes[node]['listing_count']}", size=30)

# Kenarları ekleyin
for edge in G.edges():
    nt.add_edge(edge[0], edge[1], title=f"Fiyat Farkı: {abs(G.nodes[edge[0]]['price'] - G.nodes[edge[1]]['price'])}")

# HTML dosyasını oluşturun
nt.write_html("airbnb_network.html")

# HTML dosyasının içeriğini gösterin
st.title("Airbnb İlanlarının Fiyat ve Bağlantı Grafiği")
st.write("Bu görselleştirme, Airbnb ilanlarının konumlarına ve fiyatlarına göre oluşturulmuş bir ağ grafiğidir.")
st.write("Düğümlere ve çizgilere tıkladığınızda daha fazla bilgi alabilirsiniz.")
st.components.v1.html(open("airbnb_network.html", "r").read(), height=900)



















# Görsel Kodlama
if st.button("Görsel Kodlama Yap"):
    st.subheader("Görsel Kodlama")
    # Veriyi görselleştirme
    fig = px.scatter(data_filtered, x="price", y="number_of_reviews")
    st.plotly_chart(fig)   

# En İyi Konaklama Yerlerini Sıralama
if st.button("Sırala"):
    st.subheader("En İyi Konaklama Yerleri")
    top_listings = data_filtered.sort_values(by=["price", "reviews_per_month"], ascending=[True, False]).head(10)
    
    # Tabloyu oluşturma
    fig = go.Figure(data=[go.Table(
        header=dict(values=["İsim", "İnceleme Puanı", "Konum", "Fiyat"],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[top_listings["name"], 
                           top_listings["reviews_per_month"], 
                           top_listings["neighbourhood"], 
                           top_listings["price"]],
                   fill_color='lavender',
                   align='left'))
    ])
    
    # Tabloyu gösterme
    st.plotly_chart(fig)












# Verileri Yükleme


# Fiyat Aralığı Seçimi
# min_price = st.sidebar.number_input("Minimum Fiyat", min_value=0, max_value=int(max(data["price"])), value=0, key="min_price_input")
# max_price = st.sidebar.number_input("Maksimum Fiyat", min_value=int(min(data["price"])), max_value=int(max(data["price"])), value=int(max(data["price"])), key="max_price_input")


# Fiyat Aralığına Göre Veriyi Filtreleme
data_filtered = data[(data["price"] >= min_price) & (data["price"] <= max_price)]

# İlçelere Göre Ortalama Fiyatları Hesaplama
avg_prices_by_neighbourhood = data_filtered.groupby("neighbourhood")["price"].mean().reset_index()

# İlçelere Göre Ortalama Fiyatları Görselleştirme
fig = px.bar(avg_prices_by_neighbourhood, x="neighbourhood", y="price", title="İstanbul İlçelerine Göre Ortalama Fiyatlar")
fig.update_xaxes(title="İlçe")
fig.update_yaxes(title="Ortalama Fiyat")
st.plotly_chart(fig)




# Verileri Yükleme


# Fiyat Aralığı Seçimi için Benzersiz Anahtar Oluşturma
min_price_key = f"min_price_input_{int(time.time())}"
max_price_key = f"max_price_input_{int(time.time())}"

# Fiyat Aralığı Seçimi
min_price = st.sidebar.number_input("Minimum Fiyat", min_value=0, max_value=int(max(data["price"])), value=0, key=min_price_key)
max_price = st.sidebar.number_input("Maksimum Fiyat", min_value=int(min(data["price"])), max_value=int(max(data["price"])), value=int(max(data["price"])), key=max_price_key)

# Fiyat Aralığına Göre Veriyi Filtreleme
data_filtered = data[(data["price"] >= min_price) & (data["price"] <= max_price)]

# İlçelere Göre Ortalama Fiyatları Hesaplama
avg_prices_by_neighbourhood = data_filtered.groupby("neighbourhood")["price"].mean().reset_index()

# Renk Paleti ve Fiyat Aralıkları Belirleme
price_ranges = [210.48, 263.25, 344.80, 420.63, 481.46, 542.43, 664.86, 802.76, 912.69, 1028.05, 1574.78]
colors = ["#f7fbff", "#ebf3fa", "#dee7f5", "#cedbf1", "#adb5ed", "#8799d8", "#6a7eb3", "#54679f", "#3e508b", "#293c77"]











# Görselleştirme Oluşturma
def visualize_istanbul_districts():
    # İstanbul ilçeleri listesi
    istanbul_districts = ["Kadıköy", "Beşiktaş", "Şişli", "Beyoğlu", "Fatih", "Üsküdar", "Sarıyer", "Bakırköy", "Kartal", "Maltepe", "Ataşehir", "Pendik", "Beylikdüzü", "Ümraniye", "Eyüpsultan", "Avcılar", "Bağcılar", "Bahçelievler", "Gaziosmanpaşa", "Başakşehir", "Esenler", "Silivri", "Kağıthane", "Sultangazi", "Büyükçekmece", "Sancaktepe", "Esenyurt", "Bayrampaşa", "Zeytinburnu", "Tuzla", "Şile", "Arnavutköy", "Çekmeköy", "Küçükçekmece", "Çatalca", "Sultangazi"]

    # İstanbul ilçelerine göre filtreleme
    istanbul_district_data = data[data["neighbourhood"].isin(istanbul_districts)]

    # Fiyat aralıkları için renk paleti oluşturma
    price_ranges = list(range(0, 10500, 500))
    colors = px.colors.diverging.RdBu[:len(price_ranges)]

    # İstanbul haritasını gösterme
    fig = px.scatter_mapbox(istanbul_district_data, 
                             lat="latitude", 
                             lon="longitude", 
                             color="price", 
                             hover_name="neighbourhood",
                             hover_data=["price"],
                             zoom=10,
                             color_continuous_scale=colors)
    fig.update_layout(mapbox_style="open-street-map")

    # Airbnb ilanlarının fiyat ve bağlantı grafiğini gösterme
    st.plotly_chart(fig)

    # Airbnb İlanlarının Fiyat ve Bağlantı Grafiği HTML dosyasını gösterme
    st.title("Airbnb İlanlarının Fiyat ve Bağlantı Grafiği")
    st.write("Bu görselleştirme, Airbnb ilanlarının konumlarına ve fiyatlarına göre oluşturulmuş bir ağ grafiğidir.")
    st.write("Düğümlere ve çizgilere tıkladığınızda daha fazla bilgi alabilirsiniz.")
    st.components.v1.html(open("airbnb_network.html", "r").read(), height=900)











import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit as st

# Verileri Yükleme ve İlk 20 Satırı Seçme
data_filtered = pd.read_csv("C:/Users/MONSTER/Downloads/listings.csv").head(20)

# Konum ve inceleme puanı temelli gruplama
grouped_data = data_filtered.groupby(["neighbourhood", "number_of_reviews"])

# Ortalama inceleme puanı ve ilan sayısını hesaplama
average_reviews = grouped_data["number_of_reviews"].mean().reset_index(name="average_review")
average_reviews["listing_count"] = grouped_data.size().reset_index(name="count")["count"].tolist()

# En yüksek inceleme puanına sahip konaklamaları seçme
best_listings = data_filtered.groupby('neighbourhood').apply(lambda x: x.nlargest(1, 'number_of_reviews')).reset_index(drop=True)

# Ağ oluşturma
G = nx.Graph()

for index, row in average_reviews.iterrows():
    node_id = f"{row['neighbourhood']}_{row['average_review']}"
    G.add_node(node_id, review=row["average_review"], listing_count=row["listing_count"])

for _, row in best_listings.iterrows():
    G.add_node(row['neighbourhood'], best_listing=row['name'], review_score=row['number_of_reviews'])

for i, node1 in average_reviews.iterrows():
    for j, node2 in average_reviews.iterrows():
        if i != j and node1["neighbourhood"] == node2["neighbourhood"]:
            review_diff = abs(node1["average_review"] - node2["average_review"])
            if review_diff <= 10:
                weight = 3
            elif review_diff <= 20:
                weight = 2
            else:
                weight = 1
            G.add_edge(f"{node1['neighbourhood']}_{node1['average_review']}",
                       f"{node2['neighbourhood']}_{node2['average_review']}",
                       weight=weight)

# Görselleştirme
nt = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# Düğümleri ekleme
for node in G.nodes():
    if 'best_listing' in G.nodes[node]:
        nt.add_node(node, label=node, title=f"En İyi İlan: {G.nodes[node]['best_listing']}\nİnceleme Puanı: {G.nodes[node]['review_score']}", size=50)
    else:
        nt.add_node(node, label=node, title=f"Ortalama İnceleme Puanı: {G.nodes[node]['review']}\nİlan Sayısı: {G.nodes[node]['listing_count']}", size=30)

# Kenarları ekleyin
for edge in G.edges():
    nt.add_edge(edge[0], edge[1], title=f"İnceleme Puanı Farkı: {abs(G.nodes[edge[0]]['review'] - G.nodes[edge[1]]['review'])}")

# HTML dosyasını oluşturun
nt.write_html("airbnb_network_reviews.html")

# HTML dosyasının içeriğini gösterin
st.title("Airbnb İlanlarının İnceleme Puanı ve Bağlantı Grafiği")
st.write("Bu görselleştirme, Airbnb ilanlarının konumlarına ve ortalama inceleme puanlarına göre oluşturulmuş bir ağ grafiğidir.")
st.write("Düğümlere ve çizgilere tıkladığınızda daha fazla bilgi alabilirsiniz.")
st.components.v1.html(open("airbnb_network_reviews.html", "r").read(), height=900)




















import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit as st

# Verileri Yükleme ve İlk 20 Satırı Seçme
data_filtered = pd.read_csv("C:/Users/MONSTER/Downloads/listings.csv").head(20)

# İlçelere Göre Konaklama Sayısını Hesaplama
neighbourhood_counts = data_filtered["neighbourhood"].value_counts()

# Ortalama fiyat farkı hesaplama
average_price_diff = {}

for neighbourhood1 in data_filtered["neighbourhood"].unique():
    for neighbourhood2 in data_filtered["neighbourhood"].unique():
        if neighbourhood1 != neighbourhood2:
            listings_neighbourhood1 = data_filtered[data_filtered["neighbourhood"] == neighbourhood1]["price"]
            listings_neighbourhood2 = data_filtered[data_filtered["neighbourhood"] == neighbourhood2]["price"]
            average_price1 = listings_neighbourhood1.mean()
            average_price2 = listings_neighbourhood2.mean()
            average_price_diff[(neighbourhood1, neighbourhood2)] = abs(average_price1 - average_price2)

# En pahalı Airbnb ilanlarını belirleme
most_expensive_listings = data_filtered.groupby('neighbourhood').apply(lambda x: x.nlargest(1, 'price')).reset_index(drop=True)

# Ağ oluşturma
G = nx.Graph()

for neighbourhood in data_filtered["neighbourhood"].unique():
    G.add_node(neighbourhood, size=neighbourhood_counts.get(neighbourhood, 0))

for index, row in most_expensive_listings.iterrows():
    expensive_neighbourhood = row['neighbourhood'] + "_expensive"
    G.add_node(expensive_neighbourhood, label=row['name'], title=f"En Pahalı İlan\nLokasyon: {row['neighbourhood']}\nFiyat: {row['price']}\nİnceleme Puanı: {row['number_of_reviews']}", size=50, color="#4CAF50")  # Yeşil renk
    G.add_edge(expensive_neighbourhood, row['neighbourhood'], weight=1)  # En pahalı lokasyon ile ilgili ilçeye bağlantı ekle

for (neighbourhood1, neighbourhood2), price_diff in average_price_diff.items():
    if price_diff > 0:
        G.add_edge(neighbourhood1, neighbourhood2, weight=1/price_diff)

# Görselleştirme
nt = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# Düğümleri ekleme
for node in G.nodes():
    if node.endswith("_expensive"):
        nt.add_node(node, label=G.nodes[node]["label"], title=G.nodes[node]["title"], size=50, color="#4CAF50")  # Yeşil renk
    else:
        nt.add_node(node, label=node, title=f"İlçe: {node}\nKonaklama Sayısı: {neighbourhood_counts.get(node, 0)}")

# Kenarları ekleyin
for edge in G.edges():
    if edge[0].endswith("_expensive") or edge[1].endswith("_expensive"):
        nt.add_edge(edge[0], edge[1], title="En Pahalı Lokasyon ile Bağlantı")
    else:
        nt.add_edge(edge[0], edge[1], title=f"Ortalama Fiyat Farkı: {average_price_diff[(edge[0], edge[1])]:.2f}")

# HTML dosyasını oluşturun
nt.write_html("neighbourhood_network.html")

# HTML dosyasının içeriğini gösterin
st.title("Airbnb İlanlarının İlçe ve Ortalama Fiyat Farkı Ağı")
st.write("Bu görselleştirme, Airbnb ilanlarının ilçelere göre ortalama fiyat farklarını ve en pahalı lokasyonları göstermektedir.")
st.write("Düğümlere ve çizgilere tıkladığınızda daha fazla bilgi alabilirsiniz.")
st.components.v1.html(open("neighbourhood_network.html", "r").read(), height=900)














import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit as st
import numpy as np

# Verileri Yükleme
data_filtered = pd.read_csv("C:/Users/MONSTER/Downloads/listings.csv")

# İlçelere Göre Fiyat Ortalamalarını Hesaplama
average_prices_by_neighbourhood = data_filtered.groupby("neighbourhood")["price"].mean()

# İlçelere Göre Konaklama Sayısını Hesaplama
listings_count_by_neighbourhood = data_filtered["neighbourhood"].value_counts()

# İlçeler Arasındaki Fiyat Farklarını Hesaplama
price_diff_between_neighbourhoods = {}
neighbourhoods = average_prices_by_neighbourhood.index
for neighbourhood1 in neighbourhoods:
    for neighbourhood2 in neighbourhoods:
        if neighbourhood1 != neighbourhood2:
            price_diff = abs(average_prices_by_neighbourhood[neighbourhood1] - average_prices_by_neighbourhood[neighbourhood2])
            price_diff_between_neighbourhoods[(neighbourhood1, neighbourhood2)] = price_diff

# En Çok Listelenen İlçeleri Seçme
top_neighbourhoods = listings_count_by_neighbourhood.head(10).index

# Seçilen İlçelerdeki Fiyat Ortalamalarını ve Konaklama Sayılarını Güncelleme
average_prices_by_neighbourhood = average_prices_by_neighbourhood.loc[top_neighbourhoods]
listings_count_by_neighbourhood = listings_count_by_neighbourhood.loc[top_neighbourhoods]

# Ağ Oluşturma
G = nx.Graph()

# İlçeleri Düğüm Olarak Ekleme
for neighbourhood in top_neighbourhoods:
    G.add_node(neighbourhood, size=listings_count_by_neighbourhood.get(neighbourhood, 0))

# Kenarları Ekleyin
for (neighbourhood1, neighbourhood2), price_diff in price_diff_between_neighbourhoods.items():
    if neighbourhood1 in top_neighbourhoods and neighbourhood2 in top_neighbourhoods:
        if price_diff > 0:
            G.add_edge(neighbourhood1, neighbourhood2, weight=1/price_diff)

# Görselleştirme
nt = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")

# Düğümleri Ekleme
for node in G.nodes():
    nt.add_node(node, label=node, title=f"İlçe: {node}\nKonaklama Sayısı: {listings_count_by_neighbourhood.get(node, 0)}", physics=True)

# Kenarları Ekleyin
for edge in G.edges():
    nt.add_edge(edge[0], edge[1], title=f"Fiyat Farkı: {price_diff_between_neighbourhoods[(edge[0], edge[1])]:.2f}")

# HTML dosyasını oluşturun
nt.write_html("top_neighbourhoods_network.html")

# HTML dosyasının içeriğini gösterin
st.title("En Çok Listelenen İlçelerin Airbnb Ağı")
st.write("Bu görselleştirme, en çok listelenen ilçeler arasındaki ortalama fiyat farklarını ve konaklama sayılarını göstermektedir.")
st.write("Düğümlere ve çizgilere tıkladığınızda daha fazla bilgi alabilirsiniz.")
st.components.v1.html(open("top_neighbourhoods_network.html", "r").read(), height=900)
