DROP DATABASE IF EXISTS farmer_schema;
Create database farmer_schema;
use farmer_schema;

CREATE TABLE Users (
    id INT PRIMARY KEY,
    username VARCHAR(100),
    role VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE Posts (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    body TEXT,
    user_id INT,
    status VARCHAR(50),
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Follows (
    following_user_id INT,
    followed_user_id INT,
    created_at TIMESTAMP,
    PRIMARY KEY (following_user_id, followed_user_id),
    FOREIGN KEY (following_user_id) REFERENCES Users(id),
    FOREIGN KEY (followed_user_id) REFERENCES Users(id)
);

CREATE TABLE Product (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    Price DECIMAL(10, 2),
    SeasonalAvailability VARCHAR(50)
);

CREATE TABLE Vendor (
    VendorID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(255),
    StallLocation VARCHAR(100)
);

CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY,
    ProductID INT,
    VendorID INT,
    QuantityInStock INT,
    RestockThreshold INT,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (VendorID) REFERENCES Vendor(VendorID)
);

CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(255),
    Preferences TEXT
);

CREATE TABLE Sale (
    SaleID INT PRIMARY KEY,
    VendorID INT,
    ProductID INT,
    CustomerID INT,
    SaleDate DATE,
    QuantitySold INT,
    TotalPrice DECIMAL(10, 2),
    FOREIGN KEY (VendorID) REFERENCES Vendor(VendorID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

CREATE TABLE SeasonalAnalysis (
    SeasonID INT PRIMARY KEY,
    ProductID INT,
    DemandTrend VARCHAR(255),
    SeasonalPeakPeriod VARCHAR(50),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

-- Insert data into Users
INSERT INTO Users (id, username, role, created_at) VALUES
(1, 'jdoe', 'admin', '2023-01-15'),
(2, 'asmith', 'user', '2023-02-20'),
(3, 'mwilson', 'user', '2023-02-25'),
(4, 'ktaylor', 'vendor', '2023-03-05'),
(5, 'lbrown', 'user', '2023-03-15'),
(6, 'pjones', 'admin', '2023-03-20');

-- Insert data into Posts
INSERT INTO Posts (id, title, body, user_id, status, created_at) VALUES
(1, 'First Post', 'This is the body of the first post', 1, 'published', '2023-02-15'),
(2, 'Second Post', 'This is the body of the second post', 2, 'draft', '2023-03-10'),
(3, 'Healthy Eating Tips', 'Top 10 healthy foods to include in your diet', 3, 'published', '2023-03-01'),
(4, 'Seasonal Fruits', 'Why seasonal fruits are better for your health', 4, 'published', '2023-03-10'),
(5, 'Vegetable Gardening', 'Grow your own vegetables this summer!', 5, 'draft', '2023-03-20');

-- Insert data into Follows
INSERT INTO Follows (following_user_id, followed_user_id, created_at) VALUES
(1, 2, '2023-02-16'),
(2, 1, '2023-03-01'),
(3, 2, '2023-03-05'),
(4, 3, '2023-03-10'),
(5, 4, '2023-03-15');

-- Insert data into Product
INSERT INTO Product (ProductID, Name, Category, Price, SeasonalAvailability) VALUES
(1, 'Apples', 'Fruits', 2.99, 'Fall'),
(2, 'Oranges', 'Fruits', 3.49, 'Winter'),
(3, 'Carrots', 'Vegetables', 1.29, 'Spring'),
(4, 'Strawberries', 'Fruits', 4.99, 'Summer'),
(5, 'Pumpkins', 'Vegetables', 3.49, 'Fall'),
(6, 'Tomatoes', 'Vegetables', 2.49, 'Summer');

-- Insert data into Vendor
INSERT INTO Vendor (VendorID, Name, ContactInfo, StallLocation) VALUES
(1, 'Vendor A', '123-456-7890', 'Stall 1'),
(2, 'Vendor B', '987-654-3210', 'Stall 2'),
(3, 'Vendor C', '111-222-3333', 'Stall 3'),
(4, 'Vendor D', '444-555-6666', 'Stall 4'),
(5, 'Vendor E', '777-888-9999', 'Stall 5');

-- Insert data into Inventory
INSERT INTO Inventory (InventoryID, ProductID, VendorID, QuantityInStock, RestockThreshold) VALUES
(1, 1, 1, 100, 10),
(2, 2, 2, 50, 5),
(3, 3, 3, 200, 20),
(4, 4, 4, 150, 15),
(5, 5, 5, 80, 10),
(6, 6, 3, 120, 25);

-- Insert data into Customer
INSERT INTO Customer (CustomerID, Name, ContactInfo, Preferences) VALUES
(1, 'Customer A', 'contactA@example.com', 'Fruits'),
(2, 'Customer B', 'contactB@example.com', 'Vegetables'),
(3, 'Customer C', 'contactC@example.com', 'Fruits and Vegetables'),
(4, 'Customer D', 'contactD@example.com', 'Fruits'),
(5, 'Customer E', 'contactE@example.com', 'Seasonal Produce'),
(6, 'Customer F', 'contactF@example.com', 'Exotic Fruits');

-- Insert data into Sale
INSERT INTO Sale (SaleID, VendorID, ProductID, CustomerID, SaleDate, QuantitySold, TotalPrice) VALUES
(1, 1, 1, 1, '2023-02-17', 3, 8.97),
(2, 2, 2, 2, '2023-03-11', 2, 6.98),
(3, 3, 3, 3, '2023-03-18', 5, 6.45),
(4, 4, 4, 4, '2023-03-20', 3, 14.97),
(5, 5, 5, 5, '2023-03-25', 4, 13.96),
(6, 3, 6, 6, '2023-03-28', 6, 14.94);

-- Insert data into SeasonalAnalysis
INSERT INTO SeasonalAnalysis (SeasonID, ProductID, DemandTrend, SeasonalPeakPeriod) VALUES
(1, 1, 'High Demand', 'Fall'),
(2, 2, 'Moderate Demand', 'Winter'),
(3, 3, 'High Demand', 'Spring'),
(4, 4, 'Very High Demand', 'Summer'),
(5, 5, 'High Demand', 'Fall'),
(6, 6, 'Moderate Demand', 'Summer');
