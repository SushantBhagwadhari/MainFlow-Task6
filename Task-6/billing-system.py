import os
from fpdf import FPDF
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from datetime import datetime
from kivy.graphics import Color, Rectangle

# Sample data structure for items in the store with units
store_items = {
    "Flours": {
        "Wheat Flour": {"price": 40, "quantity": 100, "unit": "per kg"},
        "Rice Flour": {"price": 35, "quantity": 50, "unit": "per kg"},
    },
    "Pulses": {
        "Chickpeas": {"price": 60, "quantity": 80, "unit": "per kg"},
        "Lentils": {"price": 70, "quantity": 40, "unit": "per kg"}
    },
    "Spices": {
        "Turmeric": {"price": 100, "quantity": 20, "unit": "per kg"},
        "Cumin": {"price": 90, "quantity": 30, "unit": "per kg"}
    },
    "Misc": {
        "Eggs": {"price": 5, "quantity": 200, "unit": "per item"},
        "Milk": {"price": 50, "quantity": 150, "unit": "per liter"}
    }
}

# Custom PDF class for A6 size
class MyFPDF(FPDF):
    def __init__(self):
        # Initialize with A6 paper size
        super().__init__(format='A6')
        self.set_auto_page_break(auto=True, margin=10)
        self.add_page()

    def header(self):
        # Title for the Invoice at the top of each page
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Departmental Store Invoice', ln=True, align='C')

    def footer(self):
        # Position at 1.5 cm from the bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

# Main Kivy App
class GroceryStoreApp(App):
    def build(self):
        # Main layout with cream white background
        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.set_background(root_layout)

        # Store name at the top, constrained with size_hint_y
        store_name_layout = AnchorLayout(anchor_x='center', anchor_y='top', size_hint_y=None, height=50)
        store_name_label = Label(text="[b]Departmental Store[/b]", markup=True, font_size=24, color=(0, 0, 0, 1))
        store_name_layout.add_widget(store_name_label)
        root_layout.add_widget(store_name_layout)

        # Main content layout (for items and invoice)
        content_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)

        # Left layout for items
        item_layout = GridLayout(cols=1, size_hint=(0.7, 1), spacing=10)
        self.cart = {}  # Cart to hold selected items

        # ScrollView for item layout to handle long lists
        item_scrollview = ScrollView(size_hint=(0.7, 1))
        item_scrollview.add_widget(item_layout)

        for category, items in store_items.items():
            # Category box with a label at the top
            category_box = BoxLayout(orientation='vertical', padding=5, spacing=5, size_hint_y=None)
            category_box.add_widget(Label(text=f"[b]{category}[/b]", markup=True, font_size=18, color=(0, 0, 0, 1)))

            for item, info in items.items():
                # Display item, price, and unit
                item_label = Label(text=f"{item} - Rs.{info['price']} {info['unit']}", color=(0, 0, 0, 1))
                qty_input = TextInput(text="0", multiline=False, size_hint=(0.3, None), height=30)

                # Add and Remove buttons
                add_button = Button(text="Add", size_hint=(None, None), width=80, height=30)
                remove_button = Button(text="Remove", size_hint=(None, None), width=80, height=30)

                add_button.bind(on_press=lambda btn, i=item, q=qty_input: self.add_to_cart(i, q))
                remove_button.bind(on_press=lambda btn, i=item, q=qty_input: self.remove_from_cart(i, q))

                # Add item and buttons to layout
                item_box = BoxLayout(orientation='horizontal', spacing=5)
                item_box.add_widget(item_label)
                item_box.add_widget(qty_input)
                item_box.add_widget(add_button)
                item_box.add_widget(remove_button)
                category_box.add_widget(item_box)

            # Add category box to item layout
            item_layout.add_widget(category_box)

        content_layout.add_widget(item_scrollview)

        # Right layout for invoice and total
        invoice_layout = GridLayout(cols=1, size_hint=(0.3, 1), padding=10, spacing=10)

        # Invoice title
        invoice_layout.add_widget(Label(text="Invoice", font_size=16, color=(0, 0, 0, 1)))

        # Scrollable TextInput for invoice display, larger window size
        self.invoice_display = TextInput(text="", readonly=True, size_hint_y=0.8, font_size=14)
        invoice_layout.add_widget(self.invoice_display)

        # Total label (highlighted)
        self.total_label = Label(text="[b]Total: Rs.0[/b]", markup=True, font_size=16, color=(0.8, 0, 0, 1))
        invoice_layout.add_widget(self.total_label)

        # Print button
        print_button = Button(text="Print Invoice", size_hint=(None, None), width=150, height=40)
        print_button.bind(on_press=self.print_invoice)
        invoice_layout.add_widget(print_button)

        content_layout.add_widget(invoice_layout)
        root_layout.add_widget(content_layout)

        return root_layout

    # Set background color for layout
    def set_background(self, layout):
        with layout.canvas.before:
            Color(0.96, 0.96, 0.86, 1)  # Cream white background
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self.update_rect, pos=self.update_rect)

    # Update rectangle size for background when window resizes
    def update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    # Add an item to the cart
    def add_to_cart(self, item_name, qty_input):
        try:
            qty = float(qty_input.text)  # Allow float for kg/liters
            if item_name in self.cart:
                self.cart[item_name] += qty
            else:
                self.cart[item_name] = qty

            self.update_invoice()
        except ValueError:
            pass

    # Remove an item from the cart
    def remove_from_cart(self, item_name, qty_input):
        try:
            qty = float(qty_input.text)
            if item_name in self.cart and self.cart[item_name] > 0:
                self.cart[item_name] -= qty
                if self.cart[item_name] <= 0:
                    del self.cart[item_name]

            self.update_invoice()
        except ValueError:
            pass

    # Update the invoice in real-time
    def update_invoice(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        invoice_text = f"[b]---- Departmental Store Invoice ----[/b]\nGenerated on: {current_time}\n\n"
        total = 0
        for item, qty in self.cart.items():
            price = None
            unit = None
            for category, items in store_items.items():
                if item in items:
                    price = items[item]['price']
                    unit = items[item]['unit']
                    break
            item_total = qty * price
            total += item_total
            invoice_text += f"{item}: {qty} {unit} x Rs.{price} = Rs.{item_total}\n"

        invoice_text += f"\n[b]Grand Total: Rs.{total}[/b]"
        self.invoice_display.text = invoice_text
        self.total_label.text = f"[b]Total: Rs.{total}[/b]"

    # Print invoice and generate A6 PDF
    def print_invoice(self, instance):
        # Create an instance of the custom PDF class
        pdf = MyFPDF()

        # Set font for the body
        pdf.set_font("Arial", size=10)

        # Add date and time to the invoice
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, f'Generated on: {current_time}', ln=True, align='C')

        # Add an empty line
        pdf.ln(5)

        # Invoice body (cart details)
        for item, qty in self.cart.items():
            # Find the item details (price and unit)
            price = None
            unit = None
            for category, items in store_items.items():
                if item in items:
                    price = items[item]['price']
                    unit = items[item]['unit']
                    break

            # Calculate item total
            item_total = qty * price
            # Add the item details to the invoice
            pdf.cell(0, 10, f"{item}: {qty} {unit} x Rs.{price} = Rs.{item_total}", ln=True)

        # Grand total at the bottom
        total = sum(self.cart[item] * store_items[cat][item]['price'] 
                    for cat in store_items for item in self.cart if item in store_items[cat])
        pdf.ln(5)
        pdf.cell(0, 10, f"Grand Total: Rs.{total}", ln=True, align='R')

        # Save the PDF
        filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)

        # Open the PDF file to print (Windows)
        os.startfile(filename)

# Run the app
if __name__ == '__main__':
    GroceryStoreApp().run()
