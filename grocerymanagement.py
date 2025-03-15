import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import NearestNeighbors
from statsmodels.tsa.arima.model import ARIMA


# ---------------------- Step 1: Generate & Load Grocery Data ----------------------
# data = {
#     "Product Name": [f"Product_{i}" for i in range(1, 21)],
#     "Category": random.choices(["Dairy", "Beverage", "Snack", "Household"], k=20),
#     "Price": np.random.randint(50, 500, 20),
#     "Stock": np.random.randint(10, 100, 20),
#     "Best Seller": [random.choice([True, False]) for _ in range(20)],
#     "Quantity Sold": np.random.randint(5, 150, 20),
# }


# df_grocery = pd.DataFrame(data)
# csv_filename = "grocery_data.csv"
# df_grocery.to_csv(grocery_data.csv, index=False)
# df_grocery = pd.read_csv(grocery_data.csv)

csv_filename = "grocery_data_updated.csv"  # Ensure this matches your downloaded file name
df_grocery = pd.read_csv(csv_filename)


# ---------------------- Step 2: Product Search & Purchase ----------------------
def search_and_buy_product(product_name, quantity):
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

# ---------------------- Step 3: Filtering Options ----------------------
def filter_products(filter_type, value):
    if filter_type == "price":
        return df_grocery[df_grocery["Price"] <= value]
    elif filter_type == "best_seller":
        return df_grocery[df_grocery["Best Seller"] == True]
    elif filter_type == "category":
        return df_grocery[df_grocery["Category"] == value]
    else:
        return "❌ Invalid filter option."

# ---------------------- Step 4: Sales Prediction (Linear Regression) ----------------------
class SalesPredictionModel:
    def __init__(self, data):
        self.df = data
        self.model = LinearRegression()

    def train(self):
        X = self.df[['Price']]
        y = self.df['Quantity Sold']
        self.model.fit(X, y)

    def predict(self, price):
        return self.model.predict([[price]])[0]

    def plot_sales(self):
        plt.scatter(self.df['Price'], self.df['Quantity Sold'], color='blue', label='Actual Sales')
        plt.plot(self.df['Price'], self.model.predict(self.df[['Price']]), color='red', label='Predicted Sales')
        plt.xlabel('Price')
        plt.ylabel('Quantity Sold')
        plt.title('Sales Prediction Model')
        plt.legend()
        plt.show()

sales_model = SalesPredictionModel(df_grocery)
sales_model.train()

# ---------------------- Step 5: Inventory Management (ARIMA) ----------------------
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

# ---------------------- Step 6: Price Optimization (Q-Learning) ----------------------
class PricingEnvironment:
    def __init__(self):
        self.state_space = [0, 1, 2]  # 0 - Low Price, 1 - Medium Price, 2 - High Price
        self.action_space = [0, 1, 2]
        self.q_table = np.zeros((len(self.state_space), len(self.action_space)))
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 1.0

    def step(self, state, action):
        reward = random.uniform(5, 15) if action == 1 else random.uniform(2, 12)
        next_state = random.choice(self.state_space)
        return next_state, reward

    def train(self, episodes=1000):
        for _ in range(episodes):
            state = random.choice(self.state_space)
            action = np.argmax(self.q_table[state]) if random.random() > self.exploration_rate else random.choice(self.action_space)
            next_state, reward = self.step(state, action)
            self.q_table[state, action] += self.learning_rate * (reward + self.discount_factor * np.max(self.q_table[next_state]) - self.q_table[state, action])
            self.exploration_rate *= 0.99  

pricing_env = PricingEnvironment()
pricing_env.train()

# ---------------------- Step 7: Customer Purchase Prediction (Logistic Regression) ----------------------
customer_data = {
    'Age': np.random.randint(18, 65, 100),
    'Income': np.random.randint(20000, 80000, 100),
    'Previous Purchases': np.random.randint(1, 10, 100),
    'Purchased': np.random.choice([0, 1], 100)
}

df_customer = pd.DataFrame(customer_data)

def train_purchase_model():
    X = df_customer[['Age', 'Income', 'Previous Purchases']]
    y = df_customer['Purchased']
    model = LogisticRegression()
    model.fit(X, y)
    return model

purchase_model = train_purchase_model()

# ---------------------- Step 8: Product Recommendation (Collaborative Filtering) ----------------------
interaction_data = np.random.randint(0, 2, (10, 5))

def recommend_product(data):
    model = NearestNeighbors(n_neighbors=2)
    model.fit(data)
    return model

recommendation_model = recommend_product(interaction_data)

# ---------------------- Step 9: User Interaction ----------------------
while True:
    print("\n📌 Grocery Management System")
    print("1. Search & Buy Product")
    print("2. Filter Products")
    print("3. Predict Sales")
    print("4. Predict Stock Levels")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        product_name = input("Enter product name: ")
        quantity = int(input("Enter quantity to buy: "))
        print(search_and_buy_product(product_name, quantity))

    elif choice == "2":
        filter_type = input("Filter by (price/category/best_seller): ").strip().lower()
        if filter_type == "price":
            value = int(input("Enter max price: "))
        elif filter_type == "category":
            value = input("Enter category: ")
        else:
            value = None
        print(filter_products(filter_type, value))

    elif choice == "3":
        price = int(input("Enter product price for sales prediction: "))
        print(f"Predicted sales for ₹{price}: {sales_model.predict(price):.2f} units")
        sales_model.plot_sales()

    elif choice == "4":
        days = int(input("Enter number of days for stock forecasting: "))
        print(f"Predicted stock levels: {predict_stock(df_grocery['Stock'], days)}")

    elif choice == "5":
        print("Exiting program...")
        break

    else:
        print("Invalid choice. Please try again.")
