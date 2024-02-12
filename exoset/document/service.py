from django.conf import settings
from .serializers import ResourceSerializers
from .models import Resource

class Cart:
    def __init__(self, request):
        """
        initialize the cart
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def save(self):
        self.session.modified = True

    def add(self, exercise):
        """
        Add product to the cart or update its quantity
        """
        if not self.cart.values():
            order = 1
        else:
            order = self.cart.__len__() + 1
        if exercise not in self.cart:
            self.cart[exercise] = {'order': order}
        self.save()

    def remove(self, exercise):
        """
        Remove a product from the cart
        """
        exercise_id = str(exercise)
        i = self.cart[exercise_id]['order']
        if exercise_id in self.cart:
            order_to_remove = self.cart[exercise_id]['order']
            del self.cart[exercise_id]

            self.save()
        for key, value in self.cart.items():
            if value['order'] > order_to_remove:
                value['order'] -= 1
                self.save()

    def __iter__(self):
        """
        Loop through cart items and fetch the products from the database
        """
        exercises_ids = self.cart.keys()
        exercises = Resource.objects.filter(id__in=exercises_ids)
        cart = self.cart.copy()
        for exercise in exercises:
            cart[str(exercise.id)]["exercise"] = ResourceSerializers(exercise).data
        for item in cart.values():
            item["order"] = int(item["order"])
            yield item

    def __len__(self):
        """
        Count all items in the cart
        """
        if self.cart.values():
            return max(self.cart.values())
        else:
            return 0

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def number_of_exercises(self):
        return len(self.cart)

    def reorder_exercises(self, desired_order):
        self.session['cart'] = {k: self.cart[k] for k in desired_order}
        #self.session = self.cart
        self.save()

