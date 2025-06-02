from django.urls import resolve

def dynamic_banner(request):
    route_name = resolve(request.path_info).url_name

    titles = {
        'home': ("Welcome to Airbnb Manager", "Track your bookings, manage expenses, and grow your Airbnb business"),
        'booking_list': ("All Bookings", "View and manage all your reservations"),
        'generate_invoices': ("Invoices", "Generate and download invoices for bookings"),
        'manage_houses': ("Manage Houses", "Add, update, or remove your properties"),
        'discounts_page': ("Discounts", "Apply and track discounts for your listings"),
        'financial_overview': ("Financial Overview", "Track income, expenses, and taxes"),
        'expense_overview': ("Expense Overview", "See where your money goes"),
        'house_compare': ("House Analytics", "Compare house performance across the board"),
        'utility_expenses': ("Utility Expenses", "Track monthly electricity and water costs"),
        'houses_list': ("Make a Booking", "Create a new reservation for your property"),  # asta e URL-ul pentru /houses/
    }

    title, subtitle = titles.get(route_name, ("Welcome to Airbnb Manager", ""))

    return {
        'banner_title': title,
        'banner_subtitle': subtitle,
    }
