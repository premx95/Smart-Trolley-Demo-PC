import cv2 # OpenCV for camera access
from pyzbar.pyzbar import decode # pyzbar for barcode decoding
import sqlite3 # SQLite for database access
import tkinter as tk # Tkinter for GUI
from tkinter import ttk, messagebox, simpledialog, StringVar, OptionMenu # Additional Tkinter components
import threading  # Threading for running camera in a separate thread

'''# Hardcoded products (name, barcode, price)
PRODUCTS = {
    "8961014255188": {"name": "Lux Soap", "price": 25},
    "L-EK-0600017": {"name": "Shoes", "price": 1000},  # New shoe product
    "9876543210987": {"name": "Olay Soap", "price": 35}
}
'''
# GUI Class
class SmartTrolleyApp:
    def __init__(self, root):
        # Connect to the database
        self.conn = sqlite3.connect("products.db")
        self.cursor = self.conn.cursor()

        #gui starts here
        self.root = root
        self.root.title("Smart Trolley System")
        self.root.geometry("600x400")
        
        # Billing data
        self.billing_data = {}
        
        # Table for displaying scanned items
        self.tree = ttk.Treeview(root, columns=('Product', 'Price', 'Quantity', 'Total'), show='headings')
        self.tree.heading('Product', text='Product')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Total', text='Total')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Total bill display
        self.total_label = tk.Label(root, text="Total: 0", font=("Arial", 16))
        self.total_label.pack()
        
        # Start/Stop scanning buttons
        self.start_btn = tk.Button(root, text="Start Scanning", command=self.start_scanning)
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.stop_btn = tk.Button(root, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Scan Another Item button
        self.scan_another_btn = tk.Button(root, text="Scan Another Item", command=self.scan_another_item, state=tk.DISABLED)
        self.scan_another_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Payment Method button
        self.payment_btn = tk.Button(root, text="Proceed to Payment", command=self.ask_payment_method, state=tk.DISABLED)
        self.payment_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Delete Product button
        self.delete_btn = tk.Button(root, text="Delete Product", command=self.delete_product, state=tk.NORMAL)
        self.delete_btn.pack(side=tk.LEFT, padx=10, pady=10)
                
        # Camera thread
        self.scanning = False
        self.thread = None
        self.last_scanned_barcode = None  # Store the last scanned barcode

    def update_billing(self, barcode):
        print(f"Scanned Barcode: '{barcode}'")

        # Query database 
        self.cursor.execute(
            "SELECT name, price FROM products WHERE barcode=?",
            (barcode,)
        )
        result = self.cursor.fetchone()

        if result:
            name, price = result

            # IMPORTANT: UI operations must stay on main thread
            self.root.after(0, self.ask_for_quantity, name, barcode, price)
        else:
            # Handle unknown product (also on main thread)
            self.root.after(0, self.product_not_found, barcode)

    def ask_for_quantity(self, name, barcode, price):
        # Prompt the user to enter quantity for the scanned product
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {name}:", minvalue=1)
        if quantity:
            # Add the new product as a new entry in the list
            if barcode in self.billing_data:
                # If the product already exists, ask for previous and current quantity
                old_quantity = self.billing_data[barcode]['quantity']
                total_quantity = old_quantity + quantity
                messagebox.showinfo("Product Added", f"Previous Quantity: {old_quantity}\nAdded {quantity} more of {name}.\nTotal quantity: {total_quantity}")
                self.billing_data[barcode]['quantity'] = total_quantity
            else:
                messagebox.showinfo("Product Added", f"Added {quantity} of {name}.")
                self.billing_data[barcode] = {'name': name, 'price': price, 'quantity': quantity}
            
            # Refresh the table with updated data and recalculate the total
            self.refresh_table()
            self.scan_another_btn.config(state=tk.NORMAL)  
            self.payment_btn.config(state=tk.NORMAL)  
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid quantity.")
    
    def product_not_found(self, barcode):
        # Show an error message if the product is not found in the database
        messagebox.showerror(
            "Product Not Found",
            f"Barcode '{barcode}' is not registered.\nPlease contact customer support."
        )

    def refresh_table(self):
        # Clear the table
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Add updated billing data
        total_bill = 0
        for item in self.billing_data.values():
            total = item['price'] * item['quantity']
            self.tree.insert('', tk.END, values=(item['name'], item['price'], item['quantity'], total))
            total_bill += total
        
        # Update total
        self.total_label.config(text=f"Your Total Bill is : {total_bill}")

    def start_scanning(self):
        self.scanning = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.scan_another_btn.config(state=tk.DISABLED)  
        self.payment_btn.config(state=tk.DISABLED)  
        self.thread = threading.Thread(target=self.scan_barcode)
        self.thread.start()

    def stop_scanning(self):
        self.scanning = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.scan_another_btn.config(state=tk.DISABLED)  
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def scan_another_item(self):
        # Reset barcode scanning and allow scanning another item
        self.last_scanned_barcode = None
        self.scan_another_btn.config(state=tk.DISABLED)  
        self.start_scanning()  

    # Function to delete a product from the billing    
    def delete_product(self):
        # Get selected item in the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Product", "Please select a product to delete.")
            return

        # Get product name from the selected row
        item_values = self.tree.item(selected_item, 'values')
        product_name = item_values[0]  # Assuming first column is product name
        barcode_to_delete = None

        # Find the barcode in billing_data
        for barcode, info in self.billing_data.items():
            if info['name'] == product_name:
                barcode_to_delete = barcode
                break

        if barcode_to_delete:
            # Ask user for confirmation
            confirm = messagebox.askyesno("Confirm Delete", f"Delete {product_name} from billing?")
            if confirm:
                # Remove from billing (temporary)
                del self.billing_data[barcode_to_delete]
                self.refresh_table()
                messagebox.showinfo("Deleted", f"{product_name} removed from the bill.")

    def ask_payment_method(self):
        # Ask the user for payment method selection
        payment_methods = ["Easypaisa", "JazzCash", "DebitCard"]

        # Function to process payment method and collect additional info
        def on_method_select(event):
            selected_method = payment_method_var.get()
            if selected_method == "Easypaisa" or selected_method == "JazzCash":
                self.ask_phone_number(selected_method)
            elif selected_method == "DebitCard":
                self.ask_debitcard_info()

        # Create dropdown for payment methods
        payment_method_var = StringVar(self.root)
        payment_method_var.set(payment_methods[0])  # Default value

        # Create dropdown menu
        payment_method_menu = OptionMenu(self.root, payment_method_var, *payment_methods)
        payment_method_menu.pack(padx=10, pady=10)

        # Bind dropdown selection to method
        payment_method_menu.bind("<Configure>", on_method_select)

    def ask_phone_number(self, payment_method):
        phone_number = simpledialog.askstring("Phone Number", f"Enter your {payment_method} number:")
        if phone_number:
            messagebox.showinfo("Payment Information", f"Payment Method: {payment_method}\nPhone Number: {phone_number}")
            self.payment_btn.config(state=tk.DISABLED)  
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid phone number.")

    def ask_debitcard_info(self):
        card_choice = simpledialog.askstring("Debit Card", "Enter your Debit Card Account Number or scan your card?")
        if card_choice:
            messagebox.showinfo("Payment Information", f"Payment Method: DebitCard\nAccount Number: {card_choice}")
            self.payment_btn.config(state=tk.DISABLED)  # Disable the payment button after selection
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid account number or scan your card.")

    def scan_barcode(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend for camera

        if not cap.isOpened():
            #add pop up message box for error
            messagebox.showerror("Camera Error", "Error: Could not open camera.")
            return

        while self.scanning:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                break
            
            # Convert the frame to grayscale for better detection
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect barcodes
            barcodes = decode(gray_frame)
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    print(f"Decoded {barcode_type} barcode: {barcode_data}")  # Debugging print
                    if barcode_data != self.last_scanned_barcode:
                        self.last_scanned_barcode = barcode_data
                        self.update_billing(barcode_data)
            
            cv2.imshow("Scanning...", frame)

            # Stop if the user presses 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    
    # connection close function to close the database connection when the application is closed
    def on_closing(self):
        self.conn.close()
        self.root.destroy()
        
# Run the application
root = tk.Tk()
app = SmartTrolleyApp(root)

# Handle window close event to ensure database connection is closed
root.protocol("WM_DELETE_WINDOW", app.on_closing)

root.mainloop()
