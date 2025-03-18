import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import base64
from io import BytesIO
import json

app = Flask(__name__)

# ---------------------- Step 1: Load Grocery Data ----------------------
csv_filename = "grocery_data.csv"
try:
    # Read CSV with explicit encoding and handle any BOM
    df_grocery = pd.read_csv(csv_filename, encoding='utf-8-sig')
    
    # Clean column names
    df_grocery.columns = df_grocery.columns.str.strip()
    
    # Rename columns to match our application's expectations
    column_mapping = {
        'ProductName': 'Product Name',
        'StockQuantity': 'Stock',
        'BestSeller': 'Best Seller',
        'QuantitySold': 'Quantity Sold'
    }
    df_grocery = df_grocery.rename(columns=column_mapping)
    
    # Verify required columns exist
    required_columns = ['Product Name', 'Price', 'Stock', 'Category', 'Best Seller', 'Quantity Sold']
    missing_columns = [col for col in required_columns if col not in df_grocery.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        print("Available columns:", df_grocery.columns.tolist())
        raise KeyError(f"Missing required columns: {missing_columns}")
        
    # Convert numeric columns
    df_grocery['Price'] = pd.to_numeric(df_grocery['Price'], errors='coerce')
    df_grocery['Stock'] = pd.to_numeric(df_grocery['Stock'], errors='coerce')
    df_grocery['Quantity Sold'] = pd.to_numeric(df_grocery['Quantity Sold'], errors='coerce')
    
except Exception as e:
    print(f"Error loading CSV file: {str(e)}")
    raise

# ---------------------- Step 2: Search Product ----------------------
def search_product(product_name):
    # Convert product name to lowercase for case-insensitive search
    product_name = product_name.lower()
    
    # Convert all product names in dataframe to lowercase for comparison
    df_grocery['Product Name Lower'] = df_grocery['Product Name'].str.lower()
    
    # Search for the product
    product = df_grocery[df_grocery['Product Name Lower'] == product_name]
    
    # Drop the temporary lowercase column
    df_grocery.drop('Product Name Lower', axis=1, inplace=True)
    
    if product.empty:
        return "❌ Product not available."
    return product

# ---------------------- Step 3: Buy Product ----------------------
def buy_product(product_name, quantity):
    global df_grocery
    # Convert product name to lowercase for case-insensitive search
    product_name = product_name.lower()
    
    # Convert all product names in dataframe to lowercase for comparison
    df_grocery['Product Name Lower'] = df_grocery['Product Name'].str.lower()
    
    # Search for the product
    product = df_grocery[df_grocery['Product Name Lower'] == product_name]
    
    # Drop the temporary lowercase column
    df_grocery.drop('Product Name Lower', axis=1, inplace=True)

    if product.empty:
        return "❌ Product not available."

    stock = product["Stock"].values[0]
    if stock >= quantity:
        df_grocery.loc[df_grocery['Product Name'].str.lower() == product_name, "Stock"] -= quantity
        df_grocery.to_csv(csv_filename, index=False)
        return f"✅ Purchased {quantity} of {product['Product Name'].values[0]}. Remaining stock: {stock - quantity}."
    else:
        return "⚠️ Not enough stock available."

# ---------------------- Step 4: Filtering Options ----------------------
def filter_products(filter_type, value=None, price_range=None):
    if filter_type == "price" and price_range:
        min_price, max_price = price_range
        return df_grocery[(df_grocery["Price"] >= min_price) & (df_grocery["Price"] <= max_price)]
    elif filter_type == "best_seller":
        return df_grocery[df_grocery["Best Seller"] == True]
    elif filter_type == "category":
        return df_grocery[df_grocery["Category"] == value]
    else:
        return "❌ Invalid filter option."

# ---------------------- Step 5: Sales Prediction (Linear Regression) ----------------------
class SalesPredictionModel:
    def __init__(self, data):
        self.df = data
        self.model = LinearRegression()

    def train(self):
        self.df['Quantity Sold'] = pd.to_numeric(self.df['Quantity Sold'], errors='coerce')
        self.df.dropna(subset=['Quantity Sold'], inplace=True)
        X = self.df[['Price']].loc[self.df['Quantity Sold'].notna()]
        y = self.df['Quantity Sold'].loc[self.df['Quantity Sold'].notna()]

        self.model.fit(X, y)

    def predict(self, price):
        price = np.array(price).reshape(-1, 1)
        return self.model.predict(price)[0]

    def plot_sales(self, x_vals=None, x_label="Price", title="Sales Prediction Model"):
        plt.figure(figsize=(10, 6))
        plt.scatter(self.df['Price'], self.df['Quantity Sold'], color='blue', label='Actual Sales')
        plt.plot(self.df['Price'], self.model.predict(self.df[['Price']]), color='red', label='Predicted Sales')

        if x_vals is not None:
            plt.axvline(x=x_vals, color='green', linestyle='dashed', label=f'Predicted at ₹{x_vals}')
        
        plt.xlabel(x_label)
        plt.ylabel('Quantity Sold')
        plt.title(title)
        plt.legend()
        
        # Save plot to a base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str

sales_model = SalesPredictionModel(df_grocery)
sales_model.train()

# ---------------------- Step 6: Predict Sales ----------------------
def predict_sales_by_product_name(product_name):
    # Convert product name to lowercase for case-insensitive search
    product_name = product_name.lower()
    
    # Convert all product names in dataframe to lowercase for comparison
    df_grocery['Product Name Lower'] = df_grocery['Product Name'].str.lower()
    
    # Search for the product
    product = df_grocery[df_grocery['Product Name Lower'] == product_name]
    
    # Drop the temporary lowercase column
    df_grocery.drop('Product Name Lower', axis=1, inplace=True)
    
    if product.empty:
        return {"success": False, "message": "❌ Product not available for sales prediction."}

    price = product["Price"].values[0]
    predicted_sales = sales_model.predict(price)
    img_str = sales_model.plot_sales(x_vals=price, x_label="Price", title=f"Sales Prediction for {product['Product Name'].values[0]}")
    
    return {
        "success": True,
        "message": f"📊 Predicted sales for {product['Product Name'].values[0]} (₹{price}): {predicted_sales:.2f} units",
        "image": img_str
    }

def predict_sales_by_category(category):
    category_data = df_grocery[df_grocery["Category"] == category]
    if category_data.empty:
        return {"success": False, "message": "❌ No products found in this category."}

    avg_price = category_data["Price"].mean()
    predicted_sales = sales_model.predict(avg_price)
    img_str = sales_model.plot_sales(x_vals=avg_price, x_label="Price", title=f"Sales Prediction for {category} Category")
    
    return {
        "success": True,
        "message": f"📊 Predicted average sales for {category} category (₹{avg_price:.2f}): {predicted_sales:.2f} units",
        "image": img_str
    }

def predict_sales_by_best_sellers():
    best_seller_data = df_grocery[df_grocery["Best Seller"] == True]
    if best_seller_data.empty:
        return {"success": False, "message": "❌ No best sellers found."}

    avg_price = best_seller_data["Price"].mean()
    predicted_sales = sales_model.predict(avg_price)
    img_str = sales_model.plot_sales(x_vals=avg_price, x_label="Price", title="Sales Prediction for Best Sellers")
    
    return {
        "success": True,
        "message": f"📊 Predicted sales for best sellers (Avg Price: ₹{avg_price:.2f}): {predicted_sales:.2f} units",
        "image": img_str
    }

def predict_sales_by_price(input_price):
    try:
        input_price = float(input_price)
        predicted_sales = sales_model.predict(input_price)
        img_str = sales_model.plot_sales(x_vals=input_price, x_label="Price", title=f"Sales Prediction for ₹{input_price}")
        
        return {
            "success": True,
            "message": f"📊 Predicted sales for price ₹{input_price}: {predicted_sales:.2f} units",
            "image": img_str
        }
    except:
        return {"success": False, "message": "❌ Invalid price input."}

# ---------------------- Step 7: Stock Prediction (ARIMA) ----------------------
def predict_stock(days_to_predict=5):
    stock_data = df_grocery['Stock'].values
    
    try:
        model = ARIMA(stock_data, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=days_to_predict)
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(stock_data)), stock_data, label="Current Stock")
        plt.plot(range(len(stock_data), len(stock_data) + days_to_predict), forecast, label="Forecasted Stock", linestyle="dashed")
        plt.xlabel("Days")
        plt.ylabel("Stock Levels")
        plt.title("Stock Forecasting (ARIMA)")
        plt.legend()
        
        # Save plot to a base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            "success": True, 
            "message": f"Stock prediction for next {days_to_predict} days",
            "forecast": forecast.tolist(),
            "image": img_str
        }
    except Exception as e:
        return {"success": False, "message": f"❌ Error in prediction: {str(e)}"}

# ---------------------- HTML Template ----------------------
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grocery Management System</title>
    <style>
        :root {
            --primary: #3498db;
            --secondary: #2ecc71;
            --danger: #e74c3c;
            --warning: #f39c12;
            --dark: #34495e;
            --light: #ecf0f1;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f7fa;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 20px 0;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 12px 24px;
            background-color: white;
            color: var(--dark);
            cursor: pointer;
            border-radius: 5px;
            margin: 5px;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .tab:hover {
            background-color: var(--primary);
            color: white;
            transform: translateY(-3px);
        }
        
        .tab.active {
            background-color: var(--primary);
            color: white;
        }
        
        .content {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            min-height: 400px;
        }
        
        .panel {
            display: none;
        }
        
        .panel.active {
            display: block;
        }
        
        input, select, button {
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            width: 100%;
            transition: all 0.3s;
        }
        
        input:focus, select:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
        }
        
        button {
            background-color: var(--primary);
            color: white;
            cursor: pointer;
            font-weight: bold;
            border: none;
        }
        
        button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
        }
        
        .result-container {
            margin-top: 20px;
            padding: 20px;
            background-color: var(--light);
            border-radius: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: var(--primary);
            color: white;
        }
        
        tr:hover {
            background-color: #f1f1f1;
        }
        
        .chart-container {
            width: 100%;
            margin-top: 20px;
        }
        
        .chart-container img {
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-row {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .form-group.col {
            flex: 1;
            min-width: 200px;
        }
        
        @media (max-width: 768px) {
            .tab {
                width: 100%;
                margin-bottom: 10px;
            }
            
            .form-row {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Grocery Management System</h1>
            <p>Manage your inventory and predict sales with machine learning</p>
        </header>
        
        <div class="tabs">
            <div class="tab active" data-tab="search">Search Product</div>
            <div class="tab" data-tab="buy">Buy Product</div>
            <div class="tab" data-tab="filter">Filter Products</div>
            <div class="tab" data-tab="sales">Sales Prediction</div>
            <div class="tab" data-tab="stock">Stock Prediction</div>
        </div>
        
        <div class="content">
            <!-- Search Product Panel -->
            <div class="panel active" id="search-panel">
                <h2>Search Product</h2>
                <div class="form-group">
                    <label for="search-input">Product Name:</label>
                    <input type="text" id="search-input" placeholder="Enter product name...">
                </div>
                <button id="search-btn">Search</button>
                <div id="search-result" class="result-container" style="display: none;"></div>
            </div>
            
            <!-- Buy Product Panel -->
            <div class="panel" id="buy-panel">
                <h2>Buy Product</h2>
                <div class="form-group">
                    <label for="buy-product-input">Product Name:</label>
                    <input type="text" id="buy-product-input" placeholder="Enter product name...">
                </div>
                <div class="form-group">
                    <label for="buy-quantity-input">Quantity:</label>
                    <input type="number" id="buy-quantity-input" min="1" value="1">
                </div>
                <button id="buy-btn">Buy</button>
                <div id="buy-result" class="result-container" style="display: none;"></div>
            </div>
            
            <!-- Filter Products Panel -->
            <div class="panel" id="filter-panel">
                <h2>Filter Products</h2>
                <div class="form-group">
                    <label for="filter-type">Filter Type:</label>
                    <select id="filter-type">
                        <option value="price">By Price Range</option>
                        <option value="category">By Category</option>
                        <option value="best_seller">Best Sellers</option>
                    </select>
                </div>
                
                <div id="price-filter" class="form-row">
                    <div class="form-group col">
                        <label for="min-price">Minimum Price:</label>
                        <input type="number" id="min-price" min="0" value="0">
                    </div>
                    <div class="form-group col">
                        <label for="max-price">Maximum Price:</label>
                        <input type="number" id="max-price" min="0" value="1000">
                    </div>
                </div>
                
                <div id="category-filter" style="display: none;">
                    <div class="form-group">
                        <label for="category-input">Category:</label>
                        <input type="text" id="category-input" placeholder="Enter category name...">
                    </div>
                </div>
                
                <button id="filter-btn">Filter</button>
                <div id="filter-result" class="result-container" style="display: none;"></div>
            </div>
            
            <!-- Sales Prediction Panel -->
            <div class="panel" id="sales-panel">
                <h2>Sales Prediction</h2>
                <div class="form-group">
                    <label for="sales-prediction-type">Prediction Type:</label>
                    <select id="sales-prediction-type">
                        <option value="product">By Product Name</option>
                        <option value="category">By Category</option>
                        <option value="best_seller">For Best Sellers</option>
                        <option value="price">By Price</option>
                    </select>
                </div>
                
                <div id="product-prediction" class="form-group">
                    <label for="product-name-prediction">Product Name:</label>
                    <input type="text" id="product-name-prediction" placeholder="Enter product name...">
                </div>
                
                <div id="category-prediction" class="form-group" style="display: none;">
                    <label for="category-name-prediction">Category:</label>
                    <input type="text" id="category-name-prediction" placeholder="Enter category name...">
                </div>
                
                <div id="price-prediction" class="form-group" style="display: none;">
                    <label for="price-prediction-input">Price:</label>
                    <input type="number" id="price-prediction-input" min="0" value="100">
                </div>
                
                <button id="predict-sales-btn">Predict Sales</button>
                <div id="sales-result" class="result-container" style="display: none;">
                    <div id="sales-message"></div>
                    <div id="chart-container" class="chart-container"></div>
                </div>
            </div>
            
            <!-- Stock Prediction Panel -->
            <div class="panel" id="stock-panel">
                <h2>Stock Prediction</h2>
                <div class="form-group">
                    <label for="days-prediction">Number of Days:</label>
                    <input type="number" id="days-prediction" min="1" max="30" value="5">
                </div>
                <button id="predict-stock-btn">Predict Stock</button>
                <div id="stock-result" class="result-container" style="display: none;">
                    <div id="stock-message"></div>
                    <div id="stock-chart-container" class="chart-container"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Tab switching functionality
            const tabs = document.querySelectorAll('.tab');
            const panels = document.querySelectorAll('.panel');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const targetPanel = tab.getAttribute('data-tab');
                    
                    // Update active tab
                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    
                    // Update active panel
                    panels.forEach(panel => panel.classList.remove('active'));
                    document.getElementById(`${targetPanel}-panel`).classList.add('active');
                });
            });
            
            // Filter type change handling
            const filterType = document.getElementById('filter-type');
            const priceFilter = document.getElementById('price-filter');
            const categoryFilter = document.getElementById('category-filter');
            
            filterType.addEventListener('change', () => {
                const selectedType = filterType.value;
                
                if (selectedType === 'price') {
                    priceFilter.style.display = 'flex';
                    categoryFilter.style.display = 'none';
                } else if (selectedType === 'category') {
                    priceFilter.style.display = 'none';
                    categoryFilter.style.display = 'block';
                } else {
                    priceFilter.style.display = 'none';
                    categoryFilter.style.display = 'none';
                }
            });
            
            // Sales prediction type change handling
            const salesPredictionType = document.getElementById('sales-prediction-type');
            const productPrediction = document.getElementById('product-prediction');
            const categoryPrediction = document.getElementById('category-prediction');
            const pricePrediction = document.getElementById('price-prediction');
            
            salesPredictionType.addEventListener('change', () => {
                const selectedType = salesPredictionType.value;
                
                productPrediction.style.display = 'none';
                categoryPrediction.style.display = 'none';
                pricePrediction.style.display = 'none';
                
                if (selectedType === 'product') {
                    productPrediction.style.display = 'block';
                } else if (selectedType === 'category') {
                    categoryPrediction.style.display = 'block';
                } else if (selectedType === 'price') {
                    pricePrediction.style.display = 'block';
                }
            });
            
            // Search product functionality
            const searchBtn = document.getElementById('search-btn');
            const searchInput = document.getElementById('search-input');
            const searchResult = document.getElementById('search-result');
            
            searchBtn.addEventListener('click', () => {
                const productName = searchInput.value.trim();
                if (!productName) {
                    showAlert(searchResult, 'Please enter a product name', 'alert-warning');
                    return;
                }
                
                fetch(`/search?product_name=${encodeURIComponent(productName)}`)
                    .then(response => response.json())
                    .then(data => {
                        searchResult.style.display = 'block';
                        
                        if (typeof data === 'string' && data.includes('❌')) {
                            showAlert(searchResult, data, 'alert-danger');
                        } else {
                            let tableHtml = '<table><thead><tr>';
                            
                            // Create table headers
                            for (const key in data[0]) {
                                tableHtml += `<th>${key}</th>`;
                            }
                            
                            tableHtml += '</tr></thead><tbody>';
                            
                            // Create table rows
                            data.forEach(product => {
                                tableHtml += '<tr>';
                                for (const key in product) {
                                    tableHtml += `<td>${product[key]}</td>`;
                                }
                                tableHtml += '</tr>';
                            });
                            
                            tableHtml += '</tbody></table>';
                            searchResult.innerHTML = tableHtml;
                        }
                    })
                    .catch(error => {
                        showAlert(searchResult, 'Error searching for product', 'alert-danger');
                        console.error('Error:', error);
                    });
            });
            
            // Buy product functionality
            const buyBtn = document.getElementById('buy-btn');
            const buyProductInput = document.getElementById('buy-product-input');
            const buyQuantityInput = document.getElementById('buy-quantity-input');
            const buyResult = document.getElementById('buy-result');
            
            buyBtn.addEventListener('click', () => {
                const productName = buyProductInput.value.trim();
                const quantity = parseInt(buyQuantityInput.value);
                
                if (!productName) {
                    showAlert(buyResult, 'Please enter a product name', 'alert-warning');
                    return;
                }
                
                if (isNaN(quantity) || quantity < 1) {
                    showAlert(buyResult, 'Please enter a valid quantity', 'alert-warning');
                    return;
                }
                
                fetch('/buy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        product_name: productName,
                        quantity: quantity
                    }),
                })
                    .then(response => response.json())
                    .then(data => {
                        buyResult.style.display = 'block';
                        
                        if (data.includes('✅')) {
                            showAlert(buyResult, data, 'alert-success');
                        } else if (data.includes('⚠️')) {
                            showAlert(buyResult, data, 'alert-warning');
                        } else {
                            showAlert(buyResult, data, 'alert-danger');
                        }
                    })
                    .catch(error => {
                        showAlert(buyResult, 'Error processing purchase', 'alert-danger');
                        console.error('Error:', error);
                    });
            });
            
            // Filter products functionality
            const filterBtn = document.getElementById('filter-btn');
            const minPrice = document.getElementById('min-price');
            const maxPrice = document.getElementById('max-price');
            const categoryInput = document.getElementById('category-input');
            const filterResult = document.getElementById('filter-result');
            
            filterBtn.addEventListener('click', () => {
                const selectedFilterType = filterType.value;
                let url = `/filter?filter_type=${selectedFilterType}`;
                
                if (selectedFilterType === 'price') {
                    const min = parseFloat(minPrice.value);
                    const max = parseFloat(maxPrice.value);
                    
                    if (isNaN(min) || isNaN(max) || min > max) {
                        showAlert(filterResult, 'Please enter valid price range', 'alert-warning');
                        return;
                    }
                    
                    url += `&min_price=${min}&max_price=${max}`;
                } else if (selectedFilterType === 'category') {
                    const category = categoryInput.value.trim();
                    
                    if (!category) {
                        showAlert(filterResult, 'Please enter a category', 'alert-warning');
                        return;
                    }
                    
                    url += `&value=${encodeURIComponent(category)}`;
                }
                
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        filterResult.style.display = 'block';
                        
                        if (typeof data === 'string' && data.includes('❌')) {
                            showAlert(filterResult, data, 'alert-danger');
                        } else {
                            let tableHtml = '<table><thead><tr>';
                            
                            // Create table headers
                            for (const key in data[0]) {
                                tableHtml += `<th>${key}</th>`;
                            }
                            
                            tableHtml += '</tr></thead><tbody>';
                            
                            // Create table rows
                            data.forEach(product => {
                                tableHtml += '<tr>';
                                for (const key in product) {
                                    tableHtml += `<td>${product[key]}</td>`;
                                }
                                tableHtml += '</tr>';
                            });
                            
                            tableHtml += '</tbody></table>';
                            filterResult.innerHTML = tableHtml;
                        }
                    })
                    .catch(error => {
                        showAlert(filterResult, 'Error filtering products', 'alert-danger');
                        console.error('Error:', error);
                    });
            });
            
            // Sales prediction functionality
            const predictSalesBtn = document.getElementById('predict-sales-btn');
            const productNamePrediction = document.getElementById('product-name-prediction');
            const categoryNamePrediction = document.getElementById('category-name-prediction');
            const pricePredictionInput = document.getElementById('price-prediction-input');
            const salesResult = document.getElementById('sales-result');
            const salesMessage = document.getElementById('sales-message');
            const chartContainer = document.getElementById('chart-container');
            
            predictSalesBtn.addEventListener('click', () => {
                const selectedType = salesPredictionType.value;
                let url = `/predict_sales?type=${selectedType}`;
                
                if (selectedType === 'product') {
                    const productName = productNamePrediction.value.trim();
                    
                    if (!productName) {
                        showAlert(salesResult, 'Please enter a product name', 'alert-warning');
                        return;
                    }
                    
                    url += `&product_name=${encodeURIComponent(productName)}`;
                } else if (selectedType === 'category') {
                    const categoryName = categoryNamePrediction.value.trim();
                    
                    if (!categoryName) {
                        showAlert(salesResult, 'Please enter a category name', 'alert-warning');
                        return;
                    }
                    
                    url += `&category=${encodeURIComponent(categoryName)}`;
                } else if (selectedType === 'price') {
                    const price = parseFloat(pricePredictionInput.value);
                    
                    if (isNaN(price) || price < 0) {
                        showAlert(salesResult, 'Please enter a valid price', 'alert-warning');
                        return;
                    }
                    
                    url += `&price=${price}`;
                }
                
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        salesResult.style.display = 'block';
                        
                        if (!data.success) {
                            showAlert(salesResult, data.message, 'alert-danger');
                            chartContainer.innerHTML = '';
                        } else {
                            salesMessage.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                            chartContainer.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Sales Prediction Chart">`;
                        }
                    })
                    .catch(error => {
                        showAlert(salesResult, 'Error predicting sales', 'alert-danger');
                        console.error('Error:', error);
                    });
            });
            
            // Stock prediction functionality
            const predictStockBtn = document.getElementById('predict-stock-btn');
            const daysPrediction = document.getElementById('days-prediction');
            const stockResult = document.getElementById('stock-result');
            const stockMessage = document.getElementById('stock-message');
            const stockChartContainer = document.getElementById('stock-chart-container');
            
            predictStockBtn.addEventListener('click', () => {
                const days = parseInt(daysPrediction.value);
                
                if (isNaN(days) || days < 1 || days > 30) {
                    showAlert(stockResult, 'Please enter a valid number of days (1-30)', 'alert-warning');
                    return;
                }
                
                fetch(`/predict_stock?days=${days}`)
                    .then(response => response.json())
                    .then(data => {
                        stockResult.style.display = 'block';
                        
                        if (!data.success) {
                            showAlert(stockResult, data.message, 'alert-danger');
                            stockChartContainer.innerHTML = '';
                        } else {
                            stockMessage.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                            stockChartContainer.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Stock Prediction Chart">`;
                            
                            // Display forecast values
                            let forecastHtml = '<h3 class="mt-4">Forecasted Stock Values:</h3>';
                            forecastHtml += '<table><thead><tr><th>Day</th><th>Predicted Stock</th></tr></thead><tbody>';
                            
                            data.forecast.forEach((value, index) => {
                                forecastHtml += `<tr><td>Day ${index + 1}</td><td>${value.toFixed(2)}</td></tr>`;
                            });
                            
                            forecastHtml += '</tbody></table>';
                            stockChartContainer.innerHTML += forecastHtml;
                        }
                    })
                    .catch(error => {
                        showAlert(stockResult, 'Error predicting stock', 'alert-danger');
                        console.error('Error:', error);
                    });
            });
            
            // Helper function to show alerts
            function showAlert(container, message, alertClass) {
                container.innerHTML = `<div class="alert ${alertClass}">${message}</div>`;
                container.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

# ---------------------- Flask Routes ----------------------

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/search')
def search():
    product_name = request.args.get('product_name')
    result = search_product(product_name)
    
    if isinstance(result, str):
        return jsonify(result)
    else:
        return jsonify(result.to_dict('records'))

@app.route('/buy', methods=['POST'])
def buy():
    data = request.json
    product_name = data.get('product_name')
    quantity = data.get('quantity')
    
    result = buy_product(product_name, quantity)
    return jsonify(result)

@app.route('/filter')
def filter():
    filter_type = request.args.get('filter_type')
    value = request.args.get('value')
    
    if filter_type == 'price':
        min_price = float(request.args.get('min_price'))
        max_price = float(request.args.get('max_price'))
        result = filter_products(filter_type, price_range=(min_price, max_price))
    elif filter_type == 'category':
        result = filter_products(filter_type, value=value)
    else:
        result = filter_products(filter_type)
    
    if isinstance(result, str):
        return jsonify(result)
    else:
        return jsonify(result.to_dict('records'))

@app.route('/predict_sales')
def predict_sales():
    prediction_type = request.args.get('type')
    
    if prediction_type == 'product':
        product_name = request.args.get('product_name')
        return jsonify(predict_sales_by_product_name(product_name))
    elif prediction_type == 'category':
        category = request.args.get('category')
        return jsonify(predict_sales_by_category(category))
    elif prediction_type == 'best_seller':
        return jsonify(predict_sales_by_best_sellers())
    elif prediction_type == 'price':
        price = request.args.get('price')
        return jsonify(predict_sales_by_price(price))
    else:
        return jsonify({"success": False, "message": "Invalid prediction type"})

@app.route('/predict_stock')
def predict_stock_route():
    days = int(request.args.get('days', 5))
    return jsonify(predict_stock(days))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
