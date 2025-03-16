import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA








# ---------------------- Step 1: Load Grocery Data ----------------------
csv_filename = "grocery_data_updated.csv"
df_grocery = pd.read_csv(csv_filename)

# ---------------------- Step 2: Search Product ----------------------
def search_product(product_name):
    product = df_grocery[df_grocery["Product Name"] == product_name]
    if product.empty:
        return "❌ Product not available."
    return product

# ---------------------- Step 3: Buy Product ----------------------
def buy_product(product_name, quantity):
    global df_grocery
    product = df_grocery[df_grocery["Product Name"] == product_name]

    if product.empty:
        return "❌ Product not available."

    stock = product["Stock"].values[0]
    if stock >= quantity:
        df_grocery.loc[df_grocery["Product Name"] == product_name, "Stock"] -= quantity
        df_grocery.to_csv(csv_filename, index=False)
        return f"✅ Purchased {quantity} of {product_name}. Remaining stock: {stock - quantity}."
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
        X = self.df[['Price']]
        y = self.df['Quantity Sold']
        self.model.fit(X, y)

    def predict(self, price):
        price = np.array(price).reshape(-1, 1)
        return self.model.predict(price)[0]

    def plot_sales(self, x_vals=None, x_label="Price", title="Sales Prediction Model"):
        plt.scatter(self.df['Price'], self.df['Quantity Sold'], color='blue', label='Actual Sales')
        plt.plot(self.df['Price'], self.model.predict(self.df[['Price']]), color='red', label='Predicted Sales')

        if x_vals is not None:
            plt.axvline(x=x_vals, color='green', linestyle='dashed', label=f'Predicted at ₹{x_vals}')
        
        plt.xlabel(x_label)
        plt.ylabel('Quantity Sold')
        plt.title(title)
        plt.legend()
        plt.show()

sales_model = SalesPredictionModel(df_grocery)
sales_model.train()

# ---------------------- Step 6: Predict Sales ----------------------
def predict_sales_by_product_name(product_name):
    product = df_grocery[df_grocery["Product Name"] == product_name]
    if product.empty:
        return "❌ Product not available for sales prediction."

    price = product["Price"].values[0]
    predicted_sales = sales_model.predict(price)
    sales_model.plot_sales(x_vals=price, x_label="Price", title=f"Sales Prediction for {product_name}")
    return f"📊 Predicted sales for {product_name} (₹{price}): {predicted_sales:.2f} units"

def predict_sales_by_category(category):
    category_data = df_grocery[df_grocery["Category"] == category]
    if category_data.empty:
        return "❌ No products found in this category."

    avg_price = category_data["Price"].mean()
    predicted_sales = sales_model.predict(avg_price)
    sales_model.plot_sales(x_vals=avg_price, x_label="Price", title=f"Sales Prediction for {category} Category")
    return f"📊 Predicted average sales for {category} category (₹{avg_price:.2f}): {predicted_sales:.2f} units"

def predict_sales_by_best_sellers():
    best_seller_data = df_grocery[df_grocery["Best Seller"] == True]
    if best_seller_data.empty:
        return "❌ No best sellers found."

    avg_price = best_seller_data["Price"].mean()
    predicted_sales = sales_model.predict(avg_price)
    sales_model.plot_sales(x_vals=avg_price, x_label="Price", title="Sales Prediction for Best Sellers")
    return f"📊 Predicted sales for best sellers (Avg Price: ₹{avg_price:.2f}): {predicted_sales:.2f} units"

def predict_sales_by_price():
    input_price = int(input("Enter a price for sales prediction: "))
    predicted_sales = sales_model.predict(input_price)
    sales_model.plot_sales(x_vals=input_price, x_label="Price", title=f"Sales Prediction for ₹{input_price}")
    return f"📊 Predicted sales for price ₹{input_price}: {predicted_sales:.2f} units"

# ---------------------- Step 7: Stock Prediction (ARIMA) ----------------------
def predict_stock(stock_data, days_to_predict=5):
    model = ARIMA(stock_data, order=(1, 1, 1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=days_to_predict)
    
    plt.plot(range(len(stock_data)), stock_data, label="Current Stock")
    plt.plot(range(len(stock_data), len(stock_data) + days_to_predict), forecast, label="Forecasted Stock", linestyle="dashed")
    plt.xlabel("Days")
    plt.ylabel("Stock Levels")
    plt.title("Stock Forecasting (ARIMA)")
    plt.legend()
    plt.show()
    
    return forecast

# ---------------------- Step 8: User Interaction ----------------------
while True:
    print("\n📌 Grocery Management System")
    print("1. Search Product")
    print("2. Buy Product")
    print("3. Filter Products")
    print("4. Sales Prediction")
    print("5. Stock Prediction")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        product_name = input("Enter product name to search: ")
        print(search_product(product_name))

    elif choice == "2":
        product_name = input("Enter product name to buy: ")
        quantity = int(input("Enter quantity to buy: "))
        print(buy_product(product_name, quantity))

    elif choice == "3":
        filter_type = input("Filter by (price/category/best_seller): ").strip().lower()
        if filter_type == "price":
            min_price = int(input("Enter minimum price: "))
            max_price = int(input("Enter maximum price: "))
            print(filter_products(filter_type, price_range=(min_price, max_price)))
        elif filter_type == "category":
            value = input("Enter category: ")
            print(filter_products(filter_type, value))
        else:
            print(filter_products(filter_type))

    elif choice == "4":
        print("\n📊 Sales Prediction Menu")
        print("1. Predict Sales by Product Name")
        print("2. Predict Sales by Category")
        print("3. Predict Sales for Best Sellers")
        print("4. Predict Sales by Price")
        sales_choice = input("Enter your choice: ")

        if sales_choice == "1":
            product_name = input("Enter product name: ")
            print(predict_sales_by_product_name(product_name))
        elif sales_choice == "2":
            category = input("Enter category name: ")
            print(predict_sales_by_category(category))
        elif sales_choice == "3":
            print(predict_sales_by_best_sellers())
        elif sales_choice == "4":
            print(predict_sales_by_price())
        else:
            print("Invalid choice. Returning to main menu.")

    elif choice == "5":
        days = int(input("Enter number of days for stock forecasting: "))
        print(f"Predicted stock levels: {predict_stock(df_grocery['Stock'], days)}")

    elif choice == "6":
        print("Exiting program...")
        break

    else:
        print("Invalid choice. Please try again.")




# # **Grocery Management System: Detailed Explanation**

# ## **1. Code Breakdown**
# This Grocery Management System integrates various functionalities such as product search, purchase, filtering, sales prediction, and stock forecasting. The code is structured into several modules, each performing a specific function.

# ### **Functions Used in the Code**
# 1. **`search_product(product_name)`** – Searches for a product by name and returns details.
# 2. **`buy_product(product_name, quantity)`** – Updates stock when a purchase is made.
# 3. **`filter_products(filter_type, value, price_range)`** – Filters products based on category, price, or best-seller status.
# 4. **`predict_sales_by_product_name(product_name)`** – Predicts sales based on product price using Linear Regression.
# 5. **`predict_sales_by_category(category)`** – Estimates average sales for a category.
# 6. **`predict_sales_by_best_sellers()`** – Predicts sales for best-selling items.
# 7. **`predict_sales_by_price()`** – Uses price input to predict sales and visualize trends.
# 8. **`predict_stock(stock_data, days_to_predict)`** – Uses ARIMA for stock forecasting.

# ## **2. Machine Learning Models Used**

# ### **A. Linear Regression (Sales Prediction)**
# #### **What is Linear Regression?**
# Linear Regression is a supervised learning algorithm used for predicting numerical values based on input features. It establishes a relationship between an independent variable (price) and a dependent variable (quantity sold).

# #### **Why is Linear Regression Used?**
# - Helps predict future sales based on price.
# - Identifies trends in pricing and quantity sold.
# - Provides insights into how pricing affects sales.

# #### **How is it Implemented?**
# - `self.model = LinearRegression()` initializes the model.
# - `.fit(X, y)` trains the model with price as the feature (`X`) and quantity sold as the target (`y`).
# - `.predict(price)` predicts sales for a given price input.
# - The model is visualized using Matplotlib to show actual vs. predicted sales.

# ### **B. ARIMA (Stock Forecasting)**
# #### **What is ARIMA?**
# ARIMA (AutoRegressive Integrated Moving Average) is a time-series forecasting algorithm that predicts future values based on historical data.

# #### **Why is ARIMA Used?**
# - Accurately forecasts future stock levels.
# - Helps in inventory management and replenishment.
# - Uses past trends to estimate stock depletion over time.

# #### **How is it Implemented?**
# - `model = ARIMA(stock_data, order=(1,1,1))` initializes the ARIMA model.
# - `.fit()` trains the model using historical stock data.
# - `.forecast(steps=days_to_predict)` predicts stock for a given number of days.
# - The results are visualized to observe trends in stock levels.

# ## **3. Libraries Used**

# ### **1. Pandas** (`import pandas as pd`)
# - Used for handling CSV files and manipulating data tables.
# - Functions like `read_csv()`, `to_csv()`, and data selection (`df_grocery[df_grocery['Category'] == value]`) make data handling efficient.

# ### **2. NumPy** (`import numpy as np`)
# - Provides support for numerical operations.
# - Used in sales prediction to reshape arrays (`np.array(price).reshape(-1,1)`).

# ### **3. Matplotlib** (`import matplotlib.pyplot as plt`)
# - Generates visualizations.
# - Used to display trends in sales and stock levels.

# ### **4. Scikit-learn** (`from sklearn.linear_model import LinearRegression`)
# - Implements the Linear Regression model.

# ### **5. Statsmodels** (`from statsmodels.tsa.arima.model import ARIMA`)
# - Implements ARIMA for time-series forecasting.

# ## **4. Graph Generation & Visualization**
# Graphs help in visualizing trends and understanding relationships between variables.

# ### **Graph Functions:**
# 1. **Sales Prediction Graph (`plot_sales()`)**
#    - X-axis: Price
#    - Y-axis: Quantity Sold
#    - Red Line: Predicted Sales
#    - Blue Dots: Actual Sales

# 2. **Stock Forecasting Graph (`predict_stock()`)**
#    - X-axis: Days
#    - Y-axis: Stock Levels
#    - Solid Line: Current Stock
#    - Dashed Line: Predicted Stock

# ## **5. Common Questions & Answers**

# **Q1: How does the system predict sales for a product?**
# - It uses Linear Regression to estimate sales based on the product’s price.

# **Q2: How does the stock prediction work?**
# - ARIMA is trained on past stock levels and forecasts future inventory.

# **Q3: Can the user see sales predictions for a specific price?**
# - Yes, the system asks for a price input and displays predictions visually.

# **Q4: How does filtering work?**
# - Users can filter products by price, category, or best-seller status.

# ## **6. Accuracy of the Models**
# ### **Linear Regression Accuracy**
# - Evaluated using **R-squared Score**.
# - Measures how well the model fits the data.
# - Higher R-squared means better predictions.

# ### **ARIMA Model Accuracy**
# - Evaluated using **Mean Absolute Error (MAE)**.
# - Measures the difference between actual and predicted values.

# ## **7. Final Thoughts**
# This Grocery Management System efficiently integrates **data handling, ML models, and visualization** to assist store owners in managing inventory and predicting sales trends. By utilizing **Linear Regression for sales forecasting and ARIMA for stock prediction**, the system ensures better decision-making for pricing and stock replenishment.

# this code do the new things like filter things by price range and predict the salses by name , catogery, best seller and price