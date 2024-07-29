# carter quesenberry cs 3270 online groceries database

from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

# dataclass for customer information:
@dataclass
class Customer:
    cust_id: int
    name: str
    street: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str

    # read the customer information from file:
    @classmethod
    def read_customers(cls, file_path):
        customers = {}
        with open(file_path, 'r') as file:
            for line in file:
                data = line.strip().split(',')
                cust_id, name, street, city, state, zip_code, phone, email = data
                customer = Customer(int(cust_id), name, street, city, state, zip_code, phone, email)
                customers[int(cust_id)] = customer
        # return customer info:
        return customers

# dataclass for item information:
@dataclass
class Item:
    item_id: int
    description: str
    price: float

    @classmethod
    def read_items(cls, file_path):
        items = {}
        with open(file_path, 'r') as file:
            for line in file:
                data = line.strip().split(',')
                item_id, description, price = data
                item = Item(int(item_id), description, float(price))
                items[int(item_id)] = item
        return items

# dataclass for line items in an order:
@dataclass
class LineItem:
    item_id: int
    qty: int

    #calculate the subtotal for the line based on them item price and quantity:
    def sub_total(self, items):
        return self.qty * items[self.item_id].price

# base class for payments methods:
class Payment(ABC):
    amount: float

    #print payment details:
    @abstractmethod
    def print_detail(self):
        pass

# payment methods:
class CreditCardPayment(Payment):
    def __init__(self, card_number: str, expiration: str):
        self.card_number = card_number
        self.expiration = expiration

    def print_detail(self):
        return f"Credit card {self.card_number}, exp. {self.expiration}"


class PayPalPayment(Payment):
    def __init__(self, paypal_id: str):
        self.paypal_id = paypal_id

    def print_detail(self):
        return f"PayPal ID: {self.paypal_id}"


class WireTransferPayment(Payment):
    def __init__(self, bank_id: str, account_id: str):
        self.bank_id = bank_id
        self.account_id = account_id

    def print_detail(self):
        return f"Wire transfer from Bank ID {self.bank_id}, Account# {self.account_id}"

# dataclass for orders
@dataclass
class Order:
    order_id: int
    order_date: datetime
    cust_id: int
    line_items: List[LineItem]
    payment: Payment

    # calculates the total amount for the order:
    @property
    def total(self):
        return sum(line_item.sub_total(items) for line_item in self.line_items)

    #format the order details:
    def print_order(self, customers, items):
        customer = customers[self.cust_id]
        order_str = "=" * 27 + "\n"
        order_str += f"Order #{self.order_id}, Date: {self.order_date}\n"
        order_str += f"Amount: ${self.total:.2f}, Paid by {self.payment.print_detail()}\n"
        order_str += f"\nCustomer ID #{self.cust_id}:\n"
        order_str += f"{customer.name}, ph. {customer.phone}, email: {customer.email}\n"
        order_str += customer.street + "\n"
        order_str += f"{customer.city}, {customer.state} {customer.zip_code}\n"
        order_str += "\nOrder Detail:\n"
        sorted_line_items = sorted(self.line_items, key=lambda x: x.item_id)
        for line_item in sorted_line_items:
            item = items[line_item.item_id]
            order_str += f"\tItem {item.item_id}: \"{item.description}\", {line_item.qty} @ {item.price:.2f}\n"
        return order_str

    #read order information from a file and return a list of order info:
    @classmethod
    def read_orders(cls, file_path, customers, items):
        orders = []

        with open(file_path, 'r') as file:
            lines = file.readlines()
            i = 0

            while i < len(lines):
                # the order details:
                order_data = lines[i].strip().split(',')
                cust_id, order_number, order_date_str, *item_quantities = order_data
                order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
                line_items = [LineItem(int(item.split('-')[0]), int(item.split('-')[1])) for item in item_quantities]

                # the payment information:
                payment_data = lines[i + 1].strip().split(',')
                payment_code = int(payment_data[0])
                if payment_code == 1:
                    payment_info = CreditCardPayment(payment_data[1], payment_data[2])
                elif payment_code == 2:
                    payment_info = PayPalPayment(payment_data[1])
                elif payment_code == 3:
                    payment_info = WireTransferPayment(payment_data[1], payment_data[2])

                # create an order object and add it to the orders list:
                order = Order(int(order_number), order_date, int(cust_id), line_items, payment_info)
                orders.append(order)

                # skip 2 lines:
                i += 2

        return orders


if __name__ == '__main__':
    customers = Customer.read_customers("customers.txt")
    items = Item.read_items("items.txt")

    orders = Order.read_orders("orders.txt", customers, items)

    # Print orders to the file order_report.txt
    with open("order_report.txt", "w") as report_file:
        for order in orders:
            report_file.write(order.print_order(customers, items))
            report_file.write("\n")
