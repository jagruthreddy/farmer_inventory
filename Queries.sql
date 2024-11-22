use farmer_schema;
drop table followers;
drop table product;
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
    ProductID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    Price DECIMAL(10, 2),
    SeasonalAvailability VARCHAR(50)
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

CREATE TABLE Vendor (
    VendorID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(255),
    StallLocation VARCHAR(100)
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

INSERT INTO Users (id, username, role, created_at) VALUES
(1, 'jdoe', 'admin', '2023-01-15'),
(2, 'asmith', 'user', '2023-02-20');

INSERT INTO Posts (id, title, body, user_id, status, created_at) VALUES
(1, 'First Post', 'This is the body of the first post', 1, 'published', '2023-02-15'),
(2, 'Second Post', 'This is the body of the second post', 2, 'draft', '2023-03-10');

INSERT INTO Follows (following_user_id, followed_user_id, created_at) VALUES
(1, 2, '2023-02-16');

INSERT INTO Product (ProductID, Name, Category, Price, SeasonalAvailability) VALUES
(1, 'Apples', 'Fruits', 2.99, 'Fall'),
(2, 'Oranges', 'Fruits', 3.49, 'Winter');

INSERT INTO Vendor (VendorID, Name, ContactInfo, StallLocation) VALUES
(1, 'Vendor A', '123-456-7890', 'Stall 1'),
(2, 'Vendor B', '987-654-3210', 'Stall 2');

INSERT INTO Inventory (InventoryID, ProductID, VendorID, QuantityInStock, RestockThreshold) VALUES
(1, 1, 1, 100, 10),
(2, 2, 2, 50, 5);

INSERT INTO Customer (CustomerID, Name, ContactInfo, Preferences) VALUES
(1, 'Customer A', 'contactA@example.com', 'Fruits'),
(2, 'Customer B', 'contactB@example.com', 'Vegetables');

INSERT INTO Sale (SaleID, VendorID, ProductID, CustomerID, SaleDate, QuantitySold, TotalPrice) VALUES
(1, 1, 1, 1, '2023-02-17', 3, 8.97),
(2, 2, 2, 2, '2023-03-11', 2, 6.98);

INSERT INTO SeasonalAnalysis (SeasonID, ProductID, DemandTrend, SeasonalPeakPeriod) VALUES
(1, 1, 'High Demand', 'Fall'),
(2, 2, 'Moderate Demand', 'Winter');

